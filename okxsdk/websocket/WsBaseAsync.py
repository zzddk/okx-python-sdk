"""Shared WebSocket session: routing, authentication and the public entries.

`WsPublicAsync` and `WsPrivateAsync` differ only in their constructors and the
private trading helpers. This module owns what the protocol *means*: which
callback receives a message, whether this connection needs a login, what a
subscribe frame carries. The socket and the tasks that keep it alive — the read
loop, the heartbeat, reconnect backoff and stop — live in
`okxsdk.websocket.connection.ConnectionSupervisor`.

Routing and callbacks
----------------------
A message is delivered to the callback registered for its `arg`; an
acknowledgement without `arg` (such as an order response) is matched by its
`id`. Only a message that matches neither reaches `callback`, which is a
deprecated fallback kept until 1.0. The table itself lives in
`okxsdk.websocket.subscriptions`.

A callback may be a plain function or an `async def`. A coroutine is awaited,
so it never blocks the event loop; a plain function is called inline (kept for
callers written against 0.8 and earlier). Either way an exception raised by the
callback is logged and the next message is still delivered — a broken callback
cannot end the stream.

Login
-----
`start()` runs the login when this session needs one, so the first
connection and a reconnect follow the same path: the reader is already
running, and the handshake only has to wait for the acknowledgement it feeds.

Protocol frames
---------------
The server answers a text `ping` with `pong`. Pong frames are consumed by the
supervisor's heartbeat and are not handed here. A missing pong makes the
connection count as dead, which triggers a reconnect.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
from typing import Any, ClassVar, Dict, List, Optional

from okxsdk.websocket.connection import (
    DEFAULT_PING_INTERVAL,
    DEFAULT_PING_TIMEOUT,
    DEFAULT_RECONNECT_BACKOFF,
    DEFAULT_RECONNECT_MAX_BACKOFF,
    ConnectionSupervisor,
    Message,
)
from okxsdk.websocket.connector import WebSocketConnector
from okxsdk.websocket.login import DEFAULT_LOGIN_TIMEOUT, LoginHandshake, login_payload
from okxsdk.websocket.subscriptions import Callback, Subscriptions, key

logger = logging.getLogger(__name__)


class WsBaseAsync:
    """One OKX WebSocket session: sending, subscribing, login and routing.

    Subclasses supply a default host and, for the private client, the
    order-entry helpers. `_LOGIN_REQUIRED` selects whether subscribing
    authenticates first, which is what `WsPrivateAsync` always did.

    The socket is opened by `connector`; when it is omitted a
    `WebSocketConnector` is built with `proxy`. Supplying both keeps the
    connector and ignores `proxy`, the same rule as
    `Transport(proxy=, http=)`.
    """

    _LOGIN_REQUIRED = False
    # "is demo trading" -> endpoint, declared by each client. Without a
    # transport there is no demo switch, so the live entry is the default url.
    _HOSTS: ClassVar[Dict[bool, str]] = {}

    def __init__(
        self,
        url: Optional[str] = None,
        apiKey: str = '',
        passphrase: str = '',
        secretKey: str = '',
        debug: bool = False,
        ping_interval: Optional[float] = DEFAULT_PING_INTERVAL,
        ping_timeout: float = DEFAULT_PING_TIMEOUT,
        reconnect: bool = True,
        reconnect_backoff: float = DEFAULT_RECONNECT_BACKOFF,
        reconnect_max_backoff: float = DEFAULT_RECONNECT_MAX_BACKOFF,
        proxy: Optional[str] = None,
        connector: Optional[WebSocketConnector] = None,
    ) -> None:
        self.url = url if url is not None else self._HOSTS.get(False)
        self.apiKey = apiKey
        self.passphrase = passphrase
        self.secretKey = secretKey
        self.debug = debug

        # Deprecated fallback: messages that match no subscription or request
        # are delivered here. Assigning still works; new code should pass the
        # callback to subscribe() instead. Removed before 1.0.
        self.callback: Optional[Callback] = None
        self._subs = Subscriptions()

        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._connector = connector if connector is not None else WebSocketConnector(proxy=proxy)
        self._is_logged_in = False
        self._ever_logged_in = False
        self._handshake: Optional[LoginHandshake] = None
        # Serializes login attempts; created in the running loop on first use.
        self._login_lock: Optional[asyncio.Lock] = None

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.reconnect = reconnect
        self.reconnect_backoff = reconnect_backoff
        self.reconnect_max_backoff = reconnect_max_backoff

        self._connection = ConnectionSupervisor(
            connector=self._connector,
            url=self.url,
            on_frame=self._on_frame,
            on_ready=self._on_ready,
            on_lost=self._on_lost,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            reconnect=reconnect,
            reconnect_backoff=reconnect_backoff,
            reconnect_max_backoff=reconnect_max_backoff,
            debug=debug,
        )

    # ------------------------------------------------------------------ views

    @property
    def isLoggedIn(self) -> bool:
        """Whether the current connection has authenticated. Read-only.

        The session writes it in `login()`, `stop()` and on reconnect;
        callers only read it.
        """
        return self._is_logged_in

    @property
    def websocket(self) -> Any:
        """The connection the supervisor currently holds, or None. Read-only."""
        return self._connection.socket

    @property
    def subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Deprecated read-only view of the subscribed args, keyed like replay.

        Derived from `_subs` on every read, so there is no second copy of the
        state. Assigning raises `AttributeError`; subscribe() and
        unsubscribe() are the supported way to change it. Removed before 1.0.
        """
        return {key(arg): arg for arg in self._subs.replay()}

    # ------------------------------------------------------------------ start/stop

    async def start(self) -> asyncio.Task:
        """Connect and start the supervisor, heartbeat and reconnect loop.

        The first connection also runs the session restore: a session that
        needs to log in does so before `start()` returns. The returned task is
        the supervisor. It stays alive across reconnects and finishes only when
        `stop()` is called (or when `reconnect=False` and the connection ends).
        """
        self.loop = asyncio.get_running_loop()
        return await self._connection.start()

    async def stop(self) -> None:
        """Stop the supervisor, the heartbeat and the socket. Idempotent.

        A callback may call this from inside a dispatch; the supervisor then
        returns without cancelling the frame it is running.
        """
        await self._connection.stop()
        self._subs.drop_requests()
        self._is_logged_in = False
        self._login_lock = None

    def stop_sync(self) -> None:
        if self.loop is None:
            raise RuntimeError("stop_sync() requires a prior start(); no event loop has been captured")
        if self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.stop(), self.loop)
            future.result(timeout=10)
        else:
            self.loop.run_until_complete(self.stop())

    # ------------------------------------------------------------------ frames

    async def _on_frame(self, message: Message) -> None:
        """Take one frame from the supervisor (pong is already filtered out)."""
        if self.debug:
            logger.debug("Received message: {%s}", message)
        payload = self._parse(message)
        if LoginHandshake.is_ack(payload):
            # A login answer is never delivered: it belongs to the handshake.
            handshake = self._handshake
            if handshake is not None:
                handshake.feed(payload)
            return
        await self._deliver(message, payload)

    def _on_lost(self, exc: BaseException) -> None:
        """The reader ended on its own: fail the login handshake if one is open.

        Nothing goes to the callback stream here. A drop is reported by the
        task `start()` returned (and, with reconnect on, by the session being
        restored once the socket is back) — the same reason `pong` stays out of
        callbacks: it is connection state, not a message from the server.
        """
        if self._handshake is not None:
            self._handshake.abort(ConnectionError(f"connection lost during login: {exc}"))

    async def _on_ready(self) -> None:
        """Restore the session on a fresh connection.

        Runs after the reader has started: mark the new connection unlogged,
        forget replies that belonged to the old one, log in when this session
        needs to, and replay the subscriptions.
        """
        self._is_logged_in = False
        self._subs.drop_requests()
        if self._needs_login():
            await self.login()
        await self._replay()

    async def _deliver(self, message: Message, payload: Any) -> None:
        await self._emit(message, self._subs.take(payload))

    async def _emit(self, message: Message, callback: Optional[Callback] = None) -> None:
        if callback is None:
            callback = self.callback
        if callback is None:
            return
        try:
            result = callback(message)
            if inspect.isawaitable(result):
                await result
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("WebSocket callback failed; dropping the message and continuing")

    @staticmethod
    def _parse(message: Message) -> Any:
        if not isinstance(message, (str, bytes)):
            return None
        try:
            return json.loads(message)
        except ValueError:
            return None

    # ------------------------------------------------------------------ auth

    async def login(self, timeout: float = DEFAULT_LOGIN_TIMEOUT) -> bool:
        """Authenticate the connection and wait for the server's acknowledgement.

        The protocol lives in `okxsdk.websocket.login.LoginHandshake`; this method
        only decides who feeds it — the reader always runs after `start()`, so
        the answer arrives through `_on_frame`.

        Concurrent callers share one attempt: the lock serializes them, and a
        caller that arrives after a success sees `_is_logged_in` and returns
        without sending a second login.
        """
        if self._is_logged_in:
            return True
        if not self._has_credentials():
            raise ValueError("apiKey, secretKey and passphrase are required for login")
        if self._connection.socket is None:
            raise RuntimeError("start() must be called before login()")
        if self._login_lock is None:
            # Created on first use, inside the running loop; stop() drops it so
            # a session restarted on another loop does not reuse a stale lock.
            self._login_lock = asyncio.Lock()

        async with self._login_lock:
            if self._is_logged_in:
                return True
            if self._connection.socket is None:
                raise RuntimeError("start() must be called before login()")

            payload = login_payload(
                api_key=self.apiKey,
                passphrase=self.passphrase,
                secret_key=self.secretKey,
            )
            if self.debug:
                masked = json.loads(payload)
                for arg in masked.get("args", []):
                    for field in ("apiKey", "passphrase", "sign"):
                        if field in arg:
                            arg[field] = "***"
                logger.debug("login: %s", json.dumps(masked))

            handshake = LoginHandshake(timeout)
            self._handshake = handshake
            try:
                await self._connection.send(payload)
                await handshake.wait()
            except BaseException:
                self._is_logged_in = False
                raise
            finally:
                self._handshake = None
            self._is_logged_in = True
            self._ever_logged_in = True
            return True

    def _has_credentials(self) -> bool:
        return bool(self.apiKey and self.passphrase and self.secretKey)

    def _needs_login(self) -> bool:
        """Whether this connection should authenticate before it is used.

        `_LOGIN_REQUIRED` is what the class always wanted; `_ever_logged_in`
        keeps a public client that logged in for the business channel logging
        in after a reconnect. The other two terms are the current state.
        """
        return (
            (self._LOGIN_REQUIRED or self._ever_logged_in)
            and not self._is_logged_in
            and self._has_credentials()
        )

    async def _ensure_login(self) -> None:
        if self._needs_login():
            await self.login()

    # ------------------------------------------------------------------ operations

    async def subscribe(
        self,
        params: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Subscribe and route messages for these args to `callback`.

        Every arg needs a non-blank `channel`; the table rejects anything else
        with `ValueError` before the table or the socket is touched, since the
        server would reject it later without a traceable owner.

        The table is updated before the frame goes out: if the send fails the
        subscription is still replayed on the next connection, which is the
        safe direction.
        """
        self._subs.add(params, callback)
        await self._ensure_login()
        await self._send_payload("subscribe", params, id)

    async def unsubscribe(
        self,
        params: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Unsubscribe; messages for these args fall back to `callback`.

        The table applies the same arg rule as subscribe(), so an unroutable
        arg raises `ValueError` before anything is removed or sent.
        """
        self._subs.remove(params)
        await self._ensure_login()
        await self._send_payload("unsubscribe", params, id)

    async def send(
        self,
        op: str,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Send a generic operation.

        A callback with an `id` is remembered for that one response; without
        an `id` there is nothing to correlate it with, so it becomes the
        fallback and keeps the 0.11 behaviour. subscribe() and unsubscribe()
        are the entries that maintain the subscription table.
        """
        if callback is not None:
            if id is not None:
                self._subs.add_request(id, callback)
            else:
                self.callback = callback
        await self._ensure_login()
        await self._send_payload(op, args, id)

    async def _send_payload(
        self,
        op: str,
        args: List[Dict[str, Any]],
        id: Optional[str],
    ) -> None:
        payload_dict: Dict[str, Any] = {"op": op, "args": args}
        if id is not None:
            payload_dict["id"] = id
        payload = json.dumps(payload_dict)
        if self.debug:
            logger.debug("send: %s", payload)
        await self._connection.send(payload)

    async def _replay(self) -> None:
        args = self._subs.replay()
        if not args:
            return
        for arg in args:
            await self._send_payload("subscribe", [arg], None)
        logger.info("Resubscribed to %d channel(s)", len(args))

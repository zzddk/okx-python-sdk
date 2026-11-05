"""Shared WebSocket session lifecycle.

`WsPublicAsync` and `WsPrivateAsync` differ only in their constructors and the
private trading helpers. Everything that keeps a connection alive — the read
loop, the heartbeat, reconnect and subscription replay — lives here so it is
written once.

Routing and callbacks
----------------------
A message is delivered to the callback registered for its `arg`; an
acknowledgement without `arg` (such as an order response) is matched by its
`id`. Only a message that matches neither reaches `callback`, which is a
deprecated fallback kept until 1.0. The table itself lives in
`okx.websocket.subscriptions`.

A callback may be a plain function or an `async def`. A coroutine is awaited,
so it never blocks the event loop; a plain function is called inline (kept for
callers written against 0.8 and earlier). Either way an exception raised by the
callback is logged and the next message is still delivered — a broken callback
cannot end the stream.

Protocol frames
---------------
The server answers a text `ping` with `pong`. Pong frames are consumed by the
heartbeat machinery and are not handed to the callback. A missing pong makes
the connection count as dead, which triggers a reconnect.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
from contextlib import suppress
from typing import Any, Dict, List, Optional, Union

from websockets.exceptions import ConnectionClosed, ConnectionClosedError

from okx.websocket import WsUtils
from okx.websocket.connector import WebSocketConnector
from okx.websocket.login import LoginHandshake
from okx.websocket.subscriptions import Callback, Subscriptions, key

logger = logging.getLogger(__name__)

Message = Union[str, bytes]

DEFAULT_PING_INTERVAL = 25.0
DEFAULT_PING_TIMEOUT = 10.0
DEFAULT_RECONNECT_BACKOFF = 1.0
DEFAULT_RECONNECT_MAX_BACKOFF = 60.0


def _require_channel(arg: Dict[str, Any]) -> None:
    """Reject an arg the server cannot route: a blank or missing channel."""
    channel = arg.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"channel must be a non-blank string, got {channel!r}")


class WsBaseAsync:
    """One OKX WebSocket session with heartbeat, reconnect and replay.

    Subclasses only supply a constructor (and, for the private client, the
    order-entry helpers). `_LOGIN_REQUIRED` selects whether subscribing
    authenticates first, which is what `WsPrivateAsync` always did.

    The socket is opened by `connector`; when it is omitted a
    `WebSocketConnector` is built with `proxy`. Supplying both keeps the
    connector and ignores `proxy`, the same rule as
    `Transport(proxy=, http=)`.
    """

    _LOGIN_REQUIRED = False

    def __init__(
        self,
        url: str,
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
        self.url = url
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
        self.websocket: Any = None
        self.isLoggedIn = False

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.reconnect = reconnect
        self.reconnect_backoff = reconnect_backoff
        self.reconnect_max_backoff = reconnect_max_backoff

        # Set from _LOGIN_REQUIRED, then latched on the first successful login
        # so a public client that logged in for the business channel keeps
        # logging in after a reconnect.
        self._should_login = self._LOGIN_REQUIRED
        self._stopping = False
        self._task: Optional[asyncio.Task] = None
        self._consumer: Optional[asyncio.Task] = None
        self._heartbeat: Optional[asyncio.Task] = None
        self._pong: Optional[asyncio.Event] = None
        self._handshake: Optional[LoginHandshake] = None

        if debug:
            logger.setLevel(logging.DEBUG)

    @property
    def subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Deprecated read-only view of the subscribed args, keyed like replay.

        Derived from `_subs` on every read, so there is no second copy of the
        state. Assigning raises `AttributeError`; subscribe() and
        unsubscribe() are the supported way to change it. Removed before 1.0.
        """
        return {key(arg): arg for arg in self._subs.replay()}

    # ------------------------------------------------------------------ start/stop

    async def connect(self) -> None:
        self.websocket = await self._connector.connect(self.url)

    async def start(self) -> asyncio.Task:
        """Connect and start the reader, heartbeat and reconnect supervisor.

        The returned task is the supervisor. It stays alive across reconnects
        and finishes only when `stop()` is called (or when `reconnect=False`
        and the connection ends).
        """
        if self._task is not None and not self._task.done():
            raise RuntimeError("WebSocket is already started")
        self.loop = asyncio.get_running_loop()
        self._stopping = False
        self._pong = asyncio.Event()
        if self.debug:
            logger.debug("Connecting to WebSocket...")
        else:
            logger.info("Connecting to WebSocket...")
        await self.connect()
        self._start_connection_tasks()
        self._task = asyncio.create_task(self._supervise())
        return self._task

    async def stop(self) -> None:
        """Stop the supervisor, the heartbeat and the socket. Idempotent."""
        self._stopping = True
        current = asyncio.current_task()
        task = self._task
        self._task = None
        # A callback may call stop() from inside consume(); cancelling the
        # supervisor then would cancel the very task awaiting us.
        if task is not None and task is not current and current is not self._consumer:
            task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task
        await self._stop_heartbeat()
        await self._close_socket()
        self._subs.drop_requests()
        self.isLoggedIn = False

    def stop_sync(self) -> None:
        if self.loop is None:
            raise RuntimeError("stop_sync() requires a prior start(); no event loop has been captured")
        if self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.stop(), self.loop)
            future.result(timeout=10)
        else:
            self.loop.run_until_complete(self.stop())

    # ------------------------------------------------------------------ read loop

    async def consume(self) -> None:
        """Read frames from the current socket until it closes.

        A closed connection raises `ConnectionClosedError` after the callback
        has been told; the supervisor catches it and reconnects.
        """
        if self.websocket is None:
            raise RuntimeError("connect() must be called before consume()")
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except ConnectionClosedError as exc:
            logger.error("WebSocket connection closed: %s", exc)
            await self._emit_error("ConnClosed", str(exc))
            raise

    async def _handle_message(self, message: Message) -> None:
        if self.debug:
            logger.debug("Received message: {%s}", message)
        if message == "pong":
            if self._pong is not None:
                self._pong.set()
            return
        payload = self._parse(message)
        if LoginHandshake.is_ack(payload):
            # A login answer is never delivered: it belongs to the handshake.
            handshake = self._handshake
            if handshake is not None:
                handshake.feed(payload)
            return
        await self._deliver(message, payload)

    async def _deliver(self, message: Message, payload: Any) -> None:
        callback = self._subs.take(payload)
        if callback is None:
            callback = self.callback
        await self._emit(message, callback)

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

    async def _emit_error(self, code: str, msg: str) -> None:
        await self._emit(json.dumps({"event": "error", "code": code, "msg": msg}))

    @staticmethod
    def _parse(message: Message) -> Any:
        if not isinstance(message, (str, bytes)):
            return None
        try:
            return json.loads(message)
        except ValueError:
            return None

    # ------------------------------------------------------------------ auth

    async def login(self, timeout: float = 10.0) -> bool:
        """Authenticate the connection and wait for the server's acknowledgement.

        The protocol lives in `okx.websocket.login.LoginHandshake`; this method
        only decides who feeds it. When the reader is running the acknowledgement
        is delivered by it (a second `recv()` there would collide); otherwise the
        handshake reads the socket itself, which is what happens during a
        reconnect and after `connect()` before `start()`.
        """
        if self.isLoggedIn:
            return True
        if not self._has_credentials():
            raise ValueError("apiKey, secretKey and passphrase are required for login")
        if self.websocket is None:
            raise RuntimeError("start() must be called before login()")

        payload = WsUtils.initLoginParams(
            apiKey=self.apiKey,
            passphrase=self.passphrase,
            secretKey=self.secretKey,
        )
        if self.debug:
            logger.debug("login: %s", payload)

        handshake = LoginHandshake(timeout)
        self._handshake = handshake
        try:
            await self.websocket.send(payload)
            if self._consuming():
                await handshake.wait()
            else:
                await handshake.read(self.websocket, self._parse, self._emit)
        except BaseException:
            self.isLoggedIn = False
            raise
        finally:
            self._handshake = None
        self.isLoggedIn = True
        self._should_login = True
        return True

    def _consuming(self) -> bool:
        return self._consumer is not None and not self._consumer.done()

    def _has_credentials(self) -> bool:
        return bool(self.apiKey and self.passphrase and self.secretKey)

    async def _ensure_login(self) -> None:
        if self._should_login and not self.isLoggedIn and self._has_credentials():
            await self.login()

    # ------------------------------------------------------------------ operations

    async def subscribe(
        self,
        params: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Subscribe and route messages for these args to `callback`.

        Every dict arg needs a non-blank `channel`; anything else raises
        `ValueError` before the table or the socket is touched, since the
        server would reject it later without a traceable owner.

        The table is updated before the frame goes out: if the send fails the
        subscription is still replayed on the next connection, which is the
        safe direction.
        """
        for arg in params:
            if isinstance(arg, dict):
                _require_channel(arg)
        self._subs.add(params, callback)
        await self._ensure_login()
        await self._send_payload("subscribe", params, id)

    async def unsubscribe(
        self,
        params: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Unsubscribe; messages for these args fall back to `callback`."""
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
        if self.websocket is None:
            raise RuntimeError("not connected: call start() first")
        payload_dict: Dict[str, Any] = {"op": op, "args": args}
        if id is not None:
            payload_dict["id"] = id
        payload = json.dumps(payload_dict)
        if self.debug:
            logger.debug("send: %s", payload)
        await self.websocket.send(payload)

    async def _replay(self) -> None:
        args = self._subs.replay()
        if not args:
            return
        for arg in args:
            await self._send_payload("subscribe", [arg], None)
        logger.info("Resubscribed to %d channel(s)", len(args))

    # ------------------------------------------------------------------ lifecycle

    def _start_connection_tasks(self) -> None:
        self._consumer = asyncio.create_task(self.consume())
        self._heartbeat = asyncio.create_task(self._heartbeat_loop())

    async def _supervise(self) -> None:
        while True:
            error: Optional[BaseException] = None
            try:
                await self._consumer
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                error = exc
                logger.warning("WebSocket stream ended: %s", exc)
            finally:
                await self._stop_heartbeat()

            if self._stopping:
                return
            if not self.reconnect:
                if error is not None:
                    raise error
                return

            logger.info("Reconnecting WebSocket...")
            await self._reconnect()
            if self._stopping:
                return
            self._start_connection_tasks()

    async def _reconnect(self) -> None:
        delay = self.reconnect_backoff
        while not self._stopping:
            try:
                await self._close_socket()
                await self.connect()
                await self._restore_session()
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Reconnect failed: %s; retrying in %.1fs", exc, delay)
                await self._close_socket()
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.reconnect_max_backoff)

    async def _restore_session(self) -> None:
        self.isLoggedIn = False
        # Replies to requests made on the old connection will never arrive.
        self._subs.drop_requests()
        if self._should_login and self._has_credentials():
            await self.login()
        await self._replay()

    async def _heartbeat_loop(self) -> None:
        if not self.ping_interval or self.ping_interval <= 0:
            return
        pong = self._pong
        while not self._stopping:
            await asyncio.sleep(self.ping_interval)
            if self._stopping or self.websocket is None or pong is None:
                return
            pong.clear()
            try:
                await self.websocket.send("ping")
            except ConnectionClosed:
                return
            try:
                await asyncio.wait_for(pong.wait(), timeout=self.ping_timeout)
            except asyncio.TimeoutError:
                # Close from here but do not call the user's callback: consume()
                # may be inside it, and callbacks are promised to run one at a
                # time in arrival order. The read loop will finish (or raise
                # ConnectionClosed) and the supervisor will reconnect.
                logger.warning("No pong within %.1fs; treating the connection as dead", self.ping_timeout)
                await self._close_socket()
                return

    async def _stop_heartbeat(self) -> None:
        task = self._heartbeat
        self._heartbeat = None
        if task is None:
            return
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError, Exception):
            await task

    async def _close_socket(self) -> None:
        websocket = self.websocket
        self.websocket = None
        if websocket is not None:
            with suppress(Exception):
                await websocket.close()

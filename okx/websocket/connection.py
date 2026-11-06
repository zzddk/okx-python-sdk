"""The connection supervisor: one socket and the tasks that keep it alive.

A WebSocket session has two kinds of state. One is what the protocol means --
which subscription owns a message, whether the login was accepted -- and it is
plain data, testable without a socket. The other is the connection itself: the
socket, the task reading it, the heartbeat, the reconnect backoff and the stop
flag. They used to share a class, so "who closes the socket when the pong is
late" and "stop() must not cancel the task that is calling it" were contracts
held only by comments.

This module owns the second kind. It knows nothing about subscriptions or the
login protocol: every frame that is not its own heartbeat goes to `on_frame`,
and after each successful connection it calls `on_ready` once, with the reader
already running. The session supplies both callbacks and keeps the meaning.

The heartbeat still wakes a stuck read loop by closing the socket, and a
callback may still call `stop()`; both are now internal to one object, and the
"am I being called from a dispatch?" question is answered by a context
variable rather than by comparing task identities.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from contextvars import ContextVar
from typing import Any, Awaitable, Callable, Optional, Union

from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

from okx.exceptions import PermanentConnectionError
from okx.websocket.connector import WebSocketConnector

logger = logging.getLogger(__name__)

Message = Union[str, bytes]
FrameHandler = Callable[[Message], Awaitable[None]]
ReadyHandler = Callable[[], Awaitable[None]]
# The socket ended on its own (not because stop() closed it).
LostHandler = Callable[[BaseException], None]

DEFAULT_PING_INTERVAL = 25.0
DEFAULT_PING_TIMEOUT = 10.0
DEFAULT_RECONNECT_BACKOFF = 1.0
DEFAULT_RECONNECT_MAX_BACKOFF = 60.0

# True while `on_frame` is running. A callback that calls stop() must not have
# the reader (and therefore itself) cancelled from under it; outside a dispatch
# stop() may await the supervisor task as before.
_DISPATCHING: ContextVar[bool] = ContextVar("okx_ws_dispatching", default=False)


class ConnectionSupervisor:
    """Owns the socket, the read loop, the heartbeat, backoff and stop.

    Construct it with the connector and URL to open, plus the two callbacks
    that give those bytes meaning. The socket is not opened until `start()`.
    """

    def __init__(
        self,
        connector: WebSocketConnector,
        url: Optional[str],
        on_frame: FrameHandler,
        on_ready: ReadyHandler,
        on_lost: LostHandler,
        *,
        ping_interval: Optional[float] = DEFAULT_PING_INTERVAL,
        ping_timeout: float = DEFAULT_PING_TIMEOUT,
        reconnect: bool = True,
        reconnect_backoff: float = DEFAULT_RECONNECT_BACKOFF,
        reconnect_max_backoff: float = DEFAULT_RECONNECT_MAX_BACKOFF,
        debug: bool = False,
    ) -> None:
        self.connector = connector
        self.url = url
        self._on_frame = on_frame
        self._on_ready = on_ready
        self._on_lost = on_lost
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.reconnect = reconnect
        self.reconnect_backoff = reconnect_backoff
        self.reconnect_max_backoff = reconnect_max_backoff
        self.debug = debug

        self._socket: Any = None
        self._task: Optional[asyncio.Task] = None
        self._reader: Optional[asyncio.Task] = None
        self._heartbeat: Optional[asyncio.Task] = None
        self._pong: Optional[asyncio.Event] = None
        self._stopping = False

    @property
    def socket(self) -> Any:
        """The open connection, or None between attempts. Read-only."""
        return self._socket

    async def start(self) -> asyncio.Task:
        """Open the first connection, then supervise it.

        The first connection is opened here rather than in the returned task,
        so a bad URL or a rejected login surfaces from `start()`. The task
        lives across reconnects and finishes when `stop()` is called, when
        `reconnect=False` and the stream ends, or with the error that ended it.
        """
        if self._task is not None and not self._task.done():
            raise RuntimeError(
                "WebSocket is already started or still stopping; "
                "wait for the previous supervisor to finish")
        self._stopping = False
        self._pong = asyncio.Event()
        await self._open()
        self._task = asyncio.create_task(self._supervise())
        return self._task

    async def stop(self) -> None:
        """Stop the supervisor, the heartbeat and the socket. Idempotent.

        When called from inside `on_frame` (a user callback calling stop()),
        it closes the socket and returns without cancelling the reader: that
        would cancel the very callback making the call. The frame finishes and
        the read loop ends on the closed socket. `_task` stays set until that
        happens, so `start()` refuses to open a second socket beside it.
        """
        self._stopping = True
        task = self._task
        await self._stop_heartbeat()
        await self._close_socket()
        if task is None:
            return
        # One place clears the reference: the supervisor itself, when it ends.
        task.add_done_callback(self._forget)
        if task.done() or _DISPATCHING.get():
            return
        task.cancel()
        with suppress(asyncio.CancelledError, Exception):
            await task

    def _forget(self, task: asyncio.Task) -> None:
        """Forget the supervisor once it ends, whether or not stop() awaited it."""
        if self._task is task:
            self._task = None

    async def send(self, payload: str) -> None:
        """Send one already-serialized frame on the current socket."""
        if self._socket is None:
            raise RuntimeError("not connected: call start() first")
        await self._socket.send(payload)

    # ------------------------------------------------------------------ opening

    async def _open(self) -> None:
        """Connect, start the reader and heartbeat, then run `on_ready`."""
        if self.debug:
            logger.debug("Connecting to WebSocket...")
        else:
            logger.info("Connecting to WebSocket...")
        socket = await self.connector.connect(self.url)
        self._socket = socket
        self._reader = asyncio.create_task(self._read(socket))
        self._heartbeat = asyncio.create_task(self._heartbeat_loop())
        try:
            await self._on_ready()
        except BaseException:
            await self._stop_reader()
            await self._stop_heartbeat()
            await self._close_socket()
            raise

    async def _supervise(self) -> None:
        while True:
            error: Optional[BaseException] = None
            try:
                await self._reader
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                error = exc
                level = logging.INFO if isinstance(exc, ConnectionClosedOK) else logging.WARNING
                logger.log(level, "WebSocket stream ended: %s", exc)
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

    async def _reconnect(self) -> None:
        delay = self.reconnect_backoff
        while not self._stopping:
            try:
                await self._close_socket()
                await self._open()
                return
            except asyncio.CancelledError:
                raise
            except PermanentConnectionError as exc:
                # Retrying the same endpoint returns the same answer: end the
                # supervisor so the task carries the reason to the caller.
                logger.error("Reconnect failed permanently: %s", exc)
                raise
            except Exception as exc:
                logger.warning("Reconnect failed: %s; retrying in %.1fs", exc, delay)
                await self._close_socket()
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.reconnect_max_backoff)

    # ------------------------------------------------------------------ reading

    async def _read(self, socket: Any) -> None:
        """Read frames from `socket` until it closes.

        The heartbeat's `pong` is consumed here; everything else goes to
        `on_frame`. A closed connection is reported to `on_lost` and re-raised
        so the supervisor can reconnect. It is not a frame: nothing the server
        sent looks like it, and nothing in it belongs in the callback stream.
        """
        try:
            async for message in socket:
                if message == "pong":
                    if self._pong is not None:
                        self._pong.set()
                    continue
                token = _DISPATCHING.set(True)
                try:
                    await self._on_frame(message)
                finally:
                    _DISPATCHING.reset(token)
        except ConnectionClosed as exc:
            if self._stopping:
                # stop() closed the socket on purpose; this is not a failure.
                return
            if isinstance(exc, ConnectionClosedError):
                logger.error("WebSocket connection closed: %s", exc)
            else:
                logger.info("WebSocket connection closed normally: %s", exc)
            self._on_lost(exc)
            raise

    # ------------------------------------------------------------------ heartbeat

    async def _heartbeat_loop(self) -> None:
        if not self.ping_interval or self.ping_interval <= 0:
            return
        pong = self._pong
        while not self._stopping:
            await asyncio.sleep(self.ping_interval)
            if self._stopping or self._socket is None or pong is None:
                return
            pong.clear()
            try:
                await self._socket.send("ping")
            except ConnectionClosed:
                return
            try:
                await asyncio.wait_for(pong.wait(), timeout=self.ping_timeout)
            except asyncio.TimeoutError:
                # Close from here but do not call the user's callback: the
                # reader may be inside one, and callbacks are promised to run
                # one at a time in arrival order. Closing the socket makes the
                # read loop finish, which makes the supervisor reconnect.
                logger.warning("No pong within %.1fs; treating the connection as dead", self.ping_timeout)
                await self._close_socket()
                return

    async def _cancel(self, task: Optional[asyncio.Task]) -> None:
        """Cancel `task` and wait for it, discarding whatever it raises."""
        if task is None:
            return
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError, Exception):
            await task

    async def _stop_heartbeat(self) -> None:
        task, self._heartbeat = self._heartbeat, None
        await self._cancel(task)

    async def _stop_reader(self) -> None:
        task, self._reader = self._reader, None
        await self._cancel(task)

    async def _close_socket(self) -> None:
        socket, self._socket = self._socket, None
        if socket is not None:
            with suppress(Exception):
                await socket.close()

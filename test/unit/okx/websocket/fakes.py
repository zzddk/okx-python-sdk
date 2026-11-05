"""Test doubles for the WebSocket connection seam."""

import asyncio
import json
from typing import Any, List, Optional

from websockets.exceptions import ConnectionClosedError


class FakeConnector:
    """Stand-in for `WebSocketConnector` that returns scripted sockets.

    Records the URLs it was asked to open so a test can assert that the
    supervisor went through the injected connector.
    """

    def __init__(self, *sockets: Any) -> None:
        self._sockets: List[Any] = list(sockets)
        self.urls: List[str] = []

    async def connect(self, url: str) -> Any:
        self.urls.append(url)
        if not self._sockets:
            raise AssertionError(f"no socket scripted for {url!r}")
        return self._sockets.pop(0)


class FakeSocket:
    """A scripted connection: queued frames, then either end or a drop.

    `FakeSocket(*frames)` yields the frames in order and then waits until
    `drop()` or `close()`; `ends=True` ends the stream (StopAsyncIteration)
    instead. `answer_pings=True` pushes a `pong` whenever the heartbeat sends
    a `ping`, which keeps the connection alive without a test loop.
    `answer_login=<frame>` pushes that frame when a login request is sent, so
    a private session can authenticate on `start()` without racing the queue.
    """

    def __init__(self, *frames: Any, ends: bool = False, answer_pings: bool = False,
                 answer_login: Optional[str] = None) -> None:
        self._frames: List[Any] = list(frames)
        self._wake = asyncio.Event()
        self._error: Optional[BaseException] = None
        self.ends = ends
        self.answer_pings = answer_pings
        self.answer_login = answer_login
        self.sent: List[str] = []
        self.closed = False

    def __aiter__(self) -> "FakeSocket":
        return self

    async def __anext__(self) -> Any:
        while not self._frames and self._error is None and not self.closed and not self.ends:
            await self._wake.wait()
            self._wake.clear()
        if self._frames:
            return self._frames.pop(0)
        if self._error is not None:
            raise self._error
        if self.ends:
            raise StopAsyncIteration
        raise ConnectionClosedError(None, None)

    def push(self, frame: Any) -> None:
        """Queue one frame for the next `__anext__`."""
        self._frames.append(frame)
        self._wake.set()

    def drop(self, exc: Optional[BaseException] = None) -> None:
        """End the stream with a connection error on the next read."""
        self._error = exc if exc is not None else ConnectionClosedError(None, None)
        self._wake.set()

    async def send(self, payload: str) -> None:
        self.sent.append(payload)
        if payload == "ping":
            if self.answer_pings:
                self.push("pong")
            return
        if self.answer_login is not None and '"op": "login"' in payload:
            self.push(self.answer_login)

    async def close(self) -> None:
        self.closed = True
        self._wake.set()

    @property
    def payloads(self) -> List[dict]:
        """The sent frames decoded as JSON, skipping the heartbeat's ping."""
        return [json.loads(payload) for payload in self.sent if payload != "ping"]

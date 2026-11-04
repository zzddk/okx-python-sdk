"""Test doubles for the WebSocket connection seam."""

from typing import Any, List


class FakeConnector:
    """Stand-in for `WebSocketConnector` that returns scripted sockets.

    Records the URLs it was asked to open so a test can assert that
    `WsBaseAsync.connect()` went through the injected connector.
    """

    def __init__(self, *sockets: Any) -> None:
        self._sockets: List[Any] = list(sockets)
        self.urls: List[str] = []

    async def connect(self, url: str) -> Any:
        self.urls.append(url)
        if not self._sockets:
            raise AssertionError(f"no socket scripted for {url!r}")
        return self._sockets.pop(0)

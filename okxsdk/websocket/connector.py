"""Open WebSocket connections, optionally through a proxy.

The connector is the injection seam for the socket: it returns a connection
and keeps no reference to it, so the connection supervisor stays the only
holder. Proxy support arrived in websockets 15.0 while this package accepts
10.0 and later, which is why the capability is probed on the live signature
instead of being derived from a version string.
"""

from __future__ import annotations

import inspect
import logging
import ssl
from typing import Any, Dict, Optional

import certifi
import websockets

logger = logging.getLogger(__name__)


class WebSocketConnector:
    """Opens one WebSocket connection per `connect()` call.

    `proxy=None` leaves `websockets.connect` alone: since 15.0 it detects the
    system/environment proxy by itself, and passing an explicit `None` would
    turn that off. When a proxy is set, a websockets build that does not accept
    `proxy=` is an error rather than a silent direct connection.
    """

    def __init__(self, proxy: Optional[str] = None) -> None:
        self._proxy = proxy

    async def connect(self, url: str) -> Any:
        """Open `url` and return the connection. The caller owns it."""
        kwargs: Dict[str, Any] = {'ssl': self._ssl_context()}
        if self._proxy is not None:
            if 'proxy' not in inspect.signature(websockets.connect).parameters:
                raise RuntimeError(
                    "proxy support requires websockets>=15.0; the installed "
                    "websockets does not accept the 'proxy' argument. Upgrade "
                    "websockets, or pass connector= with an object that opens "
                    "the connection itself."
                )
            kwargs['proxy'] = self._proxy
        try:
            connection = await websockets.connect(url, **kwargs)
        except Exception as e:
            # Swallowing this left callers iterating None, losing the real
            # cause (certificate, proxy, DNS). Let it surface instead.
            logger.error(f"Error connecting to WebSocket: {e}")
            raise
        logger.info("WebSocket connection established.")
        return connection

    @staticmethod
    def _ssl_context() -> ssl.SSLContext:
        context = ssl.create_default_context()
        context.load_verify_locations(certifi.where())
        return context

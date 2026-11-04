import logging
import ssl

import certifi
import websockets

logger = logging.getLogger(__name__)


class WebSocketFactory:

    def __init__(self, url):
        self.url = url
        self.websocket = None

    async def connect(self):
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())
        try:
            self.websocket = await websockets.connect(self.url, ssl=ssl_context)
        except Exception as e:
            # Swallowing this left callers iterating None, losing the real
            # cause (certificate, proxy, DNS). Let it surface instead.
            logger.error(f"Error connecting to WebSocket: {e}")
            raise
        logger.info("WebSocket connection established.")
        return self.websocket

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

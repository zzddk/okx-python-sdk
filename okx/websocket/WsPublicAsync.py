import asyncio
import json
import logging

from websockets.exceptions import ConnectionClosedError

from okx import consts
from okx.websocket import WsUtils
from okx.websocket.WebSocketFactory import WebSocketFactory

logger = logging.getLogger(__name__)


class WsPublicAsync:
    @classmethod
    def from_client(cls, client, channel: str = 'public', url: str = None, debug: bool = None):
        """Build from an existing REST client, matching its credentials and environment.

        `channel` selects the public or business endpoint; `client.flag == '1'`
        (demo trading) selects the demo host.
        """
        if channel not in ('public', 'business'):
            raise ValueError(f"channel must be 'public' or 'business', got {channel!r}")
        demo = str(client.flag) == '1'
        if url is None:
            if channel == 'business':
                url = consts.WS_BUSINESS_DEMO_URL if demo else consts.WS_BUSINESS_URL
            else:
                url = consts.WS_PUBLIC_DEMO_URL if demo else consts.WS_PUBLIC_URL
        return cls(
            url=url,
            apiKey=client.API_KEY,
            passphrase=client.PASSPHRASE,
            secretKey=client.API_SECRET_KEY,
            debug=client.debug if debug is None else debug,
        )

    def __init__(self, url=consts.WS_PUBLIC_URL, apiKey='', passphrase='', secretKey='', debug=False):
        self.url = url
        self.subscriptions = set()
        self.callback = None
        self.loop = None  # captured by start(); the loop must be running
        self.factory = WebSocketFactory(url)
        self.websocket = None
        self.debug = debug
        # Credentials for business channel login
        self.apiKey = apiKey
        self.passphrase = passphrase
        self.secretKey = secretKey
        self.isLoggedIn = False

        # Set log level
        if debug:
            logger.setLevel(logging.DEBUG)

    async def connect(self):
        self.websocket = await self.factory.connect()

    async def consume(self):
        try:
            async for message in self.websocket:
                if self.debug:
                    logger.debug("Received message: {%s}", message)
                if self.callback:
                    self.callback(message)
        except ConnectionClosedError as e:
            logger.error(f"WebSocket connection closed: {e}")
            if self.callback:
                self.callback(json.dumps({"event": "error", "code": "ConnClosed", "msg": str(e)}))
            raise

    async def _await_login_ack(self, timeout: float = 10.0) -> None:
        """Wait for the server's login response and surface a rejection.

        Frames that are not the login ack are handed to the callback so no
        message is lost. A timeout means the server never answered, which is
        just as unusable as a rejection.
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TimeoutError(f"no login acknowledgement within {timeout}s")
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                raise TimeoutError(f"no login acknowledgement within {timeout}s")
            payload = None
            if isinstance(message, (str, bytes)):
                try:
                    payload = json.loads(message)
                except ValueError:
                    payload = None
            if isinstance(payload, dict) and payload.get('event') == 'login':
                if str(payload.get('code', '0')) != '0':
                    raise ConnectionError(
                        f"login rejected: code={payload.get('code')} msg={payload.get('msg')}"
                    )
                return
            if self.callback:
                self.callback(message)

    async def login(self, timeout: float = 10.0) -> bool:
        """
        Login method for business channel that requires authentication (e.g. /ws/v5/business)
        """
        if not self.apiKey or not self.secretKey or not self.passphrase:
            raise ValueError("apiKey, secretKey and passphrase are required for login")

        loginPayload = WsUtils.initLoginParams(
            useServerTime=False,
            apiKey=self.apiKey,
            passphrase=self.passphrase,
            secretKey=self.secretKey
        )
        if self.debug:
            logger.debug(f"login: {loginPayload}")
        await self.websocket.send(loginPayload)
        try:
            await self._await_login_ack(timeout)
        except Exception:
            self.isLoggedIn = False
            raise
        self.isLoggedIn = True
        return True

    async def subscribe(self, params: list, callback, id: str = None):
        self.callback = callback
        payload_dict = {
            "op": "subscribe",
            "args": params
        }
        if id is not None:
            payload_dict["id"] = id
        payload = json.dumps(payload_dict)
        if self.debug:
            logger.debug(f"subscribe: {payload}")
        await self.websocket.send(payload)
        # await self.consume()

    async def unsubscribe(self, params: list, callback, id: str = None):
        self.callback = callback
        payload_dict = {
            "op": "unsubscribe",
            "args": params
        }
        if id is not None:
            payload_dict["id"] = id
        payload = json.dumps(payload_dict)
        if self.debug:
            logger.debug(f"unsubscribe: {payload}")
        else:
            logger.info(f"unsubscribe: {payload}")
        await self.websocket.send(payload)

    async def send(self, op: str, args: list, callback = None, id: str = None):
        """
        Generic send method
        :param op: Operation type
        :param args: Parameter list
        :param callback: Callback function
        :param id: Optional request ID
        """
        if callback:
            self.callback = callback
        payload_dict = {
            "op": op,
            "args": args
        }
        if id is not None:
            payload_dict["id"] = id
        payload = json.dumps(payload_dict)
        if self.debug:
            logger.debug(f"send: {payload}")
        await self.websocket.send(payload)

    async def stop(self):
        await self.factory.close()

    async def start(self):
        if self.debug:
            logger.debug("Connecting to WebSocket...")
        else:
            logger.info("Connecting to WebSocket...")
        await self.connect()
        self.loop = asyncio.get_running_loop()
        return asyncio.create_task(self.consume())

    def stop_sync(self):
        if self.loop is None:
            raise RuntimeError("stop_sync() requires a prior start(); no event loop has been captured")
        if self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.stop(), self.loop)
            future.result(timeout=10)
        else:
            self.loop.run_until_complete(self.stop())

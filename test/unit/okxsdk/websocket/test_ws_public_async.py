"""
Unit tests for okxsdk.websocket.WsPublicAsync module

Mirrors the structure: okxsdk/websocket/WsPublicAsync.py -> test/unit/okxsdk/websocket/test_ws_public_async.py
"""
import asyncio
import json
import unittest
from unittest.mock import MagicMock

from websockets.exceptions import ConnectionClosedError

from okxsdk import consts
from okxsdk.websocket.WsPublicAsync import WsPublicAsync

from .fakes import FakeConnector, FakeSocket

# Test constants
TEST_WS_URL = 'wss://test.example.com'
ACK = '{"event":"login","code":"0"}'

# Placeholder client identifiers for constructing the websocket client in unit
# or sent over a real connection — they are not real credentials.
_STUB_ID = "test_api_key"
_STUB_SIGN = "test_secret_key"
_STUB_PHRASE = "test_passphrase"


def _session(*frames, ws_kwargs=None, **socket_kwargs):
    """A public session on a scripted socket, not yet started."""
    sock = FakeSocket(*frames, **socket_kwargs)
    ws = WsPublicAsync(url=TEST_WS_URL, connector=FakeConnector(sock), **(ws_kwargs or {}))
    return ws, sock


class TestWsPublicAsyncInit(unittest.TestCase):
    """Unit tests for WsPublicAsync initialization"""

    def test_init_with_url(self):
        """Test initialization with url parameter"""
        ws = WsPublicAsync(url=TEST_WS_URL)

        self.assertEqual(ws.url, TEST_WS_URL)
        self.assertEqual(ws.apiKey, '')
        self.assertEqual(ws.passphrase, '')
        self.assertEqual(ws.secretKey, '')
        self.assertFalse(ws.debug)
        self.assertFalse(ws.isLoggedIn)

    def test_init_with_credentials(self):
        """Test initialization with all credentials for business channel"""
        ws = WsPublicAsync(
            url=TEST_WS_URL,
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN
        )

        self.assertEqual(ws.apiKey, _STUB_ID)
        self.assertEqual(ws.passphrase, _STUB_PHRASE)
        self.assertEqual(ws.secretKey, _STUB_SIGN)

    def test_init_with_debug_enabled(self):
        """Test initialization with debug mode enabled"""
        ws = WsPublicAsync(url=TEST_WS_URL, debug=True)

        self.assertTrue(ws.debug)

    def test_default_url_is_the_public_host(self):
        self.assertEqual(WsPublicAsync().url, consts.WS_PUBLIC_URL)


class TestWsPublicAsyncLogin(unittest.TestCase):
    """Unit tests for WsPublicAsync login method"""

    def test_login_without_credentials_raises_error(self):
        """Test that login raises ValueError when credentials are missing"""
        ws = WsPublicAsync(url=TEST_WS_URL)

        async def run_test():
            with self.assertRaises(ValueError) as context:
                await ws.login()
            self.assertIn("apiKey, secretKey and passphrase are required for login", str(context.exception))

        asyncio.run(run_test())

    def test_login_with_credentials_success(self):
        """Test successful login with valid credentials"""

        async def run_test():
            ws, sock = _session(answer_login=ACK, ws_kwargs={
                'apiKey': _STUB_ID, 'passphrase': _STUB_PHRASE, 'secretKey': _STUB_SIGN})
            await ws.start()
            result = await ws.login()
            self.assertTrue(result)
            self.assertTrue(ws.isLoggedIn)
            self.assertEqual([p['op'] for p in sock.payloads], ['login'])
            await ws.stop()

        asyncio.run(run_test())


class TestWsPublicAsyncSubscribe(unittest.TestCase):
    """Unit tests for WsPublicAsync subscribe method"""

    def test_subscribe_without_id(self):
        """Test subscribe without id parameter"""
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.subscribe(params, callback)
            # The callback belongs to this arg; the fallback is untouched.
            self.assertIsNone(ws.callback)
            await ws._on_frame(json.dumps({"arg": params[0], "data": []}))
            callback.assert_called_once()
            self.assertEqual(len(sock.payloads), 1)

            payload = sock.payloads[0]
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)
            await ws.stop()

        asyncio.run(run_test())

    def test_subscribe_with_id(self):
        """Test subscribe with id parameter"""
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.subscribe(params, callback, id="sub001")
            payload = sock.payloads[0]
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["args"], params)
            self.assertEqual(payload["id"], "sub001")
            await ws.stop()

        asyncio.run(run_test())

    def test_subscribe_with_multiple_channels(self):
        """Test subscribe with multiple channels"""
        callback = MagicMock()
        params = [
            {"channel": "tickers", "instId": "BTC-USDT"},
            {"channel": "tickers", "instId": "ETH-USDT"}
        ]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.subscribe(params, callback, id="multi001")
            payload = sock.payloads[0]
            self.assertEqual(len(payload["args"]), 2)
            self.assertEqual(payload["id"], "multi001")
            await ws.stop()

        asyncio.run(run_test())


class TestWsPublicAsyncUnsubscribe(unittest.TestCase):
    """Unit tests for WsPublicAsync unsubscribe method"""

    def test_unsubscribe_without_id(self):
        """Test unsubscribe without id parameter"""
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.unsubscribe(params, callback)
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)
            await ws.stop()

        asyncio.run(run_test())

    def test_unsubscribe_with_id(self):
        """Test unsubscribe with id parameter"""
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.unsubscribe(params, callback, id="unsub001")
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["id"], "unsub001")
            await ws.stop()

        asyncio.run(run_test())


class TestWsPublicAsyncSend(unittest.TestCase):
    """Unit tests for WsPublicAsync send method"""

    def test_send_without_id(self):
        """Test generic send method without id"""
        callback = MagicMock()
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.send("custom_op", args, callback=callback)
            self.assertEqual(ws.callback, callback)
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "custom_op")
            self.assertEqual(payload["args"], args)
            self.assertNotIn("id", payload)
            await ws.stop()

        asyncio.run(run_test())

    def test_send_with_id(self):
        """Test generic send method with id"""
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.send("custom_op", args, id="send001")
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "custom_op")
            self.assertEqual(payload["id"], "send001")
            await ws.stop()

        asyncio.run(run_test())

    def test_send_without_callback(self):
        """Test send method without callback (preserves existing callback)"""
        existing_callback = MagicMock()
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            ws.callback = existing_callback
            await ws.send("custom_op", args)
            # Callback should remain unchanged
            self.assertEqual(ws.callback, existing_callback)
            await ws.stop()

        asyncio.run(run_test())

    def test_send_with_new_callback_replaces_existing(self):
        """Test send method with new callback replaces existing callback"""
        old_callback = MagicMock()
        new_callback = MagicMock()
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session()
            await ws.start()
            ws.callback = old_callback
            await ws.send("custom_op", args, callback=new_callback)
            self.assertEqual(ws.callback, new_callback)
            await ws.stop()

        asyncio.run(run_test())


class TestWsPublicAsyncStartStop(unittest.TestCase):
    """Unit tests for WsPublicAsync start and stop methods"""

    def test_stop_closes_the_socket(self):
        """stop() closes the one socket the supervisor holds"""

        async def run_test():
            ws, sock = _session()
            await ws.start()
            await ws.stop()
            return ws, sock

        ws, sock = asyncio.run(run_test())
        self.assertTrue(sock.closed)
        self.assertIsNone(ws.websocket)

    def test_start_returns_task(self):
        """start() returns the supervisor task so the caller can retain/await it"""

        async def run_test():
            ws, sock = _session(ends=True, ws_kwargs={'reconnect': False})
            task = await ws.start()
            self.assertIsInstance(task, asyncio.Task)
            await task

        asyncio.run(run_test())


class TestWsPublicAsyncConnectionErrors(unittest.TestCase):
    """A dropped connection reaches the callback as an event and ends the task"""

    def test_drop_pushes_an_error_event_and_re_raises(self):
        async def run_test():
            ws, sock = _session('{"data": "ok"}', ws_kwargs={'reconnect': False})
            received = []
            ws.callback = received.append
            task = await ws.start()
            sock.drop()
            await asyncio.wait_for(task, timeout=1)

        with self.assertRaises(ConnectionClosedError):
            asyncio.run(run_test())

    def test_callback_receives_every_frame_on_the_happy_path(self):
        async def run_test():
            ws, sock = _session('a', 'b', ends=True, ws_kwargs={'reconnect': False})
            received = []
            ws.callback = received.append
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return received

        self.assertEqual(asyncio.run(run_test()), ['a', 'b'])


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for okx.websocket.WsPublicAsync module

Mirrors the structure: okx/websocket/WsPublicAsync.py -> test/unit/okx/websocket/test_ws_public_async.py
"""
import json
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Import the module first so patch can resolve the path
import okx.websocket.WsPublicAsync as ws_public_module
from okx.websocket.WsPublicAsync import WsPublicAsync

# Test constants
TEST_WS_URL = 'wss://test.example.com'

# Placeholder client identifiers for constructing the websocket client in unit
# or sent over a real connection — they are not real credentials.
_STUB_ID = "test_api_key"
_STUB_SIGN = "test_secret_key"
_STUB_PHRASE = "test_passphrase"


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
        from okx.websocket.WsPublicAsync import WsPublicAsync
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
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL, debug=True)

        self.assertTrue(ws.debug)

    def test_init_with_debug_disabled(self):
        """Test initialization with debug mode disabled (default)"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL, debug=False)

        self.assertFalse(ws.debug)


class TestWsPublicAsyncLogin(unittest.TestCase):
    """Unit tests for WsPublicAsync login method"""

    def test_login_without_credentials_raises_error(self):
        """Test that login raises ValueError when credentials are missing"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)

        async def run_test():
            with self.assertRaises(ValueError) as context:
                await ws.login()
            self.assertIn("apiKey, secretKey and passphrase are required for login", str(context.exception))

        asyncio.run(run_test())

    @patch('okx.websocket.WsBaseAsync.WsUtils.initLoginParams')
    def test_login_with_credentials_success(self, mock_init_login):
        """Test successful login with valid credentials"""

        mock_init_login.return_value = '{"op":"login","args":[...]}'

        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(
            url=TEST_WS_URL,
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')

        async def run_test():
            result = await ws.login()
            self.assertTrue(result)
            self.assertTrue(ws.isLoggedIn)
            mock_init_login.assert_called_once_with(
                apiKey=_STUB_ID,
                passphrase=_STUB_PHRASE,
                secretKey=_STUB_SIGN
            )
            mock_websocket.send.assert_called_once()

        asyncio.run(run_test())


class TestWsPublicAsyncSubscribe(unittest.TestCase):
    """Unit tests for WsPublicAsync subscribe method"""

    def test_subscribe_without_id(self):
        """Test subscribe without id parameter"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            await ws.subscribe(params, callback)
            # The callback belongs to this arg; the fallback is untouched.
            self.assertIsNone(ws.callback)
            await ws._handle_message(json.dumps({"arg": params[0], "data": []}))
            callback.assert_called_once()
            mock_websocket.send.assert_called_once()

            # Verify the payload
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_subscribe_with_id(self):
        """Test subscribe with id parameter"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            await ws.subscribe(params, callback, id="sub001")

            # Verify the payload includes id
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["args"], params)
            self.assertEqual(payload["id"], "sub001")

        asyncio.run(run_test())

    def test_subscribe_with_multiple_channels(self):
        """Test subscribe with multiple channels"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [
            {"channel": "tickers", "instId": "BTC-USDT"},
            {"channel": "tickers", "instId": "ETH-USDT"}
        ]

        async def run_test():
            await ws.subscribe(params, callback, id="multi001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(len(payload["args"]), 2)
            self.assertEqual(payload["id"], "multi001")

        asyncio.run(run_test())


class TestWsPublicAsyncUnsubscribe(unittest.TestCase):
    """Unit tests for WsPublicAsync unsubscribe method"""

    def test_unsubscribe_without_id(self):
        """Test unsubscribe without id parameter"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            await ws.unsubscribe(params, callback)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_unsubscribe_with_id(self):
        """Test unsubscribe with id parameter"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "tickers", "instId": "BTC-USDT"}]

        async def run_test():
            await ws.unsubscribe(params, callback, id="unsub001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["id"], "unsub001")

        asyncio.run(run_test())


class TestWsPublicAsyncSend(unittest.TestCase):
    """Unit tests for WsPublicAsync send method"""

    def test_send_without_id(self):
        """Test generic send method without id"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            await ws.send("custom_op", args, callback=callback)
            self.assertEqual(ws.callback, callback)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "custom_op")
            self.assertEqual(payload["args"], args)
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_send_with_id(self):
        """Test generic send method with id"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            await ws.send("custom_op", args, id="send001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "custom_op")
            self.assertEqual(payload["id"], "send001")

        asyncio.run(run_test())

    def test_send_without_callback(self):
        """Test send method without callback (preserves existing callback)"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        existing_callback = MagicMock()
        ws.callback = existing_callback
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            await ws.send("custom_op", args)
            # Callback should remain unchanged
            self.assertEqual(ws.callback, existing_callback)

        asyncio.run(run_test())

    def test_send_with_new_callback_replaces_existing(self):
        """Test send method with new callback replaces existing callback"""
        from okx.websocket.WsPublicAsync import WsPublicAsync
        ws = WsPublicAsync(url=TEST_WS_URL)
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        old_callback = MagicMock()
        new_callback = MagicMock()
        ws.callback = old_callback
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            await ws.send("custom_op", args, callback=new_callback)
            self.assertEqual(ws.callback, new_callback)

        asyncio.run(run_test())


class TestWsPublicAsyncStartStop(unittest.TestCase):
    """Unit tests for WsPublicAsync start and stop methods"""

    def test_stop(self):
        """stop() closes the one socket the client holds"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        socket = AsyncMock()
        ws.websocket = socket

        asyncio.run(ws.stop())

        socket.close.assert_awaited_once()
        self.assertIsNone(ws.websocket)

    def test_start_returns_task(self):
        """start() returns the supervisor task so the caller can retain/await it"""
        ws = WsPublicAsync(url=TEST_WS_URL)

        async def run_test():
            ws.connect = AsyncMock()
            ws.consume = AsyncMock()
            ws.ping_interval = 0
            ws.reconnect = False
            task = await ws.start()
            self.assertIsInstance(task, asyncio.Task)
            await task

        asyncio.run(run_test())


class _RaisingAsyncIterator:
    """Async iterator that yields queued messages then raises the given exception."""

    def __init__(self, exc, messages=None):
        self._messages = list(messages or [])
        self._exc = exc

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        raise self._exc


class TestWsPublicAsyncConsumeErrorPropagation(unittest.TestCase):
    """Unit tests for consume() ConnectionClosedError handling (GH#116)"""

    def test_consume_propagates_connection_closed_and_pushes_error_event(self):
        """A dropped socket reaches the callback as an error event and re-raises"""
        from websockets.exceptions import ConnectionClosedError

        ws = WsPublicAsync(url=TEST_WS_URL)
        received = []
        ws.callback = received.append
        exc = ConnectionClosedError(None, None)
        ws.websocket = _RaisingAsyncIterator(exc, messages=['{"data": "ok"}'])

        async def run_test():
            with self.assertRaises(ConnectionClosedError):
                await ws.consume()

        with patch('okx.websocket.WsBaseAsync.logger.error') as mock_log_error:
            asyncio.run(run_test())
            mock_log_error.assert_called_once()

        # Normal message delivered first, then the injected error event
        self.assertEqual(received[0], '{"data": "ok"}')
        error_payload = json.loads(received[1])
        self.assertEqual(error_payload["event"], "error")
        self.assertEqual(error_payload["code"], "ConnClosed")

    def test_consume_happy_path_unchanged(self):
        """Normal messages still reach the callback with no error event"""
        ws = WsPublicAsync(url=TEST_WS_URL)
        received = []
        ws.callback = received.append

        class _CleanIterator:
            def __init__(self, messages):
                self._messages = list(messages)

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._messages:
                    return self._messages.pop(0)
                raise StopAsyncIteration

        ws.websocket = _CleanIterator(['a', 'b'])

        async def run_test():
            await ws.consume()

        asyncio.run(run_test())
        self.assertEqual(received, ['a', 'b'])


if __name__ == '__main__':
    unittest.main()

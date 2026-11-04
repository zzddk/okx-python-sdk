"""
Unit tests for okx.websocket.WsPrivateAsync module

Mirrors the structure: okx/websocket/WsPrivateAsync.py -> test/unit/okx/websocket/test_ws_private_async.py
"""
import json
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Import the module first so patch can resolve the path
import okx.websocket.WsPrivateAsync as ws_private_module
from okx.websocket.WsPrivateAsync import WsPrivateAsync

# Test constants
TEST_WS_URL = 'wss://test.example.com'

# Placeholder client identifiers for constructing the websocket client in unit
# or sent over a real connection — they are not real credentials.
_STUB_ID = "test_api_key"
_STUB_SIGN = "test_secret_key"
_STUB_PHRASE = "test_passphrase"


class TestWsPrivateAsyncInit(unittest.TestCase):
    """Unit tests for WsPrivateAsync initialization"""

    def test_init_with_required_params(self):
        """Test initialization with required parameters"""
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )

        self.assertEqual(ws.apiKey, _STUB_ID)
        self.assertEqual(ws.passphrase, _STUB_PHRASE)
        self.assertEqual(ws.secretKey, _STUB_SIGN)
        self.assertEqual(ws.url, TEST_WS_URL)
        self.assertFalse(ws.debug)

    def test_init_with_debug_enabled(self):
        """Test initialization with debug mode enabled"""
        from okx.websocket.WsPrivateAsync import WsPrivateAsync
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL,
            debug=True
        )

        self.assertTrue(ws.debug)


class TestWsPrivateAsyncSubscribe(unittest.TestCase):
    """Unit tests for WsPrivateAsync subscribe method"""

    @patch('okx.websocket.WsBaseAsync.WsUtils')
    def test_subscribe_sends_correct_payload(self, mock_ws_utils):
        """Test subscribe sends correct payload after login"""

        mock_ws_utils.initLoginParams.return_value = '{"op":"login"}'

        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            await ws.subscribe(params, callback)
            # The callback belongs to this arg; the fallback is untouched.
            self.assertIsNone(ws.callback)
            await ws._handle_message(json.dumps({"arg": params[0], "data": []}))
            callback.assert_called_once()
            # Second call should be the subscribe (first is login)
            subscribe_call = mock_websocket.send.call_args_list[1]
            payload = json.loads(subscribe_call[0][0])
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    @patch('okx.websocket.WsBaseAsync.WsUtils')
    def test_subscribe_with_id(self, mock_ws_utils):
        """Test subscribe with id parameter"""

        mock_ws_utils.initLoginParams.return_value = '{"op":"login"}'

        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            await ws.subscribe(params, callback, id="sub001")
            # Second call should be the subscribe (first is login)
            subscribe_call = mock_websocket.send.call_args_list[1]
            payload = json.loads(subscribe_call[0][0])
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["id"], "sub001")

        asyncio.run(run_test())


class TestWsPrivateAsyncUnsubscribe(unittest.TestCase):
    """Unit tests for WsPrivateAsync unsubscribe method"""

    def test_unsubscribe_sends_correct_payload(self):
        """Test unsubscribe sends correct payload"""
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

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
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            await ws.unsubscribe(params, callback, id="unsub001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["id"], "unsub001")

        asyncio.run(run_test())


class TestWsPrivateAsyncSend(unittest.TestCase):
    """Unit tests for WsPrivateAsync generic send method"""

    def test_send_without_id(self):
        """Test generic send method without id"""
        from okx.websocket.WsPrivateAsync import WsPrivateAsync
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
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
        from okx.websocket.WsPrivateAsync import WsPrivateAsync
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
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


class TestWsPrivateAsyncOrderMethods(unittest.TestCase):
    """Unit tests for WsPrivateAsync order-related methods"""

    def _create_ws_instance(self):
        """Helper to create WsPrivateAsync instance with mocked websocket"""
        from okx.websocket.WsPrivateAsync import WsPrivateAsync
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')
        return ws, mock_websocket

    def test_place_order_sends_correct_payload(self):
        """Test place_order sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        order_args = [{
            "instId": "BTC-USDT",
            "tdMode": "cash",
            "side": "buy",
            "ordType": "limit",
            "sz": "0.001",
            "px": "30000"
        }]

        async def run_test():
            await ws.place_order(order_args, callback=callback, id="order001")
            # An order acknowledgement carries no arg; its id finds the callback.
            self.assertIsNone(ws.callback)
            await ws._handle_message(json.dumps({"id": "order001", "op": "order", "data": []}))
            callback.assert_called_once()
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "order")
            self.assertEqual(payload["args"], order_args)
            self.assertEqual(payload["id"], "order001")

        asyncio.run(run_test())

    def test_place_order_without_id(self):
        """Test place_order without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        order_args = [{"instId": "BTC-USDT"}]

        async def run_test():
            await ws.place_order(order_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "order")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_batch_orders_sends_correct_payload(self):
        """Test batch_orders sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        order_args = [
            {"instId": "BTC-USDT", "side": "buy", "sz": "0.001", "px": "30000"},
            {"instId": "ETH-USDT", "side": "buy", "sz": "0.01", "px": "2000"}
        ]

        async def run_test():
            await ws.batch_orders(order_args, callback=callback, id="batch001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-orders")
            self.assertEqual(payload["args"], order_args)
            self.assertEqual(payload["id"], "batch001")

        asyncio.run(run_test())

    def test_batch_orders_without_id(self):
        """Test batch_orders without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        order_args = [{"instId": "BTC-USDT"}, {"instId": "ETH-USDT"}]

        async def run_test():
            await ws.batch_orders(order_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-orders")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_cancel_order_sends_correct_payload(self):
        """Test cancel_order sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        cancel_args = [{"instId": "BTC-USDT", "ordId": "12345"}]

        async def run_test():
            await ws.cancel_order(cancel_args, callback=callback, id="cancel001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "cancel-order")
            self.assertEqual(payload["args"], cancel_args)
            self.assertEqual(payload["id"], "cancel001")

        asyncio.run(run_test())

    def test_cancel_order_without_id(self):
        """Test cancel_order without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        cancel_args = [{"instId": "BTC-USDT", "ordId": "12345"}]

        async def run_test():
            await ws.cancel_order(cancel_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "cancel-order")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_batch_cancel_orders_sends_correct_payload(self):
        """Test batch_cancel_orders sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        cancel_args = [
            {"instId": "BTC-USDT", "ordId": "12345"},
            {"instId": "ETH-USDT", "ordId": "67890"}
        ]

        async def run_test():
            await ws.batch_cancel_orders(cancel_args, callback=callback, id="batchCancel001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-cancel-orders")
            self.assertEqual(payload["args"], cancel_args)
            self.assertEqual(payload["id"], "batchCancel001")

        asyncio.run(run_test())

    def test_batch_cancel_orders_without_id(self):
        """Test batch_cancel_orders without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        cancel_args = [{"instId": "BTC-USDT", "ordId": "12345"}]

        async def run_test():
            await ws.batch_cancel_orders(cancel_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-cancel-orders")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_amend_order_sends_correct_payload(self):
        """Test amend_order sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        amend_args = [{
            "instId": "BTC-USDT",
            "ordId": "12345",
            "newSz": "0.002",
            "newPx": "31000"
        }]

        async def run_test():
            await ws.amend_order(amend_args, callback=callback, id="amend001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "amend-order")
            self.assertEqual(payload["args"], amend_args)
            self.assertEqual(payload["id"], "amend001")

        asyncio.run(run_test())

    def test_amend_order_without_id(self):
        """Test amend_order without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        amend_args = [{"instId": "BTC-USDT", "ordId": "12345", "newSz": "0.002"}]

        async def run_test():
            await ws.amend_order(amend_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "amend-order")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_batch_amend_orders_sends_correct_payload(self):
        """Test batch_amend_orders sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        amend_args = [
            {"instId": "BTC-USDT", "ordId": "12345", "newSz": "0.002"},
            {"instId": "ETH-USDT", "ordId": "67890", "newPx": "2100"}
        ]

        async def run_test():
            await ws.batch_amend_orders(amend_args, callback=callback, id="batchAmend001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-amend-orders")
            self.assertEqual(payload["args"], amend_args)
            self.assertEqual(payload["id"], "batchAmend001")

        asyncio.run(run_test())

    def test_batch_amend_orders_without_id(self):
        """Test batch_amend_orders without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        amend_args = [{"instId": "BTC-USDT", "ordId": "12345", "newSz": "0.002"}]

        async def run_test():
            await ws.batch_amend_orders(amend_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "batch-amend-orders")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())

    def test_mass_cancel_sends_correct_payload(self):
        """Test mass_cancel sends correct operation"""
        ws, mock_websocket = self._create_ws_instance()
        callback = MagicMock()
        mass_cancel_args = [{
            "instType": "SPOT",
            "instFamily": "BTC-USDT"
        }]

        async def run_test():
            await ws.mass_cancel(mass_cancel_args, callback=callback, id="massCancel001")
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "mass-cancel")
            self.assertEqual(payload["args"], mass_cancel_args)
            self.assertEqual(payload["id"], "massCancel001")

        asyncio.run(run_test())

    def test_mass_cancel_without_id(self):
        """Test mass_cancel without id parameter"""
        ws, mock_websocket = self._create_ws_instance()
        mass_cancel_args = [{"instType": "SPOT", "instFamily": "BTC-USDT"}]

        async def run_test():
            await ws.mass_cancel(mass_cancel_args)
            call_args = mock_websocket.send.call_args[0][0]
            payload = json.loads(call_args)
            self.assertEqual(payload["op"], "mass-cancel")
            self.assertNotIn("id", payload)

        asyncio.run(run_test())


class TestWsPrivateAsyncLogin(unittest.TestCase):
    """Unit tests for WsPrivateAsync login method"""

    @patch('okx.websocket.WsBaseAsync.WsUtils')
    def test_login_calls_init_login_params(self, mock_ws_utils):
        """Test login calls WsUtils.initLoginParams with correct parameters"""

        mock_ws_utils.initLoginParams.return_value = '{"op":"login","args":[...]}'

        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        mock_websocket = AsyncMock()
        ws.websocket = mock_websocket
        mock_websocket.recv = AsyncMock(return_value='{"event":"login","code":"0"}')

        async def run_test():
            result = await ws.login()
            self.assertTrue(result)
            mock_ws_utils.initLoginParams.assert_called_once_with(
                apiKey=_STUB_ID,
                passphrase=_STUB_PHRASE,
                secretKey=_STUB_SIGN
            )

        asyncio.run(run_test())


class TestWsPrivateAsyncStartStop(unittest.TestCase):
    """Unit tests for WsPrivateAsync start and stop methods"""

    def test_stop(self):
        """stop() closes the one socket the client holds"""
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )
        socket = AsyncMock()
        ws.websocket = socket

        asyncio.run(ws.stop())

        socket.close.assert_awaited_once()
        self.assertIsNone(ws.websocket)

    def test_start_returns_task(self):
        """start() returns the supervisor task so the caller can retain/await it"""
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )

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


class TestWsPrivateAsyncConsumeErrorPropagation(unittest.TestCase):
    """Unit tests for consume() ConnectionClosedError handling (GH#116)"""

    def _make_ws(self):
        return WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL
        )

    def test_consume_propagates_connection_closed_and_pushes_error_event(self):
        """A dropped socket reaches the callback as an error event and re-raises"""
        from websockets.exceptions import ConnectionClosedError

        ws = self._make_ws()
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

        self.assertEqual(received[0], '{"data": "ok"}')
        error_payload = json.loads(received[1])
        self.assertEqual(error_payload["event"], "error")
        self.assertEqual(error_payload["code"], "ConnClosed")

    def test_consume_happy_path_unchanged(self):
        """Normal messages still reach the callback with no error event"""
        ws = self._make_ws()
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

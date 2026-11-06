"""
Unit tests for okxsdk.websocket.WsPrivateAsync module

Mirrors the structure: okxsdk/websocket/WsPrivateAsync.py -> test/unit/okxsdk/websocket/test_ws_private_async.py
"""
import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch

from okxsdk import consts
from okxsdk.websocket.WsPrivateAsync import WsPrivateAsync

from .fakes import FakeConnector, FakeSocket

# Test constants
TEST_WS_URL = 'wss://test.example.com'
ACK = '{"event":"login","code":"0"}'

# Placeholder client identifiers for constructing the websocket client in unit
# or sent over a real connection — they are not real credentials.
_STUB_ID = "test_api_key"
_STUB_SIGN = "test_secret_key"
_STUB_PHRASE = "test_passphrase"


def _session(*frames, **socket_kwargs):
    """A private session on a scripted socket. `start()` logs in first."""
    sock = FakeSocket(*frames, **socket_kwargs)
    ws = WsPrivateAsync(apiKey=_STUB_ID, passphrase=_STUB_PHRASE,
                        secretKey=_STUB_SIGN, url=TEST_WS_URL,
                        connector=FakeConnector(sock))
    return ws, sock


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
        ws = WsPrivateAsync(
            apiKey=_STUB_ID,
            passphrase=_STUB_PHRASE,
            secretKey=_STUB_SIGN,
            url=TEST_WS_URL,
            debug=True
        )

        self.assertTrue(ws.debug)

    def test_default_url_is_the_private_host(self):
        ws = WsPrivateAsync(apiKey=_STUB_ID, passphrase=_STUB_PHRASE, secretKey=_STUB_SIGN)
        self.assertEqual(ws.url, consts.WS_PRIVATE_URL)


class TestWsPrivateAsyncLogin(unittest.TestCase):
    """The login frame is built by the shared primitive, not by a copy here."""

    def test_login_goes_through_the_shared_payload_builder(self):
        payload = json.dumps({"op": "login", "args": []})

        async def run_test():
            ws, _ = _session(answer_login=ACK)
            await ws.start()
            await ws.stop()

        with patch("okxsdk.websocket.WsBaseAsync.login_payload",
                   return_value=payload) as build:
            asyncio.run(run_test())

        build.assert_called_once()


class TestWsPrivateAsyncSubscribe(unittest.TestCase):
    """Unit tests for WsPrivateAsync subscribe method"""

    def test_subscribe_sends_correct_payload(self):
        """Test subscribe sends correct payload after login"""
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            await ws.subscribe(params, callback)
            # The callback belongs to this arg; the fallback is untouched.
            self.assertIsNone(ws.callback)
            await ws._on_frame(json.dumps({"arg": params[0], "data": []}))
            callback.assert_called_once()
            # First frame is the login the session sent at start().
            self.assertEqual([p["op"] for p in sock.payloads], ["login", "subscribe"])
            payload = sock.payloads[1]
            self.assertEqual(payload["args"], params)
            self.assertNotIn("id", payload)
            await ws.stop()

        asyncio.run(run_test())

    def test_subscribe_with_id(self):
        """Test subscribe with id parameter"""
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            await ws.subscribe(params, callback, id="sub001")
            payload = sock.payloads[1]
            self.assertEqual(payload["op"], "subscribe")
            self.assertEqual(payload["id"], "sub001")
            await ws.stop()

        asyncio.run(run_test())


class TestWsPrivateAsyncUnsubscribe(unittest.TestCase):
    """Unit tests for WsPrivateAsync unsubscribe method"""

    def test_unsubscribe_sends_correct_payload(self):
        """Test unsubscribe sends correct payload"""
        callback = MagicMock()
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
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
        params = [{"channel": "account", "ccy": "BTC"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            await ws.unsubscribe(params, callback, id="unsub001")
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "unsubscribe")
            self.assertEqual(payload["id"], "unsub001")
            await ws.stop()

        asyncio.run(run_test())


class TestWsPrivateAsyncSend(unittest.TestCase):
    """Unit tests for WsPrivateAsync generic send method"""

    def test_send_without_id(self):
        """Test generic send method without id"""
        callback = MagicMock()
        args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
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
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            await ws.send("custom_op", args, id="send001")
            payload = sock.payloads[-1]
            self.assertEqual(payload["op"], "custom_op")
            self.assertEqual(payload["id"], "send001")
            await ws.stop()

        asyncio.run(run_test())


# method name -> op the private client sends for it
ORDER_METHODS = [
    ("place_order", "order"),
    ("batch_orders", "batch-orders"),
    ("cancel_order", "cancel-order"),
    ("batch_cancel_orders", "batch-cancel-orders"),
    ("amend_order", "amend-order"),
    ("batch_amend_orders", "batch-amend-orders"),
    ("mass_cancel", "mass-cancel"),
]


class TestWsPrivateAsyncOrderMethods(unittest.TestCase):
    """Unit tests for WsPrivateAsync order-related methods"""

    def test_each_method_sends_its_op_with_id(self):
        args = [{"instId": "BTC-USDT", "ordId": "12345"}]
        for name, op in ORDER_METHODS:
            with self.subTest(method=name):
                callback = MagicMock()

                async def run_test():
                    ws, sock = _session(answer_login=ACK)
                    await ws.start()
                    await getattr(ws, name)(args, callback=callback, id="req001")
                    payload = sock.payloads[-1]
                    self.assertEqual(payload["op"], op)
                    self.assertEqual(payload["args"], args)
                    self.assertEqual(payload["id"], "req001")
                    await ws.stop()

                asyncio.run(run_test())

    def test_each_method_without_id_omits_it(self):
        args = [{"instId": "BTC-USDT"}]
        for name, op in ORDER_METHODS:
            with self.subTest(method=name):
                async def run_test():
                    ws, sock = _session(answer_login=ACK)
                    await ws.start()
                    await getattr(ws, name)(args)
                    payload = sock.payloads[-1]
                    self.assertEqual(payload["op"], op)
                    self.assertNotIn("id", payload)
                    await ws.stop()

                asyncio.run(run_test())

    def test_an_order_ack_is_matched_by_id(self):
        order_args = [{"instId": "BTC-USDT"}]

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            routed = []
            await ws.place_order(order_args, callback=routed.append, id="order001")
            # An order acknowledgement carries no arg; its id finds the callback.
            self.assertIsNone(ws.callback)
            await ws._on_frame(json.dumps({"id": "order001", "op": "order", "data": []}))
            await ws.stop()
            return routed

        self.assertEqual(len(asyncio.run(run_test())), 1)


class TestWsPrivateAsyncLogin(unittest.TestCase):
    """Unit tests for WsPrivateAsync login method"""

    def test_start_logs_in_before_anything_else(self):
        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            logged_in = ws.isLoggedIn
            await ws.stop()
            return logged_in, sock.payloads

        logged_in, payloads = asyncio.run(run_test())
        self.assertTrue(logged_in)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]["op"], "login")
        self.assertEqual(payloads[0]["args"][0]["apiKey"], _STUB_ID)


class TestWsPrivateAsyncStartStop(unittest.TestCase):
    """Unit tests for WsPrivateAsync start and stop methods"""

    def test_stop_closes_the_socket(self):
        """stop() closes the one socket the supervisor holds"""

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            await ws.start()
            await ws.stop()
            return ws, sock

        ws, sock = asyncio.run(run_test())
        self.assertTrue(sock.closed)
        self.assertIsNone(ws.websocket)

    def test_start_returns_task(self):
        """start() returns the supervisor task so the caller can retain/await it"""

        async def run_test():
            ws, sock = _session(answer_login=ACK)
            task = await ws.start()
            self.assertIsInstance(task, asyncio.Task)
            await ws.stop()

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()

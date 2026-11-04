"""
Unit tests for the WebSocket correctness fixes

Mirrors: okx/websocket/WsUtils.py, WebSocketFactory.py, Ws*Async.login
"""
import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from okx.websocket import WsUtils
from okx.websocket.WebSocketFactory import WebSocketFactory
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync

ACK = '{"event":"login","code":"0"}'
REJECT = '{"event":"login","code":"60009","msg":"Login failed"}'


class TestIsNotBlankStr(unittest.TestCase):
    def test_blank_strings_are_blank(self):
        self.assertFalse(WsUtils.isNotBlankStr(""))
        self.assertFalse(WsUtils.isNotBlankStr("   "))

    def test_non_strings_are_blank(self):
        self.assertFalse(WsUtils.isNotBlankStr(None))
        self.assertFalse(WsUtils.isNotBlankStr(123))

    def test_real_value_is_not_blank(self):
        self.assertTrue(WsUtils.isNotBlankStr("trades"))

    def test_check_socket_params_rejects_blank_channel(self):
        with self.assertRaises(ValueError):
            WsUtils.checkSocketParams([{"channel": "   "}], {}, {})


class TestFactoryPropagatesErrors(unittest.TestCase):
    def test_connect_error_is_raised_not_swallowed(self):
        factory = WebSocketFactory('wss://example.com')
        with patch('okx.websocket.WebSocketFactory.websockets.connect',
                   new=AsyncMock(side_effect=OSError('no route to host'))):
            with self.assertRaises(OSError):
                asyncio.run(factory.connect())


class _LoginSubject:
    """Build a client with a mocked socket, without touching the network."""

    def public(self, **kwargs):
        with patch('okx.websocket.WsBaseAsync.WebSocketFactory'):
            return WsPublicAsync(apiKey='k', passphrase='p', secretKey='s',
                                 url='wss://example.com', **kwargs)

    def private(self, **kwargs):
        with patch('okx.websocket.WsBaseAsync.WebSocketFactory'):
            return WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s',
                                  url='wss://example.com', **kwargs)


class TestLoginAck(unittest.TestCase):
    def _ws(self, klass):
        ws = _LoginSubject().public() if klass is WsPublicAsync else _LoginSubject().private()
        ws.websocket = AsyncMock()
        return ws

    def test_public_login_succeeds_on_ack(self):
        ws = self._ws(WsPublicAsync)
        ws.websocket.recv = AsyncMock(return_value=ACK)
        self.assertTrue(asyncio.run(ws.login()))
        self.assertTrue(ws.isLoggedIn)

    def test_public_login_raises_on_rejection(self):
        ws = self._ws(WsPublicAsync)
        ws.websocket.recv = AsyncMock(return_value=REJECT)
        with self.assertRaises(ConnectionError) as ctx:
            asyncio.run(ws.login())
        self.assertIn('60009', str(ctx.exception))
        self.assertFalse(ws.isLoggedIn)

    def test_private_login_raises_on_rejection(self):
        ws = self._ws(WsPrivateAsync)
        ws.websocket.recv = AsyncMock(return_value=REJECT)
        with self.assertRaises(ConnectionError):
            asyncio.run(ws.login())

    def test_login_times_out_without_an_ack(self):
        ws = self._ws(WsPublicAsync)
        ws.websocket.recv = AsyncMock(return_value='{"event":"subscribe"}')
        with self.assertRaises(TimeoutError):
            asyncio.run(ws.login(timeout=0.05))

    def test_non_login_frames_reach_the_callback(self):
        ws = self._ws(WsPublicAsync)
        received = []
        ws.callback = received.append
        ws.websocket.recv = AsyncMock(side_effect=['{"event":"notice"}', ACK])
        asyncio.run(ws.login())
        self.assertEqual(received, ['{"event":"notice"}'])

    def test_private_subscribe_does_not_sleep_after_the_ack(self):
        ws = self._ws(WsPrivateAsync)
        ws.websocket.recv = AsyncMock(return_value=ACK)
        with patch('okx.websocket.WsBaseAsync.WsUtils.initLoginParams', return_value='{"op":"login"}'):
            asyncio.run(ws.subscribe([{'channel': 'account'}], MagicMock()))
        self.assertEqual(ws.websocket.send.call_count, 2)

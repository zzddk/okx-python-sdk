"""
Unit tests for WebSocket endpoint defaults and Transport reuse

Mirrors: okx/consts/websocket.py, okx/websocket/*.py
"""
import asyncio
import unittest
from unittest.mock import patch

from okx import consts
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync

from ..fakes import mock_transport

PROXY = 'http://127.0.0.1:8080'


def _transport(flag='0', debug=False, proxy=None):
    return mock_transport(api_key='key', api_secret_key='secret',
                          passphrase='pass', flag=flag, debug=debug, proxy=proxy)


class TestConstants(unittest.TestCase):
    def test_endpoints_are_exported(self):
        for name in ('WS_PUBLIC_URL', 'WS_PRIVATE_URL', 'WS_BUSINESS_URL',
                     'WS_PUBLIC_DEMO_URL', 'WS_PRIVATE_DEMO_URL', 'WS_BUSINESS_DEMO_URL'):
            self.assertTrue(getattr(consts, name).startswith('wss://'))

    def test_demo_hosts_differ_from_live(self):
        self.assertNotEqual(consts.WS_PRIVATE_URL, consts.WS_PRIVATE_DEMO_URL)
        self.assertIn('wspap', consts.WS_PRIVATE_DEMO_URL)
        self.assertIn('brokerId=9999', consts.WS_PRIVATE_DEMO_URL)


class TestDefaultUrls(unittest.TestCase):
    def test_private_defaults_to_live(self):
        ws = WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s')
        self.assertEqual(ws.url, consts.WS_PRIVATE_URL)

    def test_public_defaults_to_live(self):
        ws = WsPublicAsync()
        self.assertEqual(ws.url, consts.WS_PUBLIC_URL)


class TestFromTransport(unittest.TestCase):
    def test_private_takes_credentials_from_the_transport(self):
        ws = WsPrivateAsync.from_transport(_transport())
        self.assertEqual((ws.apiKey, ws.passphrase, ws.secretKey), ('key', 'pass', 'secret'))

    def test_demo_flag_selects_the_demo_host(self):
        ws = WsPrivateAsync.from_transport(_transport(flag='1'))
        self.assertEqual(ws.url, consts.WS_PRIVATE_DEMO_URL)

    def test_live_flag_selects_the_live_host(self):
        ws = WsPrivateAsync.from_transport(_transport(flag='0'))
        self.assertEqual(ws.url, consts.WS_PRIVATE_URL)

    def test_debug_is_inherited(self):
        ws = WsPrivateAsync.from_transport(_transport(debug=True))
        self.assertTrue(ws.debug)

    def test_explicit_debug_wins(self):
        ws = WsPrivateAsync.from_transport(_transport(debug=False), debug=True)
        self.assertTrue(ws.debug)

    def test_explicit_url_wins(self):
        ws = WsPrivateAsync.from_transport(_transport(flag='1'), url='wss://example.com')
        self.assertEqual(ws.url, 'wss://example.com')

    def test_public_business_channel(self):
        ws = WsPublicAsync.from_transport(_transport(flag='1'), channel='business')
        self.assertEqual(ws.url, consts.WS_BUSINESS_DEMO_URL)

    def test_public_default_channel_is_public(self):
        ws = WsPublicAsync.from_transport(_transport())
        self.assertEqual(ws.url, consts.WS_PUBLIC_URL)

    def test_unknown_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            WsPublicAsync.from_transport(_transport(), channel='private')

    def test_private_rejects_a_non_transport(self):
        with self.assertRaises(TypeError) as ctx:
            WsPrivateAsync.from_transport(object())
        self.assertIn('Transport', str(ctx.exception))
        self.assertIn('object', str(ctx.exception))

    def test_public_rejects_a_non_transport(self):
        with self.assertRaises(TypeError) as ctx:
            WsPublicAsync.from_transport(object())
        self.assertIn('Transport', str(ctx.exception))
        self.assertIn('object', str(ctx.exception))


class TestProxyInheritance(unittest.TestCase):
    def test_connect_uses_the_proxy_recorded_on_the_transport(self):
        seen = {}

        async def connect(url, *, ssl=None, proxy=None):
            seen['url'] = url
            seen['proxy'] = proxy
            return object()

        ws = WsPrivateAsync.from_transport(_transport(proxy=PROXY))
        with patch('okx.websocket.connector.websockets.connect', new=connect):
            asyncio.run(ws.connect())

        self.assertEqual(seen['proxy'], PROXY)

    def test_injecting_http_does_not_detach_websocket_from_the_environment(self):
        """`http=` is a REST-only switch; without a proxy WS keeps websockets' default."""
        seen = {}

        async def connect(url, **kwargs):
            seen.update(kwargs)
            return object()

        ws = WsPublicAsync.from_transport(_transport())  # http= injected, no proxy
        with patch('okx.websocket.connector.websockets.connect', new=connect):
            asyncio.run(ws.connect())

        self.assertNotIn('proxy', seen)


if __name__ == '__main__':
    unittest.main()

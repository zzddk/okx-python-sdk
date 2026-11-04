"""
Unit tests for WebSocket endpoint defaults and REST-client reuse

Mirrors: okx/consts/websocket.py, okx/websocket/*.py
"""
import unittest
from types import SimpleNamespace

from okx import consts
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync


def _rest_client(flag='0', debug=False):
    return SimpleNamespace(
        API_KEY='key',
        API_SECRET_KEY='secret',
        PASSPHRASE='pass',
        flag=flag,
        debug=debug,
    )


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


class TestFromClient(unittest.TestCase):
    def test_private_takes_credentials_from_the_client(self):
        ws = WsPrivateAsync.from_client(_rest_client())
        self.assertEqual((ws.apiKey, ws.passphrase, ws.secretKey), ('key', 'pass', 'secret'))

    def test_demo_flag_selects_the_demo_host(self):
        ws = WsPrivateAsync.from_client(_rest_client(flag='1'))
        self.assertEqual(ws.url, consts.WS_PRIVATE_DEMO_URL)

    def test_live_flag_selects_the_live_host(self):
        ws = WsPrivateAsync.from_client(_rest_client(flag='0'))
        self.assertEqual(ws.url, consts.WS_PRIVATE_URL)

    def test_debug_is_inherited(self):
        ws = WsPrivateAsync.from_client(_rest_client(debug=True))
        self.assertTrue(ws.debug)

    def test_explicit_url_wins(self):
        ws = WsPrivateAsync.from_client(_rest_client(flag='1'), url='wss://example.com')
        self.assertEqual(ws.url, 'wss://example.com')

    def test_public_business_channel(self):
        ws = WsPublicAsync.from_client(_rest_client(flag='1'), channel='business')
        self.assertEqual(ws.url, consts.WS_BUSINESS_DEMO_URL)

    def test_public_default_channel_is_public(self):
        ws = WsPublicAsync.from_client(_rest_client())
        self.assertEqual(ws.url, consts.WS_PUBLIC_URL)

    def test_unknown_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            WsPublicAsync.from_client(_rest_client(), channel='private')

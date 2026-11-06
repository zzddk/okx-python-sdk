"""
Unit tests for WebSocket endpoint defaults and Transport reuse

Mirrors: okxsdk/consts/websocket.py, okxsdk/websocket/*.py
"""
import asyncio
import unittest
from unittest.mock import patch

from okxsdk import consts
from okxsdk.websocket.config import session_config
from okxsdk.websocket.WsPrivateAsync import WsPrivateAsync
from okxsdk.websocket.WsPublicAsync import WsPublicAsync

from ..fakes import mock_transport

from .fakes import FakeConnector, FakeSocket

PROXY = 'http://127.0.0.1:8080'

# An arbitrary host table: session_config only chooses between the two entries.
HOSTS = {False: 'wss://live.example', True: 'wss://demo.example'}


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


class TestSessionConfig(unittest.TestCase):
    def test_fields_come_from_the_transport(self):
        config = session_config(_transport(debug=True, proxy=PROXY), HOSTS)
        self.assertEqual(config, {
            'url': 'wss://live.example',
            'apiKey': 'key',
            'passphrase': 'pass',
            'secretKey': 'secret',
            'debug': True,
            'proxy': PROXY,
        })

    def test_demo_flag_selects_the_demo_host(self):
        config = session_config(_transport(flag='1'), HOSTS)
        self.assertEqual(config['url'], 'wss://demo.example')

    def test_no_credential_transport_yields_empty_ws_credentials(self):
        config = session_config(mock_transport(), HOSTS)
        self.assertEqual(
            (config['apiKey'], config['passphrase'], config['secretKey']),
            ('', '', ''))

    def test_url_overrides_the_host_table(self):
        config = session_config(_transport(flag='1'), HOSTS, url='wss://explicit.example')
        self.assertEqual(config['url'], 'wss://explicit.example')

    def test_explicit_debug_wins(self):
        config = session_config(_transport(debug=False), HOSTS, debug=True)
        self.assertTrue(config['debug'])

    def test_non_transport_is_rejected_with_the_argument_type(self):
        with self.assertRaises(TypeError) as ctx:
            session_config(object(), HOSTS)
        self.assertIn('Transport', str(ctx.exception))
        self.assertIn('object', str(ctx.exception))

    def test_client_host_tables_have_a_live_and_a_demo_entry(self):
        tables = [WsPrivateAsync._HOSTS, *WsPublicAsync._CHANNELS.values()]
        for hosts in tables:
            self.assertEqual(set(hosts), {False, True})
            self.assertNotEqual(hosts[False], hosts[True])


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

    def test_non_string_channel_is_rejected_as_value_error(self):
        for channel in ([], None, 1):
            with self.subTest(channel=channel):
                with self.assertRaises(ValueError) as ctx:
                    WsPublicAsync.from_transport(_transport(), channel=channel)
                self.assertIn("channel must be 'public' or 'business'", str(ctx.exception))

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


class TestNoCredentials(unittest.TestCase):
    """A Transport with no credentials must cross the seam as an absence.

    The REST side marks this with a sentinel; the WS side uses empty strings.
    Copying the sentinel verbatim makes `'-1'` look like three usable keys, so
    a private session tries to log in with it. See .scratch/no-credential-ws/spec.md
    and the Update in ADR-0014.
    """

    REJECT = '{"event":"login","code":"60009","msg":"Login failed"}'
    MESSAGE = 'apiKey, secretKey and passphrase are required for login'

    def _private(self):
        # `mock_transport()` has no credentials, i.e. all three fields are the
        # REST sentinel. Inject a scripted connector so start() never touches
        # the network and we can assert on what was actually sent.
        sock = FakeSocket(answer_login=self.REJECT)
        ws = WsPrivateAsync.from_transport(mock_transport())
        ws._connection.connector = FakeConnector(sock)
        return ws, sock

    def test_start_reports_missing_credentials_without_a_login_frame(self):
        ws, sock = self._private()

        async def run():
            with self.assertRaises(ValueError) as ctx:
                await ws.start()
            return str(ctx.exception)

        message = asyncio.run(run())
        self.assertIn(self.MESSAGE, message)
        self.assertNotIn('login', [p.get('op') for p in sock.payloads])
        # The error surfaced from the first _open(): no supervisor task was
        # created, so it cannot fall into _reconnect()'s retry loop.
        self.assertIsNone(ws._connection._task)

    def test_subscribe_reports_missing_credentials_before_start(self):
        ws, sock = self._private()

        async def run():
            with self.assertRaises(ValueError) as ctx:
                await ws.subscribe([{'channel': 'account'}])
            return str(ctx.exception)

        message = asyncio.run(run())
        self.assertIn(self.MESSAGE, message)
        self.assertEqual(sock.payloads, [])

    def test_public_channel_still_connects_without_credentials(self):
        # The bridge must not disturb a public session: it has no login to
        # perform, so an empty credential set changes nothing about it.
        sock = FakeSocket()
        ws = WsPublicAsync.from_transport(mock_transport())
        ws._connection.connector = FakeConnector(sock)

        async def run():
            await ws.start()
            try:
                return [p.get('op') for p in sock.payloads]
            finally:
                await ws.stop()

        self.assertEqual(asyncio.run(run()), [])


class TestProxyInheritance(unittest.TestCase):
    def _start_and_stop(self, ws):
        async def run():
            await ws.start()
            await ws.stop()
        asyncio.run(run())

    def test_start_uses_the_proxy_recorded_on_the_transport(self):
        seen = {}

        async def connect(url, *, ssl=None, proxy=None):
            seen['url'] = url
            seen['proxy'] = proxy
            return FakeSocket()

        ws = WsPublicAsync.from_transport(_transport(proxy=PROXY))
        with patch('okxsdk.websocket.connector.websockets.connect', new=connect):
            self._start_and_stop(ws)

        self.assertEqual(seen['url'], ws.url)
        self.assertEqual(seen['proxy'], PROXY)

    def test_injecting_http_does_not_detach_websocket_from_the_environment(self):
        """`http=` is a REST-only switch; without a proxy WS keeps websockets' default."""
        seen = {}

        async def connect(url, **kwargs):
            seen.update(kwargs)
            return FakeSocket()

        ws = WsPublicAsync.from_transport(_transport())  # http= injected, no proxy
        with patch('okxsdk.websocket.connector.websockets.connect', new=connect):
            self._start_and_stop(ws)

        self.assertNotIn('proxy', seen)


if __name__ == '__main__':
    unittest.main()

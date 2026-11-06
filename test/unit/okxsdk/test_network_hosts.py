"""Regression: network hosts must be the real OKX endpoints, not the SDK name.

The 0.17.0 import-package rename (4daa4c6) replaced ``okx`` with ``okxsdk``
everywhere, including the hostname literals in ``consts/http.py`` and
``consts/websocket.py``. Every REST and WebSocket request then went to
``*.okxsdk.com``. The tests at the time only asserted ``startswith('wss://')``
and ``'wspap' in ...``, so they stayed green.

This pins both the constants and the call sites that consume them, and adds a
guard so a future blind rename cannot silently retarget the SDK again.
"""
import unittest
from urllib.parse import urlparse

import httpx

from okxsdk import consts
from okxsdk.transport import Transport
from okxsdk.websocket.WsPrivateAsync import WsPrivateAsync
from okxsdk.websocket.WsPublicAsync import WsPublicAsync

EXPECTED_HOSTS = {
    'API_URL': 'https://www.okx.com',
    'WS_PUBLIC_URL': 'wss://ws.okx.com:8443/ws/v5/public',
    'WS_PRIVATE_URL': 'wss://ws.okx.com:8443/ws/v5/private',
    'WS_BUSINESS_URL': 'wss://ws.okx.com:8443/ws/v5/business',
    'WS_PUBLIC_DEMO_URL': 'wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999',
    'WS_PRIVATE_DEMO_URL': 'wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999',
    'WS_BUSINESS_DEMO_URL': 'wss://wspap.okx.com:8443/ws/v5/business?brokerId=9999',
}


class TestNetworkHostConstants(unittest.TestCase):
    def test_exact_okx_endpoints(self):
        for name, want in EXPECTED_HOSTS.items():
            with self.subTest(constant=name):
                self.assertEqual(getattr(consts, name), want)

    def test_no_network_host_contains_the_package_name(self):
        """A rename of the import package must never retarget the network."""
        urls = {name: value for name, value in vars(consts).items()
                if isinstance(value, str)
                and value.startswith(('http://', 'https://', 'ws://', 'wss://'))}
        self.assertTrue(set(EXPECTED_HOSTS).issubset(urls),
                        'an expected host constant is missing')
        for name, value in urls.items():
            with self.subTest(constant=name):
                self.assertNotIn('okxsdk', value)
                host = urlparse(value).hostname
                self.assertTrue(host == 'okx.com' or host.endswith('.okx.com'),
                                '%s points at %r' % (name, host))


class TestNetworkHostCallSites(unittest.TestCase):
    def test_default_transport_sends_rest_traffic_to_okx(self):
        seen = []

        def handler(request):
            seen.append(request.url.host)
            return httpx.Response(200, json={'code': '0'})

        Transport(http=httpx.MockTransport(handler)).request(
            consts.GET, '/api/v5/account/balance', {})
        self.assertEqual(seen, ['www.okx.com'])

    def test_default_ws_clients_target_okx_hosts(self):
        self.assertEqual(WsPublicAsync().url, EXPECTED_HOSTS['WS_PUBLIC_URL'])
        self.assertEqual(WsPrivateAsync('k', 'p', 's').url,
                         EXPECTED_HOSTS['WS_PRIVATE_URL'])

    def test_from_transport_targets_okx_hosts(self):
        self.assertEqual(WsPrivateAsync.from_transport(Transport(flag='0')).url,
                         EXPECTED_HOSTS['WS_PRIVATE_URL'])
        self.assertEqual(WsPrivateAsync.from_transport(Transport(flag='1')).url,
                         EXPECTED_HOSTS['WS_PRIVATE_DEMO_URL'])
        self.assertEqual(
            WsPublicAsync.from_transport(Transport(flag='1'), channel='business').url,
            EXPECTED_HOSTS['WS_BUSINESS_DEMO_URL'])


if __name__ == '__main__':
    unittest.main()

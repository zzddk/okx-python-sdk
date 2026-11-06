"""Contract tests for okx.transport.Transport.

Transport is the only module that knows httpx exists, so this is the one place
that may inject an httpx transport or assert on httpx.Client construction.

Mirrors: okx/transport.py -> test/unit/okx/test_transport.py
"""
import unittest
from unittest.mock import patch

import httpx

from okx import consts as c
from okx.Account import AccountAPI
from okx.Trade import TradeAPI
from okx.transport import Transport

MOCK_HTTP_CLIENT_INIT = 'okx.transport.httpx.Client.__init__'
TEST_PROXY_URL = 'http://proxy.example.com:8080'


class TestTransportProxy(unittest.TestCase):
    """`proxy=` is translated for both generations of the httpx signature."""

    def test_proxy_is_forwarded_to_httpx(self):
        with patch(MOCK_HTTP_CLIENT_INIT, return_value=None) as init:
            Transport(proxy=TEST_PROXY_URL)

        init.assert_called_once()
        self.assertEqual(init.call_args.kwargs['proxy'], TEST_PROXY_URL)

    def test_no_proxy_stays_none(self):
        with patch(MOCK_HTTP_CLIENT_INIT, return_value=None) as init:
            Transport()

        self.assertIsNone(init.call_args.kwargs.get('proxy'))

    def test_old_httpx_falls_back_to_proxies(self):
        with patch(MOCK_HTTP_CLIENT_INIT,
                   side_effect=[TypeError("unexpected keyword argument 'proxy'"), None]) as init:
            Transport(proxy=TEST_PROXY_URL)

        self.assertEqual(init.call_count, 2)
        self.assertEqual(
            init.call_args_list[1].kwargs['proxies'],
            {'http://': TEST_PROXY_URL, 'https://': TEST_PROXY_URL},
        )

    def test_proxy_is_readable_on_the_transport(self):
        """WS inherits the REST proxy from here, so the value stays on the object."""
        with patch(MOCK_HTTP_CLIENT_INIT, return_value=None):
            transport = Transport(proxy=TEST_PROXY_URL)
        self.assertEqual(transport.proxy, TEST_PROXY_URL)

    def test_no_proxy_is_none(self):
        with patch(MOCK_HTTP_CLIENT_INIT, return_value=None):
            transport = Transport()
        self.assertIsNone(transport.proxy)

    def test_proxy_is_recorded_when_an_http_transport_is_injected(self):
        transport = Transport(http=httpx.MockTransport(
            lambda request: httpx.Response(200, json={'code': '0'})
        ), proxy=TEST_PROXY_URL)
        self.assertEqual(transport.proxy, TEST_PROXY_URL)

    def test_old_httpx_without_proxy_retries_without_proxies(self):
        with patch(MOCK_HTTP_CLIENT_INIT,
                   side_effect=[TypeError("unexpected keyword argument 'proxy'"), None]) as init:
            Transport()

        self.assertEqual(init.call_count, 2)
        self.assertNotIn('proxies', init.call_args_list[1].kwargs)


class TestTransportEnvironment(unittest.TestCase):
    def test_explicit_http_transport_ignores_the_proxy_environment(self):
        """Injecting a transport means "I configured it myself" — no env lookup."""
        with patch.dict('os.environ', {'ALL_PROXY': 'socks5h://127.0.0.1:1'}):
            transport = Transport(http=httpx.MockTransport(
                lambda request: httpx.Response(200, json={'code': '0'})
            ))
            self.assertEqual(transport.request(c.GET, '/api/v5/test', {}), {'code': '0'})


class TestTransportSerialization(unittest.TestCase):
    def test_query_serializes_booleans_and_inlines_json(self):
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'code': '0'})

        transport = Transport(http=httpx.MockTransport(handler))
        transport.request(c.GET, '/api/v5/test',
                          {'reduceOnly': True, 'closeFraction': False, 'ids': [1, 2]})

        params = seen[0].url.params
        self.assertEqual(params['reduceOnly'], 'true')
        self.assertEqual(params['closeFraction'], 'false')
        self.assertEqual(params['ids'], '[1,2]')

    def test_none_params_send_no_arguments(self):
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'code': '0'})

        Transport(http=httpx.MockTransport(handler)).request(c.GET, '/api/v5/test', None)

        self.assertEqual(seen[0].url.query, b'')


FIXED_TS = '2020-01-01T00:00:00.000Z'
GET_PATH = '/api/v5/account/balance'
GET_QUERY = {'ccy': 'BTC'}
GET_SIGN = 'pZynVe0CTgbd68BxfwDK13LkoOLT3Z0TvdUm6ysFM1w='
POST_PATH = '/api/v5/trade/order'
POST_PARAMS = {'instId': 'BTC-USDT', 'sz': '1'}
POST_BODY = b'{"instId": "BTC-USDT", "sz": "1"}'
POST_SIGN = 'KGSgkgbrvFrIj20Kw8xJ0asjk4EcSaD9E55zn+vK7hI='


def _signed_transport(handler):
    return Transport(api_key='key', api_secret_key='secret', passphrase='pass',
                     flag='0', http=httpx.MockTransport(handler))


class TestTransportSigning(unittest.TestCase):
    """The one path that authenticates a request: fixed vectors, no live API."""

    def test_get_signs_the_method_path_and_query(self):
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'code': '0'})

        with patch('okx.utils.get_timestamp', return_value=FIXED_TS):
            _signed_transport(handler).request(c.GET, GET_PATH, GET_QUERY)

        headers = seen[0].headers
        self.assertEqual(headers['OK-ACCESS-KEY'], 'key')
        self.assertEqual(headers['OK-ACCESS-TIMESTAMP'], FIXED_TS)
        self.assertEqual(headers['OK-ACCESS-PASSPHRASE'], 'pass')
        self.assertEqual(headers['OK-ACCESS-SIGN'], GET_SIGN)
        self.assertEqual(headers['x-simulated-trading'], '0')
        self.assertEqual(seen[0].url.path, GET_PATH)
        self.assertEqual(seen[0].url.query, b'ccy=BTC')

    def test_post_signs_the_exact_body_it_sends(self):
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'code': '0'})

        with patch('okx.utils.get_timestamp', return_value=FIXED_TS):
            _signed_transport(handler).request(c.POST, POST_PATH, POST_PARAMS)

        self.assertEqual(seen[0].headers['OK-ACCESS-SIGN'], POST_SIGN)
        self.assertEqual(seen[0].content, POST_BODY)


class TestSharedConnectionPool(unittest.TestCase):
    def test_api_classes_share_one_connection_pool(self):
        """`client=` fans one pool out instead of building one per API class."""
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'code': '0'})

        shared = Transport(http=httpx.MockTransport(handler))
        trade = TradeAPI(shared)
        account = AccountAPI(shared)

        self.assertIs(trade._t, shared)
        self.assertIs(account._t, shared)

        trade.request(c.GET, '/api/v5/trade/orders', {})
        account.request(c.GET, '/api/v5/account/balance', {})
        self.assertEqual(len(seen), 2)

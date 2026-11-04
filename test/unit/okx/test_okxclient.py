"""
Unit tests for okx.okxclient module

Mirrors the structure: okx/okxclient.py -> test/unit/okx/test_okxclient.py
"""
import json
import unittest
import warnings
from unittest.mock import MagicMock, patch

import httpx

from okx import exceptions

# Test constants
MOCK_CLIENT_INIT = 'okx.okxclient.Client.__init__'
TEST_PROXY_URL = 'http://proxy.example.com:8080'
TEST_API_ENDPOINT = '/api/v5/test'


class TestOkxClientInit(unittest.TestCase):
    """Unit tests for OkxClient initialization"""

    def test_init_with_default_parameters(self):
        """Test initialization with default parameters"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            
            from okx.okxclient import OkxClient
            client = OkxClient()

            self.assertEqual(client.API_KEY, '-1')
            self.assertEqual(client.API_SECRET_KEY, '-1')
            self.assertEqual(client.PASSPHRASE, '-1')
            self.assertEqual(client.flag, '1')
            self.assertFalse(client.debug)

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            
            from okx.okxclient import OkxClient
            client = OkxClient(
                api_key='test_key',
                api_secret_key='test_secret',
                passphrase='test_pass',
                flag='0',
                debug=True
            )

            self.assertEqual(client.API_KEY, 'test_key')
            self.assertEqual(client.API_SECRET_KEY, 'test_secret')
            self.assertEqual(client.PASSPHRASE, 'test_pass')
            self.assertEqual(client.flag, '0')
            self.assertTrue(client.debug)

    def test_use_server_time_warns_that_it_has_no_effect(self):
        """The deprecated parameter stays accepted but no longer fails silently"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None

            from okx.okxclient import OkxClient

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                OkxClient(use_server_time=True)

        self.assertEqual(len(caught), 1)
        self.assertIs(caught[0].category, UserWarning)
        self.assertIn("has no effect", str(caught[0].message))


class TestOkxClientHttpxCompatibility(unittest.TestCase):
    """Unit tests for httpx version compatibility in OkxClient"""

    def test_init_with_new_httpx_proxy_parameter(self):
        """Test initialization with new httpx version using proxy parameter"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            # Simulate new httpx version (accepts proxy parameter)
            mock_init.return_value = None
            
            from okx.okxclient import OkxClient
            client = OkxClient(proxy=TEST_PROXY_URL)

            # Should call super().__init__ with proxy parameter
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args
            self.assertIn('proxy', call_kwargs.kwargs)
            self.assertEqual(call_kwargs.kwargs['proxy'], TEST_PROXY_URL)

    def test_init_with_old_httpx_falls_back_to_proxies(self):
        """Test initialization falls back to proxies for old httpx version"""
        call_count = [0]
        
        def mock_init_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1 and 'proxy' in kwargs:
                # First call with proxy parameter - simulate old httpx raising TypeError
                raise TypeError("__init__() got an unexpected keyword argument 'proxy'")
            # Second call should work (with proxies or without)
            return None

        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.side_effect = mock_init_side_effect
            
            from okx.okxclient import OkxClient
            client = OkxClient(proxy=TEST_PROXY_URL)

            # Should have been called twice
            self.assertEqual(mock_init.call_count, 2)
            
            # Second call should use proxies parameter
            second_call = mock_init.call_args_list[1]
            self.assertIn('proxies', second_call.kwargs)
            expected_proxies = {
                'http://': TEST_PROXY_URL,
                'https://': TEST_PROXY_URL
            }
            self.assertEqual(second_call.kwargs['proxies'], expected_proxies)

    def test_init_with_old_httpx_no_proxy(self):
        """Test initialization with old httpx version without proxy"""
        call_count = [0]
        
        def mock_init_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1 and 'proxy' in kwargs:
                # First call with proxy parameter - simulate old httpx raising TypeError
                raise TypeError("__init__() got an unexpected keyword argument 'proxy'")
            return None

        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.side_effect = mock_init_side_effect
            
            from okx.okxclient import OkxClient
            client = OkxClient()  # No proxy

            # Should have been called twice
            self.assertEqual(mock_init.call_count, 2)
            
            # Second call should not have proxies parameter
            second_call = mock_init.call_args_list[1]
            self.assertNotIn('proxies', second_call.kwargs)

    def test_init_without_proxy(self):
        """Test initialization without proxy parameter"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            
            from okx.okxclient import OkxClient
            client = OkxClient()

            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args.kwargs
            self.assertEqual(call_kwargs.get('proxy'), None)


class TestOkxClientRequest(unittest.TestCase):
    """Unit tests for OkxClient request methods"""

    def setUp(self):
        """Set up test fixtures"""
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            from okx.okxclient import OkxClient
            self.client = OkxClient(
                api_key='test_key',
                api_secret_key='test_secret',
                passphrase='test_pass',
                flag='0'
            )

    def test_request_without_params(self):
        """Test _request_without_params calls _request with empty dict"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'code': '0'}
            
            result = self.client._request_without_params('GET', TEST_API_ENDPOINT)
            
            mock_request.assert_called_once_with('GET', TEST_API_ENDPOINT, {})

    def test_request_with_params(self):
        """Test _request_with_params passes params correctly"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'code': '0'}
            params = {'instId': 'BTC-USDT'}
            
            result = self.client._request_with_params('GET', TEST_API_ENDPOINT, params)
            
            mock_request.assert_called_once_with('GET', TEST_API_ENDPOINT, params)

    def test_post_body_omits_none_params(self):
        """Only None means "not supplied" in a JSON body."""
        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value = _mock_response({'code': '0'})

            result = self.client._request(
                'POST', TEST_API_ENDPOINT, {'instId': 'BTC-USDT', 'sz': None, 'px': ''}
            )

        body = json.loads(mock_post.call_args.kwargs['data'])
        self.assertEqual(body, {'instId': 'BTC-USDT', 'px': ''})
        self.assertEqual(result, {'code': '0'})

    def test_get_query_keeps_explicit_empty_string(self):
        """An explicit '' is a value, not an absent parameter."""
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value = _mock_response({'code': '0'})

            self.client._request('GET', TEST_API_ENDPOINT, {'instId': '', 'uly': None})

        mock_get.assert_called_once()
        self.assertTrue(mock_get.call_args.args[0].endswith('?instId='))


class TestSubclassConstructor(unittest.TestCase):
    """Subclasses inherit the base constructor instead of re-declaring it."""

    def test_subclass_accepts_keyword_arguments(self):
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            from okx.Trade import TradeAPI

            api = TradeAPI(api_key='k', api_secret_key='s', passphrase='p', flag='0')

        self.assertEqual(api.API_KEY, 'k')
        self.assertEqual(api.flag, '0')
        self.assertFalse(api.debug)

    def test_subclass_keeps_positional_argument_order(self):
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            from okx.Trade import TradeAPI

            api = TradeAPI('k', 's', 'p', False, '0')

        self.assertEqual(api.API_KEY, 'k')
        self.assertEqual(api.API_SECRET_KEY, 's')
        self.assertEqual(api.PASSPHRASE, 'p')
        self.assertEqual(api.flag, '0')

    def test_base_api_keyword_sets_domain(self):
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            from okx.Trade import TradeAPI

            api = TradeAPI(base_api='https://example.test')

        self.assertEqual(api.domain, 'https://example.test')

    def test_shared_client_reuses_credentials_and_requests(self):
        with patch(MOCK_CLIENT_INIT) as mock_init:
            mock_init.return_value = None
            from okx.okxclient import OkxClient
            from okx.Trade import TradeAPI

            shared = OkxClient(api_key='k', api_secret_key='s', passphrase='p', flag='0')
            api = TradeAPI(client=shared)

        self.assertEqual(api.API_KEY, 'k')
        self.assertEqual(api.flag, '0')

        shared._request = MagicMock(return_value={'code': '0'})
        result = api._request('GET', TEST_API_ENDPOINT, {})

        shared._request.assert_called_once_with('GET', TEST_API_ENDPOINT, {})
        self.assertEqual(result, {'code': '0'})


def _mock_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = str(payload)
    return response


class TestOkxClientErrorHandling(unittest.TestCase):
    """Business and HTTP errors raise OkxAPIException by default."""

    def setUp(self):
        with patch('okx.okxclient.Client.__init__') as mock_init:
            mock_init.return_value = None
            from okx.okxclient import OkxClient
            self.client = OkxClient()

    def test_success_response_is_returned(self):
        payload = {'code': '0', 'data': []}
        with patch.object(self.client, 'get', return_value=_mock_response(payload)):
            self.assertEqual(
                self.client._request_with_params('GET', '/api/v5/test', {}), payload
            )

    def test_business_error_raises_with_code_and_message(self):
        payload = {'code': '51000', 'msg': 'Order rejected'}
        with patch.object(self.client, 'get', return_value=_mock_response(payload)):
            with self.assertRaises(exceptions.OkxAPIException) as ctx:
                self.client._request_with_params('GET', '/api/v5/test', {})

        error = ctx.exception
        self.assertEqual(error.code, '51000')
        self.assertEqual(error.message, 'Order rejected')
        self.assertEqual(error.status_code, 200)
        self.assertIsNotNone(error.response)

    def test_http_error_raises_with_status_code(self):
        payload = {'code': '50011', 'msg': 'Rate limit'}
        with patch.object(
            self.client, 'get', return_value=_mock_response(payload, status_code=500)
        ):
            with self.assertRaises(exceptions.OkxAPIException) as ctx:
                self.client._request_with_params('GET', '/api/v5/test', {})

        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(ctx.exception.code, '50011')

    def test_raise_on_error_false_returns_payload_unchanged(self):
        payload = {'code': '51000', 'msg': 'Order rejected'}
        with patch('okx.okxclient.Client.__init__') as mock_init:
            mock_init.return_value = None
            from okx.okxclient import OkxClient
            client = OkxClient(raise_on_error=False)

        with patch.object(client, 'get', return_value=_mock_response(payload, status_code=500)):
            self.assertEqual(
                client._request_with_params('GET', '/api/v5/test', {}), payload
            )

    def test_network_errors_are_not_wrapped(self):
        with patch.object(self.client, 'get', side_effect=httpx.ConnectError('boom')):
            with self.assertRaises(httpx.ConnectError):
                self.client._request_with_params('GET', '/api/v5/test', {})

    def test_http_error_with_non_json_body_raises_okx_exception(self):
        response = MagicMock()
        response.status_code = 502
        response.text = '<html>bad gateway</html>'
        response.json.side_effect = ValueError('not json')

        with patch.object(self.client, 'get', return_value=response):
            with self.assertRaises(exceptions.OkxAPIException) as ctx:
                self.client._request_with_params('GET', '/api/v5/test', {})

        self.assertEqual(ctx.exception.status_code, 502)
        self.assertIn('bad gateway', ctx.exception.message)

    def test_200_non_json_body_still_raises_value_error(self):
        response = MagicMock()
        response.status_code = 200
        response.text = 'not json'
        response.json.side_effect = ValueError('not json')

        with patch.object(self.client, 'get', return_value=response):
            with self.assertRaises(ValueError):
                self.client._request_with_params('GET', '/api/v5/test', {})


if __name__ == '__main__':
    unittest.main()

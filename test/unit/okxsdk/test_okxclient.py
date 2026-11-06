"""
Unit tests for okxsdk.okxclient module

Mirrors the structure: okxsdk/okxclient.py -> test/unit/okxsdk/test_okxclient.py
"""
import json
import unittest
from unittest.mock import patch

import httpx

from okxsdk import exceptions
from okxsdk.okxclient import OkxClient
from okxsdk.Trade import TradeAPI
from okxsdk.transport import Transport

from .fakes import FakeTransport, mock_transport

TEST_API_ENDPOINT = '/api/v5/test'


class TestOkxClientInit(unittest.TestCase):
    """An API class takes one Transport and exposes it, but copies nothing."""

    CONFIGURATION = ('API_KEY', 'API_SECRET_KEY', 'PASSPHRASE', 'flag', 'debug',
                     'domain', 'raise_on_error', 'max_retries', 'retry_backoff')

    def test_exposes_the_transport_it_was_given(self):
        transport = mock_transport(max_retries=3)
        client = OkxClient(transport)

        self.assertIs(client.transport, transport)
        self.assertEqual(client.transport.max_retries, 3)

    def test_configuration_is_not_copied_onto_the_client(self):
        """One configuration surface: read it from api.transport."""
        client = OkxClient(mock_transport())
        for name in self.CONFIGURATION:
            with self.subTest(name=name):
                self.assertFalse(hasattr(client, name))

    def test_non_transport_is_rejected(self):
        with self.assertRaises(TypeError):
            OkxClient(object())

    def test_removed_use_server_time_is_rejected(self):
        """The dead parameter is gone instead of silently accepted"""
        with self.assertRaises(TypeError):
            OkxClient(mock_transport(), use_server_time=True)


class TestRequest(unittest.TestCase):
    """`request` is the single seam every endpoint method funnels through."""

    def setUp(self):
        self.requests = []

        def handler(request):
            self.requests.append(request)
            return httpx.Response(200, json={'code': '0'})

        self.client = OkxClient(mock_transport(handler))

    def test_params_default_to_none(self):
        result = self.client.request('GET', TEST_API_ENDPOINT)

        self.assertEqual(result, {'code': '0'})
        self.assertEqual(self.requests[-1].url.query, b'')

    def test_request_passes_params_and_replayability_to_the_transport(self):
        params = {'instId': 'BTC-USDT'}
        with patch.object(self.client._t, 'request', return_value={'code': '0'}) as send:
            self.client.request('GET', TEST_API_ENDPOINT, params, replayable=True)

        send.assert_called_once_with('GET', TEST_API_ENDPOINT, params, replayable=True)

    def test_post_body_omits_none_params(self):
        """Only None means "not supplied" in a JSON body."""
        result = self.client.request(
            'POST', TEST_API_ENDPOINT, {'instId': 'BTC-USDT', 'sz': None, 'px': ''}
        )

        body = json.loads(self.requests[-1].content)
        self.assertEqual(body, {'instId': 'BTC-USDT', 'px': ''})
        self.assertEqual(result, {'code': '0'})

    def test_get_query_keeps_explicit_empty_string(self):
        """An explicit '' is a value, not an absent parameter."""
        self.client.request('GET', TEST_API_ENDPOINT, {'instId': '', 'uly': None})

        self.assertTrue(str(self.requests[-1].url).endswith('?instId='))


class TestApiConstruction(unittest.TestCase):
    """API classes receive a Transport; the old configuration keywords are gone."""

    def test_api_class_takes_a_transport_positionally(self):
        transport = mock_transport(api_key='k', api_secret_key='s',
                                    passphrase='p', flag='0')
        api = TradeAPI(transport)

        self.assertIs(api._t, transport)
        self.assertIs(api.transport, transport)

    def test_api_keys_are_no_longer_constructor_arguments(self):
        with self.assertRaises(TypeError):
            TradeAPI(api_key='k', api_secret_key='s', passphrase='p')

    def test_client_keyword_is_gone(self):
        with self.assertRaises(TypeError):
            TradeAPI(client=OkxClient(mock_transport()))

    def test_domain_comes_from_the_transport(self):
        api = TradeAPI(Transport(base_api='https://example.test',
                                 http=httpx.MockTransport(lambda request: httpx.Response(200))))
        self.assertEqual(api.transport.domain, 'https://example.test')


def _mock_response(payload, status_code=200):
    return httpx.Response(status_code, json=payload)


class TestOkxClientErrorHandling(unittest.TestCase):
    """Business and HTTP errors raise OkxAPIException by default."""

    def _client(self, handler, **config):
        return OkxClient(mock_transport(handler, **config))

    def test_success_response_is_returned(self):
        payload = {'code': '0', 'data': []}
        client = self._client(lambda request: _mock_response(payload))
        self.assertEqual(client.request('GET', '/api/v5/test', {}), payload)

    def test_business_error_raises_with_code_and_message(self):
        payload = {'code': '51000', 'msg': 'Order rejected'}
        client = self._client(lambda request: _mock_response(payload))
        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request('GET', '/api/v5/test', {})

        error = ctx.exception
        self.assertEqual(error.code, '51000')
        self.assertEqual(error.message, 'Order rejected')
        self.assertEqual(error.status_code, 200)
        self.assertIsNotNone(error.response)

    def test_http_error_raises_with_status_code(self):
        payload = {'code': '50011', 'msg': 'Rate limit'}
        client = self._client(lambda request: _mock_response(payload, status_code=500))
        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request('GET', '/api/v5/test', {})

        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(ctx.exception.code, '50011')

    def test_raise_on_error_false_returns_payload_unchanged(self):
        payload = {'code': '51000', 'msg': 'Order rejected'}
        client = self._client(
            lambda request: _mock_response(payload, status_code=500), raise_on_error=False
        )
        self.assertEqual(client.request('GET', '/api/v5/test', {}), payload)

    def test_network_errors_are_not_wrapped(self):
        def handler(request):
            raise httpx.ConnectError('boom')

        client = self._client(handler)
        with self.assertRaises(httpx.ConnectError):
            client.request('GET', '/api/v5/test', {})

    def test_http_error_with_non_json_body_raises_okx_exception(self):
        client = self._client(
            lambda request: httpx.Response(502, text='<html>bad gateway</html>')
        )
        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request('GET', '/api/v5/test', {})

        self.assertEqual(ctx.exception.status_code, 502)
        self.assertIn('bad gateway', ctx.exception.message)

    def test_200_non_json_body_still_raises_value_error(self):
        """`raise_on_error=False` has never swallowed an unparsable body."""
        client = self._client(lambda request: httpx.Response(200, text='not json'),
                              raise_on_error=False)
        with self.assertRaises(ValueError):
            client.request('GET', '/api/v5/test', {})


class TestClose(unittest.TestCase):
    def test_close_closes_the_transport(self):
        transport = FakeTransport()
        OkxClient(transport).close()
        self.assertTrue(transport.closed)

    def test_context_manager_closes_the_transport(self):
        transport = FakeTransport()
        with OkxClient(transport) as client:
            self.assertIsInstance(client, OkxClient)
        self.assertTrue(transport.closed)


if __name__ == '__main__':
    unittest.main()

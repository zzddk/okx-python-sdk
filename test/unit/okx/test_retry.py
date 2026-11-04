"""
Unit tests for retry and rate-limit behaviour in okx.okxclient

Mirrors the structure: okx/okxclient.py -> test/unit/okx/test_retry.py
"""
import unittest
from unittest.mock import MagicMock, patch

import httpx

from okx import consts as c
from okx import exceptions
from okx.okxclient import OkxClient
from okx.rate_limit import RateLimiter

MOCK_CLIENT_INIT = 'okx.okxclient.Client.__init__'
TEST_PATH = '/api/v5/trade/order'


def _response(status_code=200, payload=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload if payload is not None else {'code': '0', 'data': []}
    return response


class _ClientTestCase(unittest.TestCase):
    def _make(self, **kwargs):
        with patch(MOCK_CLIENT_INIT):
            return OkxClient(**kwargs)


class TestRetryDefaults(_ClientTestCase):
    def test_retries_are_off_by_default(self):
        client = self._make()
        self.assertEqual(client.max_retries, 0)
        self.assertIsNone(client._limiter)

    def test_get_is_not_retried_when_max_retries_is_zero(self):
        client = self._make()
        client.get = MagicMock(side_effect=httpx.ConnectError('boom'))
        with self.assertRaises(httpx.ConnectError):
            client._request(c.GET, TEST_PATH, {})
        self.assertEqual(client.get.call_count, 1)


class TestRetryTransportErrors(_ClientTestCase):
    def test_get_is_retried_after_a_transport_error(self):
        client = self._make(max_retries=2, retry_backoff=0)
        client.get = MagicMock(side_effect=[httpx.ConnectError('boom'), _response()])
        payload = client._request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(client.get.call_count, 2)

    def test_post_is_not_retried_without_an_idempotency_key(self):
        """A blind retry here would place the order twice."""
        client = self._make(max_retries=3, retry_backoff=0)
        client.post = MagicMock(side_effect=httpx.ConnectError('boom'))
        with self.assertRaises(httpx.ConnectError):
            client._request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'sz': '1'})
        self.assertEqual(client.post.call_count, 1)

    def test_post_is_retried_when_cl_ord_id_is_present(self):
        client = self._make(max_retries=1, retry_backoff=0)
        client.post = MagicMock(side_effect=[httpx.ConnectError('boom'), _response()])
        payload = client._request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'clOrdId': 'abc'})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(client.post.call_count, 2)

    def test_empty_idempotency_key_does_not_count(self):
        client = self._make(max_retries=2, retry_backoff=0)
        client.post = MagicMock(side_effect=httpx.ConnectError('boom'))
        with self.assertRaises(httpx.ConnectError):
            client._request(c.POST, TEST_PATH, {'clOrdId': ''})
        self.assertEqual(client.post.call_count, 1)

    def test_retries_stop_at_max_retries(self):
        client = self._make(max_retries=2, retry_backoff=0)
        client.get = MagicMock(side_effect=httpx.ConnectError('boom'))
        with self.assertRaises(httpx.ConnectError):
            client._request(c.GET, TEST_PATH, {})
        self.assertEqual(client.get.call_count, 3)


class TestRetryBusinessErrors(_ClientTestCase):
    def test_rate_limit_code_is_retried(self):
        client = self._make(max_retries=1, retry_backoff=0)
        client.get = MagicMock(side_effect=[
            _response(200, {'code': '50011', 'msg': 'Too Many Requests'}),
            _response(200, {'code': '0', 'data': []}),
        ])
        payload = client._request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(client.get.call_count, 2)

    def test_http_429_is_retried(self):
        client = self._make(max_retries=1, retry_backoff=0)
        client.get = MagicMock(side_effect=[
            _response(429, {'code': '0'}),
            _response(200, {'code': '0', 'data': []}),
        ])
        payload = client._request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')

    def test_definitional_rejection_is_not_retried(self):
        """51000 is a bad parameter: replaying it changes nothing."""
        client = self._make(max_retries=3, retry_backoff=0)
        client.post = MagicMock(return_value=_response(200, {'code': '51000', 'msg': 'Parameter error'}))
        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client._request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'sz': '1'})
        self.assertEqual(ctx.exception.code, '51000')
        self.assertEqual(client.post.call_count, 1)

    def test_raise_on_error_false_never_retries(self):
        client = self._make(max_retries=2, retry_backoff=0, raise_on_error=False)
        client.get = MagicMock(return_value=_response(200, {'code': '50011'}))
        payload = client._request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '50011')
        self.assertEqual(client.get.call_count, 1)


class TestBackoff(_ClientTestCase):
    def test_backoff_doubles_with_each_attempt(self):
        client = self._make(retry_backoff=0.5)
        with patch('okx.okxclient.time.sleep') as sleep:
            client._backoff(1)
            client._backoff(2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5, 1.0])


class TestRateLimiter(unittest.TestCase):
    def test_unknown_path_is_not_throttled(self):
        limiter = RateLimiter({'/x': (1, 10)})
        with patch('okx.rate_limit.time.sleep') as sleep:
            limiter.acquire('/y')
        sleep.assert_not_called()

    def test_calls_beyond_the_limit_wait(self):
        limiter = RateLimiter({'/x': (2, 10)})
        with patch('okx.rate_limit.time.sleep') as sleep, \
                patch('okx.rate_limit.time.monotonic', side_effect=[0, 0, 0, 10, 10]):
            limiter.acquire('/x')
            limiter.acquire('/x')
            limiter.acquire('/x')
        self.assertTrue(sleep.called)

    def test_client_shares_the_limiter(self):
        client = self._make_shared(rate_limit=True)
        with patch(MOCK_CLIENT_INIT):
            shared = OkxClient(client=client)
        self.assertIs(shared._limiter, client._limiter)

    def _make_shared(self, **kwargs):
        with patch(MOCK_CLIENT_INIT):
            return OkxClient(**kwargs)

"""
Unit tests for retry and rate-limit behaviour behind the transport seam

Mirrors the structure: okx/transport.py -> test/unit/okx/test_retry.py
"""
import unittest
from unittest.mock import MagicMock, patch

import httpx

from okx import consts as c
from okx import exceptions
from okx.okxclient import OkxClient
from okx.rate_limit import RateLimiter
from okx.transport import Transport

from .fakes import mock_transport

TEST_PATH = '/api/v5/trade/order'


def _response(status_code=200, payload=None):
    return httpx.Response(
        status_code, json=payload if payload is not None else {'code': '0', 'data': []}
    )


class _ClientTestCase(unittest.TestCase):
    def _make(self, responses, **config):
        """A client whose transport replays `responses`; exceptions are raised."""
        self.calls = []

        def handler(request):
            self.calls.append(request)
            item = responses[min(len(self.calls) - 1, len(responses) - 1)]
            if isinstance(item, Exception):
                raise item
            return item

        return OkxClient(mock_transport(handler, **config))


class TestRetryDefaults(_ClientTestCase):
    def test_retries_are_off_by_default(self):
        client = self._make([_response()])
        self.assertEqual(client.transport.max_retries, 0)
        self.assertIsNone(client._t._limiter)
        self.assertTrue(client.transport.raise_on_error)

    def test_get_is_not_retried_when_max_retries_is_zero(self):
        client = self._make([httpx.ConnectError('boom')])
        with self.assertRaises(httpx.ConnectError):
            client.request(c.GET, TEST_PATH, {})
        self.assertEqual(len(self.calls), 1)


class TestRetryTransportErrors(_ClientTestCase):
    def test_get_is_retried_after_a_transport_error(self):
        client = self._make([httpx.ConnectError('boom'), _response()],
                            max_retries=2, retry_backoff=0)
        payload = client.request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(len(self.calls), 2)

    def test_post_is_not_retried_without_an_idempotency_key(self):
        """A blind retry here would place the order twice."""
        client = self._make([httpx.ConnectError('boom')], max_retries=3, retry_backoff=0)
        with self.assertRaises(httpx.ConnectError):
            client.request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'sz': '1'})
        self.assertEqual(len(self.calls), 1)

    def test_post_is_retried_when_cl_ord_id_is_present(self):
        client = self._make([httpx.ConnectError('boom'), _response()],
                            max_retries=1, retry_backoff=0)
        payload = client.request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'clOrdId': 'abc'})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(len(self.calls), 2)

    def test_empty_idempotency_key_does_not_count(self):
        client = self._make([httpx.ConnectError('boom')], max_retries=2, retry_backoff=0)
        with self.assertRaises(httpx.ConnectError):
            client.request(c.POST, TEST_PATH, {'clOrdId': ''})
        self.assertEqual(len(self.calls), 1)

    def test_retries_stop_at_max_retries(self):
        client = self._make([httpx.ConnectError('boom')], max_retries=2, retry_backoff=0)
        with self.assertRaises(httpx.ConnectError):
            client.request(c.GET, TEST_PATH, {})
        self.assertEqual(len(self.calls), 3)


class TestRetryBusinessErrors(_ClientTestCase):
    def test_rate_limit_code_is_retried(self):
        client = self._make([
            _response(200, {'code': '50011', 'msg': 'Too Many Requests'}),
            _response(200, {'code': '0', 'data': []}),
        ], max_retries=1, retry_backoff=0)
        payload = client.request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(len(self.calls), 2)

    def test_http_429_is_retried(self):
        client = self._make([
            _response(429, {'code': '0'}),
            _response(200, {'code': '0', 'data': []}),
        ], max_retries=1, retry_backoff=0)
        payload = client.request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '0')
        self.assertEqual(len(self.calls), 2)

    def test_definitional_rejection_is_not_retried(self):
        """51000 is a bad parameter: replaying it changes nothing."""
        client = self._make([
            _response(200, {'code': '51000', 'msg': 'Parameter error'}),
        ], max_retries=3, retry_backoff=0)
        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request(c.POST, TEST_PATH, {'instId': 'BTC-USDT', 'sz': '1'})
        self.assertEqual(ctx.exception.code, '51000')
        self.assertEqual(len(self.calls), 1)

    def test_raise_on_error_false_never_retries(self):
        client = self._make([_response(200, {'code': '50011'})],
                            max_retries=2, retry_backoff=0, raise_on_error=False)
        payload = client.request(c.GET, TEST_PATH, {})
        self.assertEqual(payload['code'], '50011')
        self.assertEqual(len(self.calls), 1)


class TestRetryNonJsonErrors(_ClientTestCase):
    """A 429/5xx body that is not JSON must not escape the retry loop."""

    def test_replayable_request_retries_a_non_json_429(self):
        gateway = httpx.Response(429, text='<html>slow down</html>')
        client = self._make([gateway], max_retries=1, retry_backoff=0)

        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request(c.GET, TEST_PATH, {})

        self.assertEqual(ctx.exception.status_code, 429)
        self.assertEqual(len(self.calls), 2)

    def test_non_replayable_request_sends_once(self):
        gateway = httpx.Response(502, text='<html>bad gateway</html>')
        client = self._make([gateway], max_retries=3, retry_backoff=0)

        with self.assertRaises(exceptions.OkxAPIException) as ctx:
            client.request(c.POST, TEST_PATH, {'instId': 'BTC-USDT'})

        self.assertEqual(ctx.exception.status_code, 502)
        self.assertEqual(len(self.calls), 1)


class TestBackoff(_ClientTestCase):
    def test_backoff_doubles_with_each_attempt(self):
        client = self._make([_response()], retry_backoff=0.5)
        with patch('okx.transport.time.sleep') as sleep:
            client._t._backoff(1)
            client._t._backoff(2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5, 1.0])


class TestRateLimiter(unittest.TestCase):
    def test_unknown_path_is_not_throttled(self):
        sleep = MagicMock()
        limiter = RateLimiter({'/x': (1, 10)}, sleep=sleep)
        limiter.acquire('/y')
        sleep.assert_not_called()

    def test_calls_beyond_the_limit_wait(self):
        sleep = MagicMock()
        limiter = RateLimiter({'/x': (2, 10)}, sleep=sleep)
        with patch('okx.rate_limit.time.monotonic', side_effect=[0, 0, 0, 10, 10]):
            limiter.acquire('/x')
            limiter.acquire('/x')
            limiter.acquire('/x')
        self.assertTrue(sleep.called)
        self.assertGreater(sleep.call_args.args[0], 0)

    def test_client_shares_the_limiter(self):
        transport = Transport(rate_limit=True, http=httpx.MockTransport(
            lambda request: httpx.Response(200, json={'code': '0'})
        ))
        client = OkxClient(transport)
        shared = OkxClient(transport)
        self.assertIs(shared._t._limiter, client._t._limiter)
        self.assertIsNotNone(client._t._limiter)

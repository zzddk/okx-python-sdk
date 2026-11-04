"""Contract tests for okx.websocket.connector.WebSocketConnector.

The connector is the only module that talks to websockets, so this is the one
place that patches `websockets.connect` itself.
"""
import asyncio
import unittest
from unittest.mock import patch

from okx.websocket.connector import WebSocketConnector

URL = 'wss://example.com'
PROXY = 'http://127.0.0.1:8080'
CONNECT = 'okx.websocket.connector.websockets.connect'


class _Recorder:
    """Fake `websockets.connect` that records the keywords it receives."""

    def __init__(self, supports_proxy=True, error=None):
        self.calls = []
        self.error = error
        if supports_proxy:
            async def connect(url, *, ssl=None, proxy=None):
                self.calls.append({'url': url, 'ssl': ssl, 'proxy': proxy})
                if self.error is not None:
                    raise self.error
                return object()
        else:
            async def connect(url, *, ssl=None):
                self.calls.append({'url': url, 'ssl': ssl})
                if self.error is not None:
                    raise self.error
                return object()
        self.connect = connect


class _KeywordRecorder:
    """Fake whose signature accepts anything, so absence of `proxy` is visible."""

    def __init__(self):
        self.calls = []

    async def connect(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return object()


class TestProxyHandling(unittest.TestCase):
    def test_no_proxy_does_not_pass_proxy_at_all(self):
        """An explicit `proxy=None` would turn off websockets' env detection."""
        recorder = _KeywordRecorder()
        with patch(CONNECT, new=recorder.connect):
            asyncio.run(WebSocketConnector().connect(URL))

        url, kwargs = recorder.calls[0]
        self.assertEqual(url, URL)
        self.assertNotIn('proxy', kwargs)
        self.assertIsNotNone(kwargs['ssl'])

    def test_proxy_is_forwarded_when_the_signature_supports_it(self):
        """The probe reads the signature at connect() time, not at import."""
        connector = WebSocketConnector(proxy=PROXY)
        recorder = _Recorder(supports_proxy=True)
        with patch(CONNECT, new=recorder.connect):
            asyncio.run(connector.connect(URL))

        self.assertEqual(recorder.calls[0]['url'], URL)
        self.assertEqual(recorder.calls[0]['proxy'], PROXY)

    def test_proxy_without_signature_support_raises_before_connecting(self):
        """Silently connecting directly would leak traffic meant for the proxy."""
        recorder = _Recorder(supports_proxy=False)
        with patch(CONNECT, new=recorder.connect):
            with self.assertRaises(RuntimeError) as ctx:
                asyncio.run(WebSocketConnector(proxy=PROXY).connect(URL))

        message = str(ctx.exception)
        self.assertIn('websockets>=15.0', message)
        self.assertIn('connector=', message)
        self.assertEqual(recorder.calls, [])


class TestStatelessness(unittest.TestCase):
    def test_connect_does_not_remember_the_previous_socket(self):
        recorder = _Recorder()
        connector = WebSocketConnector()
        with patch(CONNECT, new=recorder.connect):
            first = asyncio.run(connector.connect(URL))
            second = asyncio.run(connector.connect(URL))

        self.assertIsNot(first, second)
        self.assertFalse(hasattr(connector, 'websocket'))
        self.assertFalse(hasattr(connector, 'close'))

    def test_public_surface_is_only_connect(self):
        public = [name for name in dir(WebSocketConnector) if not name.startswith('_')]
        self.assertEqual(public, ['connect'])


class TestErrorPropagation(unittest.TestCase):
    def test_connect_error_is_raised_not_swallowed(self):
        recorder = _Recorder(error=OSError('no route to host'))
        with patch(CONNECT, new=recorder.connect):
            with self.assertRaises(OSError):
                asyncio.run(WebSocketConnector().connect(URL))


if __name__ == '__main__':
    unittest.main()

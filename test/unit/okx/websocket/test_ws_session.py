"""
Unit tests for the shared WebSocket session: callback contract, heartbeat,
reconnect and subscription replay.

Mirrors: okx/websocket/WsBaseAsync.py
"""
import asyncio
import json
import unittest
from contextlib import suppress
from unittest.mock import AsyncMock, patch

from websockets.exceptions import ConnectionClosedError

from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync
from okx.websocket.connector import WebSocketConnector

from .fakes import FakeConnector

URL = 'wss://example.com'
ACK = '{"event":"login","code":"0"}'


def _public(**kwargs):
    kwargs.setdefault('url', URL)
    kwargs.setdefault('ping_interval', 0)
    return WsPublicAsync(**kwargs)


class _Messages:
    def __init__(self, *messages):
        self._messages = list(messages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        raise StopAsyncIteration


class _Socket:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send(self, payload):
        self.sent.append(payload)

    async def close(self):
        self.closed = True


class TestCallbackContract(unittest.TestCase):
    def test_async_callback_is_awaited_in_order(self):
        ws = _public()
        seen = []

        async def callback(message):
            await asyncio.sleep(0)
            seen.append(message)

        ws.callback = callback
        ws.websocket = _Messages('a', 'b')

        asyncio.run(ws.consume())
        self.assertEqual(seen, ['a', 'b'])

    def test_sync_callback_still_works(self):
        ws = _public()
        seen = []
        ws.callback = seen.append
        ws.websocket = _Messages('a')

        asyncio.run(ws.consume())
        self.assertEqual(seen, ['a'])

    def test_callback_exception_does_not_end_the_stream(self):
        ws = _public()
        seen = []

        async def callback(message):
            if message == 'boom':
                raise RuntimeError('callback failed')
            seen.append(message)

        ws.callback = callback
        ws.websocket = _Messages('boom', 'after')

        with patch('okx.websocket.WsBaseAsync.logger.exception') as log:
            asyncio.run(ws.consume())

        self.assertEqual(seen, ['after'])
        log.assert_called_once()

    def test_pong_is_not_delivered_and_sets_the_event(self):
        ws = _public()
        seen = []
        ws.callback = seen.append

        async def run():
            ws._pong = asyncio.Event()
            await ws._handle_message('pong')
            return ws._pong.is_set()

        self.assertTrue(asyncio.run(run()))
        self.assertEqual(seen, [])


class TestHeartbeat(unittest.TestCase):
    def test_ping_is_sent_and_missing_pong_closes_the_socket(self):
        async def run():
            ws = _public(ping_interval=0.01, ping_timeout=0.01)
            sock = _Socket()
            ws.websocket = sock
            ws._pong = asyncio.Event()
            await asyncio.wait_for(ws._heartbeat_loop(), timeout=1)
            return ws, sock

        ws, sock = asyncio.run(run())
        self.assertIn('ping', sock.sent)
        self.assertTrue(sock.closed)
        self.assertIsNone(ws.websocket)

    def test_pong_keeps_the_connection_open(self):
        async def run():
            ws = _public(ping_interval=0.01, ping_timeout=5)
            sock = _Socket()
            ws.websocket = sock
            ws._pong = asyncio.Event()
            task = asyncio.create_task(ws._heartbeat_loop())
            while not sock.sent:
                await asyncio.sleep(0.001)
            ws._pong.set()
            await asyncio.sleep(0.05)
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            return sock

        self.assertFalse(asyncio.run(run()).closed)


class _AckSocket:
    """Yields one scripted frame, then ends the stream."""

    def __init__(self, frame):
        self.frame = frame
        self.sent = []
        self._yielded = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._yielded:
            raise StopAsyncIteration
        self._yielded = True
        return self.frame

    async def send(self, payload):
        self.sent.append(payload)


class TestLoginThroughTheReader(unittest.TestCase):
    def _run(self, frame):
        async def run():
            ws = WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s',
                                url=URL, ping_interval=0, reconnect=False)
            ws.connect = AsyncMock()
            ws.websocket = _AckSocket(frame)
            task = await ws.start()
            await ws.login()
            await asyncio.wait_for(task, timeout=1)
            return ws

        return asyncio.run(run())

    def test_ack_is_delivered_by_the_running_reader(self):
        self.assertTrue(self._run(ACK).isLoggedIn)

    def test_rejection_is_delivered_by_the_running_reader(self):
        with self.assertRaises(ConnectionError):
            self._run('{"event":"login","code":"60009","msg":"Login failed"}')


class TestSubscriptionRegistry(unittest.TestCase):
    def test_subscribe_records_and_unsubscribe_removes(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            tickers = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            books = {'channel': 'books', 'instId': 'BTC-USDT'}
            await ws.subscribe([tickers], None)
            await ws.subscribe([dict(tickers)], None)  # duplicate is not stored twice
            await ws.subscribe([books], None)
            self.assertEqual(len(ws.subscriptions), 2)
            await ws.unsubscribe([tickers], None)
            self.assertEqual(list(ws.subscriptions.values()), [books])

        asyncio.run(run())

    def test_send_records_a_subscription(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            await ws.send('subscribe', [{'channel': 'tickers', 'instId': 'BTC-USDT'}])
            return ws.subscriptions

        self.assertEqual(len(asyncio.run(run())), 1)


class TestSessionRestore(unittest.TestCase):
    def test_public_replays_subscriptions(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            ws.subscriptions = {
                'a': {'channel': 'tickers', 'instId': 'BTC-USDT'},
                'b': {'channel': 'books', 'instId': 'ETH-USDT'},
            }
            await ws._restore_session()
            return [json.loads(call.args[0]) for call in ws.websocket.send.await_args_list]

        payloads = asyncio.run(run())
        self.assertEqual([p['op'] for p in payloads], ['subscribe', 'subscribe'])
        self.assertEqual(payloads[0]['args'], [{'channel': 'tickers', 'instId': 'BTC-USDT'}])

    def test_private_logs_in_then_replays_subscriptions(self):
        async def run():
            ws = WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s',
                                url=URL, ping_interval=0)
            ws.websocket = AsyncMock()
            ws.websocket.recv = AsyncMock(return_value=ACK)
            ws.subscriptions = {'a': {'channel': 'account'}}
            await ws._restore_session()
            return ws, [json.loads(call.args[0]) for call in ws.websocket.send.await_args_list]

        ws, payloads = asyncio.run(run())
        self.assertTrue(ws.isLoggedIn)
        self.assertEqual([p['op'] for p in payloads], ['login', 'subscribe'])


class _DroppingSocket:
    def __init__(self):
        self.drop = asyncio.Event()
        self.sent = []
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.drop.wait()
        raise ConnectionClosedError(None, None)

    async def send(self, payload):
        self.sent.append(payload)

    async def close(self):
        self.closed = True


class _IdleSocket:
    def __init__(self):
        self.release = asyncio.Event()
        self.sent = []
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.release.wait()
        raise StopAsyncIteration

    async def send(self, payload):
        self.sent.append(payload)

    async def close(self):
        self.closed = True


class TestConnectorChoice(unittest.TestCase):
    def test_injected_connector_wins_over_proxy_without_raising(self):
        """`connector` wins over `proxy`, the same rule as Transport(proxy=, http=)."""
        async def run():
            connector = FakeConnector(_Socket())
            ws = _public(proxy='http://127.0.0.1:1', connector=connector)
            await ws.connect()
            return ws, connector

        ws, connector = asyncio.run(run())
        self.assertIs(ws._connector, connector)
        self.assertEqual(connector.urls, [URL])

    def test_default_connector_is_built_from_the_proxy(self):
        ws = _public(proxy='http://127.0.0.1:8080')
        self.assertIsInstance(ws._connector, WebSocketConnector)


class TestStopFromCallback(unittest.TestCase):
    def test_stop_inside_a_callback_completes(self):
        async def run():
            ws = _public(ping_interval=0)
            ws.connect = AsyncMock()
            ws.websocket = _Messages('go')
            finished = []

            async def callback(message):
                await ws.stop()
                finished.append(message)

            ws.callback = callback
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return finished

        self.assertEqual(asyncio.run(run()), ['go'])


class TestReconnect(unittest.TestCase):
    def test_reconnects_and_replays_subscriptions(self):
        async def run():
            first, second = _DroppingSocket(), _IdleSocket()
            ws = _public(reconnect_backoff=0, ping_interval=0,
                         connector=FakeConnector(first, second))

            await ws.start()
            await ws.subscribe([{'channel': 'tickers', 'instId': 'BTC-USDT'}], None)
            first.drop.set()

            loop = asyncio.get_running_loop()
            deadline = loop.time() + 2
            while 'subscribe' not in [json.loads(p)['op'] for p in second.sent]:
                if loop.time() > deadline:
                    raise AssertionError(f'no resubscribe after reconnect: {second.sent}')
                await asyncio.sleep(0.01)

            await ws.stop()
            return first, second

        first, second = asyncio.run(run())
        self.assertTrue(first.closed)
        self.assertEqual(json.loads(second.sent[0])['op'], 'subscribe')

    def test_reconnect_disabled_surfaces_the_connection_error(self):
        async def run():
            ws = _public(reconnect=False, ping_interval=0)
            ws.connect = AsyncMock()
            sock = _DroppingSocket()
            sock.drop.set()
            ws.websocket = sock
            task = await ws.start()
            await task

        with self.assertRaises(ConnectionClosedError):
            asyncio.run(run())


if __name__ == '__main__':
    unittest.main()

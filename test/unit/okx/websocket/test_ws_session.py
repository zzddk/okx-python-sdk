"""
Unit tests for the shared WebSocket session: callback contract, heartbeat,
reconnect and subscription replay.

Mirrors: okx/websocket/WsBaseAsync.py
"""
import asyncio
import json
import unittest
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestMessageRouting(unittest.TestCase):
    """Which callback receives a message: arg, then fallback."""

    def test_two_channels_reach_their_own_callbacks(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            tickers, books = [], []
            await ws.subscribe([{'channel': 'tickers', 'instId': 'BTC-USDT'}], tickers.append)
            await ws.subscribe([{'channel': 'books', 'instId': 'BTC-USDT'}], books.append)
            await ws._handle_message(json.dumps({'arg': {'channel': 'tickers', 'instId': 'BTC-USDT'}, 'data': ['t']}))
            await ws._handle_message(json.dumps({'arg': {'channel': 'books', 'instId': 'BTC-USDT'}, 'data': ['b']}))
            return tickers, books

        tickers, books = asyncio.run(run())
        self.assertEqual([json.loads(m)['data'] for m in tickers], [['t']])
        self.assertEqual([json.loads(m)['data'] for m in books], [['b']])

    def test_unmatched_message_falls_back_to_callback(self):
        async def run():
            ws = _public()
            seen = []
            ws.callback = seen.append
            frame = json.dumps({'arg': {'channel': 'unknown'}, 'data': []})
            await ws._handle_message(frame)
            return seen, frame

        seen, frame = asyncio.run(run())
        self.assertEqual(seen, [frame])

    def test_subscription_without_callback_falls_back(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            seen = []
            ws.callback = seen.append
            params = [{'channel': 'tickers', 'instId': 'BTC-USDT'}]
            await ws.subscribe(params, None)
            await ws._handle_message(json.dumps({'arg': params[0], 'data': []}))
            return seen

        self.assertEqual(len(asyncio.run(run())), 1)

    def test_unmatched_message_without_a_fallback_is_dropped(self):
        async def run():
            ws = _public()
            await ws._handle_message('{"arg": {"channel": "unknown"}}')

        asyncio.run(run())


class TestRequestRouting(unittest.TestCase):
    """One-shot responses are matched by id, not by arg."""

    def _private(self):
        ws = WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s',
                            url=URL, ping_interval=0)
        ws.websocket = AsyncMock()
        ws.websocket.recv = AsyncMock(return_value=ACK)
        return ws

    def test_order_ack_goes_to_the_request_callback_once(self):
        async def run():
            ws = self._private()
            fallback, routed = [], []
            ws.callback = fallback.append
            await ws.place_order([{'instId': 'BTC-USDT'}], callback=routed.append, id='o1')
            ack = json.dumps({'id': 'o1', 'op': 'order', 'data': []})
            await ws._handle_message(ack)
            await ws._handle_message(ack)
            return routed, fallback, ack

        routed, fallback, ack = asyncio.run(run())
        self.assertEqual(len(routed), 1)
        self.assertEqual(fallback, [ack])

    def test_callback_without_an_id_becomes_the_fallback(self):
        async def run():
            ws = self._private()
            received = []
            callback = received.append
            await ws.place_order([{'instId': 'BTC-USDT'}], callback=callback)
            await ws._handle_message(json.dumps({'op': 'order', 'data': []}))
            return ws, callback, received

        ws, callback, received = asyncio.run(run())
        self.assertIs(ws.callback, callback)
        self.assertEqual(len(received), 1)


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


class _RecvSocket:
    """Answers `recv()` from a script; used where no reader is running."""

    def __init__(self, *frames):
        self._frames = list(frames)
        self.sent = []

    async def recv(self):
        if not self._frames:
            await asyncio.sleep(3600)
        return self._frames.pop(0)

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


class TestLoginWithoutAReader(unittest.TestCase):
    def test_frames_before_the_answer_reach_the_callback(self):
        async def run():
            ws = WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s',
                                url=URL, ping_interval=0)
            data = '{"arg": {"channel": "account"}, "data": [{"bal": "1"}]}'
            ws.websocket = _RecvSocket(data, ACK)
            seen = []
            ws.callback = seen.append
            await ws.login()
            return ws, seen

        ws, seen = asyncio.run(run())
        self.assertTrue(ws.isLoggedIn)
        self.assertEqual(len(seen), 1)
        self.assertIn('"bal"', seen[0])


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

    def test_subscribe_rejects_a_blank_channel_before_sending(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            for arg in ({'channel': '   ', 'instId': 'BTC-USDT'}, {'instId': 'BTC-USDT'}):
                with self.subTest(arg=arg):
                    with self.assertRaises(ValueError):
                        await ws.subscribe([arg], None)
            return ws

        ws = asyncio.run(run())
        self.assertEqual(ws.subscriptions, {})
        ws.websocket.send.assert_not_awaited()

    def test_subscribe_rejects_the_whole_batch_before_touching_anything(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            await ws.subscribe([{'channel': 'tickers', 'instId': 'BTC-USDT'}], None)
            with self.assertRaises(ValueError):
                await ws.subscribe([{'channel': 'books'}, 'x'], None)
            return ws

        ws = asyncio.run(run())
        self.assertEqual(
            ws.subscriptions,
            {json.dumps({'channel': 'tickers', 'instId': 'BTC-USDT'}, sort_keys=True):
             {'channel': 'tickers', 'instId': 'BTC-USDT'}},
        )
        self.assertEqual(len(ws.websocket.send.await_args_list), 1)

    def test_unsubscribe_rejects_an_unroutable_arg(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            arg = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            await ws.subscribe([arg], None)
            for bad in ({'channel': '  '}, {'instId': 'BTC-USDT'}, 'x'):
                with self.subTest(bad=bad):
                    with self.assertRaises(ValueError):
                        await ws.unsubscribe([bad], None)
            return ws, arg

        ws, arg = asyncio.run(run())
        self.assertEqual(len(ws.subscriptions), 1)
        self.assertIsNone(ws._subs.take({'arg': arg}))
        self.assertEqual(len(ws.websocket.send.await_args_list), 1)

    def test_subscriptions_view_is_derived_from_the_table(self):
        ws = _public()
        arg = {'channel': 'tickers', 'instId': 'BTC-USDT'}
        ws._subs.add([arg])

        self.assertEqual(ws.subscriptions, {json.dumps(arg, sort_keys=True): arg})

    def test_subscriptions_view_rejects_assignment(self):
        ws = _public()

        with self.assertRaises(AttributeError):
            ws.subscriptions = {}

    def test_generic_send_leaves_the_subscription_table_alone(self):
        """Only subscribe()/unsubscribe() own the table; send() is generic."""
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            await ws.send('subscribe', [{'channel': 'tickers', 'instId': 'BTC-USDT'}])
            return ws.subscriptions

        self.assertEqual(asyncio.run(run()), {})


class TestSessionRestore(unittest.TestCase):
    def test_public_replays_subscriptions(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            ws._subs.add([
                {'channel': 'tickers', 'instId': 'BTC-USDT'},
                {'channel': 'books', 'instId': 'ETH-USDT'},
            ])
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
            ws._subs.add([{'channel': 'account'}])
            await ws._restore_session()
            return ws, [json.loads(call.args[0]) for call in ws.websocket.send.await_args_list]

        ws, payloads = asyncio.run(run())
        self.assertTrue(ws.isLoggedIn)
        self.assertEqual([p['op'] for p in payloads], ['login', 'subscribe'])

    def test_restore_session_forgets_pending_requests(self):
        async def run():
            ws = _public()
            ws.websocket = AsyncMock()
            ws._subs.add_request('o1', MagicMock())
            await ws._restore_session()
            return ws

        ws = asyncio.run(run())
        self.assertIsNone(ws._subs.take({'id': 'o1'}))

    def test_stop_forgets_pending_requests(self):
        async def run():
            ws = _public(ping_interval=0)
            ws.websocket = AsyncMock()
            ws._subs.add_request('o1', MagicMock())
            await ws.stop()
            return ws

        ws = asyncio.run(run())
        self.assertIsNone(ws._subs.take({'id': 'o1'}))


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

            tickers = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            books = {'channel': 'books', 'instId': 'ETH-USDT'}
            await ws.start()
            await ws.subscribe([tickers], None)
            await ws.subscribe([books], None)
            first.drop.set()

            loop = asyncio.get_running_loop()
            deadline = loop.time() + 2
            while len([p for p in second.sent if json.loads(p)['op'] == 'subscribe']) < 2:
                if loop.time() > deadline:
                    raise AssertionError(f'no resubscribe after reconnect: {second.sent}')
                await asyncio.sleep(0.01)

            await ws.stop()
            return first, second

        first, second = asyncio.run(run())
        self.assertTrue(first.closed)
        self.assertEqual(
            [json.loads(p)['args'] for p in second.sent],
            [[{'channel': 'tickers', 'instId': 'BTC-USDT'}],
             [{'channel': 'books', 'instId': 'ETH-USDT'}]],
        )

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

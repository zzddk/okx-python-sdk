"""
Unit tests for the shared WebSocket session: callback contract, heartbeat,
reconnect and subscription replay.

Mirrors: okx/websocket/WsBaseAsync.py, okx/websocket/connection.py
"""
import asyncio
import json
import unittest
from unittest.mock import patch

from websockets.exceptions import ConnectionClosedError

from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync
from okx.websocket.connector import WebSocketConnector

from .fakes import FakeConnector, FakeSocket

URL = 'wss://example.com'
ACK = '{"event":"login","code":"0"}'
REJECT = '{"event":"login","code":"60009","msg":"Login failed"}'


def _public(**kwargs):
    kwargs.setdefault('url', URL)
    kwargs.setdefault('ping_interval', 0)
    return WsPublicAsync(**kwargs)


def _private(**kwargs):
    kwargs.setdefault('url', URL)
    kwargs.setdefault('ping_interval', 0)
    return WsPrivateAsync(apiKey='k', passphrase='p', secretKey='s', **kwargs)


def _public_on(*frames, **socket_kwargs):
    sock = FakeSocket(*frames, **socket_kwargs)
    return _public(connector=FakeConnector(sock)), sock


def _private_on(*frames, **socket_kwargs):
    sock = FakeSocket(*frames, **socket_kwargs)
    return _private(connector=FakeConnector(sock)), sock


async def _until(predicate, timeout: float = 1.0) -> None:
    """Wait for a condition the reader task settles; fails loudly on timeout."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not predicate():
        if loop.time() > deadline:
            raise AssertionError('condition not met before the deadline')
        await asyncio.sleep(0.005)


class TestCallbackContract(unittest.TestCase):
    def test_async_callback_is_awaited_in_order(self):
        async def run():
            sock = FakeSocket('a', 'b', ends=True)
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            seen = []

            async def callback(message):
                await asyncio.sleep(0)
                seen.append(message)

            ws.callback = callback
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return seen

        self.assertEqual(asyncio.run(run()), ['a', 'b'])

    def test_sync_callback_still_works(self):
        async def run():
            sock = FakeSocket('a', ends=True)
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            seen = []
            ws.callback = seen.append
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return seen

        self.assertEqual(asyncio.run(run()), ['a'])

    def test_callback_exception_does_not_end_the_stream(self):
        async def run():
            sock = FakeSocket('boom', 'after', ends=True)
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            seen = []

            async def callback(message):
                if message == 'boom':
                    raise RuntimeError('callback failed')
                seen.append(message)

            ws.callback = callback
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return seen

        with patch('okx.websocket.WsBaseAsync.logger.exception') as log:
            seen = asyncio.run(run())

        self.assertEqual(seen, ['after'])
        log.assert_called_once()

    def test_pong_is_not_delivered(self):
        async def run():
            sock = FakeSocket('pong', 'a', ends=True)
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            seen = []
            ws.callback = seen.append
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return seen

        self.assertEqual(asyncio.run(run()), ['a'])


class TestMessageRouting(unittest.TestCase):
    """Which callback receives a message: arg, then fallback."""

    def test_two_channels_reach_their_own_callbacks(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            tickers, books = [], []
            await ws.subscribe([{'channel': 'tickers', 'instId': 'BTC-USDT'}], tickers.append)
            await ws.subscribe([{'channel': 'books', 'instId': 'BTC-USDT'}], books.append)
            await ws._on_frame(json.dumps({'arg': {'channel': 'tickers', 'instId': 'BTC-USDT'}, 'data': ['t']}))
            await ws._on_frame(json.dumps({'arg': {'channel': 'books', 'instId': 'BTC-USDT'}, 'data': ['b']}))
            await ws.stop()
            return tickers, books

        tickers, books = asyncio.run(run())
        self.assertEqual([json.loads(m)['data'] for m in tickers], [['t']])
        self.assertEqual([json.loads(m)['data'] for m in books], [['b']])

    def test_unmatched_message_falls_back_to_callback(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            seen = []
            ws.callback = seen.append
            frame = json.dumps({'arg': {'channel': 'unknown'}, 'data': []})
            await ws._on_frame(frame)
            await ws.stop()
            return seen, frame

        seen, frame = asyncio.run(run())
        self.assertEqual(seen, [frame])

    def test_subscription_without_callback_falls_back(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            seen = []
            ws.callback = seen.append
            params = [{'channel': 'tickers', 'instId': 'BTC-USDT'}]
            await ws.subscribe(params, None)
            await ws._on_frame(json.dumps({'arg': params[0], 'data': []}))
            await ws.stop()
            return seen

        self.assertEqual(len(asyncio.run(run())), 1)

    def test_unmatched_message_without_a_fallback_is_dropped(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            await ws._on_frame('{"arg": {"channel": "unknown"}}')
            await ws.stop()

        asyncio.run(run())


class TestRequestRouting(unittest.TestCase):
    """One-shot responses are matched by id, not by arg."""

    def test_order_ack_goes_to_the_request_callback_once(self):
        async def run():
            ws, sock = _private_on(answer_login=ACK)
            await ws.start()
            fallback, routed = [], []
            ws.callback = fallback.append
            await ws.place_order([{'instId': 'BTC-USDT'}], callback=routed.append, id='o1')
            ack = json.dumps({'id': 'o1', 'op': 'order', 'data': []})
            await ws._on_frame(ack)
            await ws._on_frame(ack)
            await ws.stop()
            return routed, fallback, ack

        routed, fallback, ack = asyncio.run(run())
        self.assertEqual(len(routed), 1)
        self.assertEqual(fallback, [ack])

    def test_callback_without_an_id_becomes_the_fallback(self):
        async def run():
            ws, sock = _private_on(answer_login=ACK)
            await ws.start()
            received = []
            callback = received.append
            await ws.place_order([{'instId': 'BTC-USDT'}], callback=callback)
            await ws._on_frame(json.dumps({'op': 'order', 'data': []}))
            await ws.stop()
            return ws, callback, received

        ws, callback, received = asyncio.run(run())
        self.assertIs(ws.callback, callback)
        self.assertEqual(len(received), 1)


class TestHeartbeat(unittest.TestCase):
    def test_missing_pong_triggers_a_reconnect(self):
        async def run():
            first, second = FakeSocket(), FakeSocket(answer_pings=True)
            connector = FakeConnector(first, second)
            ws = _public(connector=connector, ping_interval=0.01, ping_timeout=0.01,
                         reconnect_backoff=0)
            await ws.start()
            await _until(lambda: len(connector.urls) == 2)
            await ws.stop()
            return first, connector

        first, connector = asyncio.run(run())
        self.assertIn('ping', first.sent)
        self.assertTrue(first.closed)
        self.assertEqual(connector.urls, [URL, URL])

    def test_pong_keeps_the_connection_open(self):
        async def run():
            sock = FakeSocket(answer_pings=True)
            connector = FakeConnector(sock)
            ws = _public(connector=connector, ping_interval=0.01, ping_timeout=0.05)
            await ws.start()
            await _until(lambda: sock.sent.count('ping') >= 2)
            await ws.stop()
            return sock, connector

        sock, connector = asyncio.run(run())
        self.assertEqual(connector.urls, [URL])
        self.assertGreaterEqual(sock.sent.count('ping'), 2)


class TestLogin(unittest.TestCase):
    def test_private_start_logs_in_through_the_reader(self):
        async def run():
            ws, sock = _private_on(answer_login=ACK)
            await ws.start()
            logged_in = ws.isLoggedIn
            await ws.stop()
            return logged_in

        self.assertTrue(asyncio.run(run()))

    def test_a_rejected_login_fails_start(self):
        async def run():
            ws, sock = _private_on(answer_login=REJECT)
            await ws.start()

        with self.assertRaises(ConnectionError) as ctx:
            asyncio.run(run())
        self.assertIn('60009', str(ctx.exception))

    def test_a_drop_during_login_fails_instead_of_waiting_for_the_timeout(self):
        """The socket dying while the request is in flight is not a 10s wait."""
        async def run():
            sock = FakeSocket()
            ws = _private(connector=FakeConnector(sock), reconnect_backoff=0)

            async def drop_once_the_request_is_out():
                await _until(lambda: bool(sock.sent))
                sock.drop()

            asyncio.create_task(drop_once_the_request_is_out())
            with self.assertRaises(ConnectionError):
                await asyncio.wait_for(ws.start(), timeout=1)

        asyncio.run(run())

    def test_login_requires_start(self):
        ws = _private()
        with self.assertRaises(RuntimeError) as ctx:
            asyncio.run(ws.login())
        self.assertIn('start() must be called before login()', str(ctx.exception))

    def test_public_login_waits_for_the_ack_and_sets_the_latch(self):
        async def run():
            sock = FakeSocket(answer_login=ACK)
            ws = _public(connector=FakeConnector(sock), apiKey='k', passphrase='p', secretKey='s')
            await ws.start()
            self.assertFalse(ws.isLoggedIn)
            self.assertTrue(await ws.login(timeout=1))
            logged_in = ws.isLoggedIn
            await ws.stop()
            return logged_in

        self.assertTrue(asyncio.run(run()))

    def test_login_times_out_without_an_ack(self):
        async def run():
            sock = FakeSocket()
            ws = _public(connector=FakeConnector(sock), apiKey='k', passphrase='p', secretKey='s')
            await ws.start()
            try:
                await ws.login(timeout=0.05)
            finally:
                await ws.stop()

        with self.assertRaises(TimeoutError):
            asyncio.run(run())

    def test_non_login_frames_reach_the_callback(self):
        async def run():
            sock = FakeSocket('{"event":"notice"}', answer_login=ACK)
            ws = _public(connector=FakeConnector(sock), apiKey='k', passphrase='p', secretKey='s')
            received = []
            ws.callback = received.append
            await ws.start()
            await ws.login(timeout=1)
            await ws.stop()
            return received

        self.assertEqual(asyncio.run(run()), ['{"event":"notice"}'])


class TestSubscriptionRegistry(unittest.TestCase):
    def test_subscribe_records_and_unsubscribe_removes(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            tickers = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            books = {'channel': 'books', 'instId': 'BTC-USDT'}
            await ws.subscribe([tickers], None)
            await ws.subscribe([dict(tickers)], None)  # duplicate is not stored twice
            await ws.subscribe([books], None)
            self.assertEqual(len(ws.subscriptions), 2)
            await ws.unsubscribe([tickers], None)
            self.assertEqual(list(ws.subscriptions.values()), [books])
            await ws.stop()

        asyncio.run(run())

    def test_subscribe_rejects_a_blank_channel_before_sending(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            for arg in ({'channel': '   ', 'instId': 'BTC-USDT'}, {'instId': 'BTC-USDT'}):
                with self.subTest(arg=arg):
                    with self.assertRaises(ValueError):
                        await ws.subscribe([arg], None)
            await ws.stop()
            return ws, sock

        ws, sock = asyncio.run(run())
        self.assertEqual(ws.subscriptions, {})
        self.assertEqual(sock.sent, [])

    def test_subscribe_rejects_the_whole_batch_before_touching_anything(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            await ws.subscribe([{'channel': 'tickers', 'instId': 'BTC-USDT'}], None)
            with self.assertRaises(ValueError):
                await ws.subscribe([{'channel': 'books'}, 'x'], None)
            await ws.stop()
            return ws, sock

        ws, sock = asyncio.run(run())
        self.assertEqual(
            ws.subscriptions,
            {json.dumps({'channel': 'tickers', 'instId': 'BTC-USDT'}, sort_keys=True):
             {'channel': 'tickers', 'instId': 'BTC-USDT'}},
        )
        self.assertEqual(len(sock.payloads), 1)

    def test_unsubscribe_rejects_an_unroutable_arg(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            arg = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            await ws.subscribe([arg], None)
            for bad in ({'channel': '  '}, {'instId': 'BTC-USDT'}, 'x'):
                with self.subTest(bad=bad):
                    with self.assertRaises(ValueError):
                        await ws.unsubscribe([bad], None)
            await ws.stop()
            return ws, sock, arg

        ws, sock, arg = asyncio.run(run())
        self.assertEqual(len(ws.subscriptions), 1)
        self.assertIsNone(ws._subs.take({'arg': arg}))
        self.assertEqual(len(sock.payloads), 1)

    def test_subscriptions_view_is_derived_from_the_table(self):
        ws = _public()
        arg = {'channel': 'tickers', 'instId': 'BTC-USDT'}
        ws._subs.add([arg])

        self.assertEqual(ws.subscriptions, {json.dumps(arg, sort_keys=True): arg})

    def test_websocket_view_rejects_assignment(self):
        ws = _public()

        with self.assertRaises(AttributeError):
            ws.websocket = object()

    def test_subscriptions_view_rejects_assignment(self):
        ws = _public()

        with self.assertRaises(AttributeError):
            ws.subscriptions = {}

    def test_generic_send_leaves_the_subscription_table_alone(self):
        """Only subscribe()/unsubscribe() own the table; send() is generic."""
        async def run():
            ws, sock = _public_on()
            await ws.start()
            await ws.send('subscribe', [{'channel': 'tickers', 'instId': 'BTC-USDT'}])
            await ws.stop()
            return ws.subscriptions

        self.assertEqual(asyncio.run(run()), {})


class TestStartRestoresSession(unittest.TestCase):
    def test_public_replays_subscriptions(self):
        async def run():
            ws, sock = _public_on()
            ws._subs.add([
                {'channel': 'tickers', 'instId': 'BTC-USDT'},
                {'channel': 'books', 'instId': 'ETH-USDT'},
            ])
            await ws.start()
            await ws.stop()
            return sock.payloads

        payloads = asyncio.run(run())
        self.assertEqual([p['op'] for p in payloads], ['subscribe', 'subscribe'])
        self.assertEqual(payloads[0]['args'], [{'channel': 'tickers', 'instId': 'BTC-USDT'}])

    def test_private_logs_in_then_replays_subscriptions(self):
        async def run():
            ws, sock = _private_on(answer_login=ACK)
            ws._subs.add([{'channel': 'account'}])
            await ws.start()
            logged_in = ws.isLoggedIn
            await ws.stop()
            return logged_in, sock.payloads

        logged_in, payloads = asyncio.run(run())
        self.assertTrue(logged_in)
        self.assertEqual([p['op'] for p in payloads], ['login', 'subscribe'])

    def test_start_forgets_pending_requests(self):
        async def run():
            ws, sock = _public_on()
            ws._subs.add_request('o1', object())
            await ws.start()
            await ws.stop()
            return ws

        ws = asyncio.run(run())
        self.assertIsNone(ws._subs.take({'id': 'o1'}))

    def test_stop_before_start_is_a_no_op(self):
        ws = _public()

        asyncio.run(ws.stop())
        self.assertIsNone(ws.websocket)

    def test_stop_forgets_pending_requests(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            ws._subs.add_request('o1', object())
            await ws.stop()
            return ws

        ws = asyncio.run(run())
        self.assertIsNone(ws._subs.take({'id': 'o1'}))


class TestConnectorChoice(unittest.TestCase):
    def test_injected_connector_wins_over_proxy_without_raising(self):
        """`connector` wins over `proxy`, the same rule as Transport(proxy=, http=)."""
        async def run():
            sock = FakeSocket(ends=True)
            connector = FakeConnector(sock)
            ws = _public(proxy='http://127.0.0.1:1', connector=connector, reconnect=False)
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
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
            ws, sock = _public_on('go', ends=True)
            finished = []

            async def callback(message):
                await ws.stop()
                finished.append(message)

            ws.callback = callback
            task = await ws.start()
            await asyncio.wait_for(task, timeout=1)
            return finished

        self.assertEqual(asyncio.run(run()), ['go'])


    def test_stop_inside_the_error_callback_completes(self):
        async def run():
            sock = FakeSocket()
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            stopped = []

            async def callback(message):
                if json.loads(message).get("code") == "ConnClosed":
                    await ws.stop()
                    stopped.append(True)

            ws.callback = callback
            task = await ws.start()
            sock.drop()
            await asyncio.wait_for(task, timeout=1)
            return stopped

        self.assertEqual(asyncio.run(run()), [True])


class TestReconnect(unittest.TestCase):
    def test_reconnects_and_replays_subscriptions(self):
        async def run():
            first, second = FakeSocket(), FakeSocket()
            ws = _public(connector=FakeConnector(first, second), reconnect_backoff=0)

            tickers = {'channel': 'tickers', 'instId': 'BTC-USDT'}
            books = {'channel': 'books', 'instId': 'ETH-USDT'}
            await ws.start()
            await ws.subscribe([tickers], None)
            await ws.subscribe([books], None)
            first.drop()

            await _until(lambda: len([p for p in second.payloads if p['op'] == 'subscribe']) >= 2)
            await ws.stop()
            return first, second

        first, second = asyncio.run(run())
        self.assertTrue(first.closed)
        self.assertEqual(
            [p['args'] for p in second.payloads],
            [[{'channel': 'tickers', 'instId': 'BTC-USDT'}],
             [{'channel': 'books', 'instId': 'ETH-USDT'}]],
        )

    def test_reconnect_disabled_surfaces_the_connection_error(self):
        async def run():
            sock = FakeSocket()
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            task = await ws.start()
            sock.drop()
            await asyncio.wait_for(task, timeout=1)

        with self.assertRaises(ConnectionClosedError):
            asyncio.run(run())

    def test_private_reconnect_logs_in_then_replays(self):
        async def run():
            first = FakeSocket(answer_login=ACK)
            second = FakeSocket(answer_login=ACK)
            ws = _private(connector=FakeConnector(first, second), reconnect_backoff=0)
            await ws.start()
            await ws.subscribe([{'channel': 'account'}], None)
            first.drop()
            await _until(lambda: [p['op'] for p in second.payloads] == ['login', 'subscribe'])
            await ws.stop()
            return second.payloads

        payloads = asyncio.run(run())
        self.assertEqual(payloads[0]['op'], 'login')
        self.assertEqual(payloads[1]['args'], [{'channel': 'account'}])

    def test_a_failed_restore_enters_the_backoff(self):
        """Login rejection on a reconnect is retried, not surfaced."""
        async def run():
            first = FakeSocket(answer_login=ACK)
            rejected = FakeSocket(answer_login=REJECT)
            recovered = FakeSocket(answer_login=ACK)
            connector = FakeConnector(first, rejected, recovered)
            ws = _private(connector=connector, reconnect_backoff=0)
            await ws.start()
            await ws.subscribe([{'channel': 'account'}], None)
            first.drop()

            await _until(lambda: len(connector.urls) == 3)
            await _until(lambda: [p['op'] for p in recovered.payloads] == ['login', 'subscribe'])
            await ws.stop()
            return connector, recovered

        connector, recovered = asyncio.run(run())
        self.assertEqual(len(connector.urls), 3)
        self.assertEqual([p['op'] for p in recovered.payloads], ['login', 'subscribe'])


class TestClosedConnectionReporting(unittest.TestCase):
    def test_a_dropped_socket_reaches_the_callback_as_an_error_event(self):
        received = []

        async def run():
            sock = FakeSocket('{"data": "ok"}')
            ws = _public(connector=FakeConnector(sock), reconnect=False)
            ws.callback = received.append
            task = await ws.start()
            sock.drop()
            await asyncio.wait_for(task, timeout=1)

        with patch('okx.websocket.connection.logger.error') as log:
            with self.assertRaises(ConnectionClosedError):
                asyncio.run(run())

        log.assert_called_once()
        self.assertEqual(received[0], '{"data": "ok"}')
        error_payload = json.loads(received[1])
        self.assertEqual(error_payload["event"], "error")
        self.assertEqual(error_payload["code"], "ConnClosed")


class TestStartWhileStopping(unittest.TestCase):
    """stop() from a callback keeps the supervisor alive until the frame ends.

    `stop()` returns immediately when the frame being dispatched called it, so
    `_task` has to stay set: otherwise `start()` would open a second socket
    beside the read loop that is still running.
    """

    def test_start_from_the_stopping_callback_raises(self):
        errors = []

        async def run():
            sock = FakeSocket()
            ws = _public(connector=FakeConnector(sock))
            seen = []

            async def on_message(message):
                seen.append(message)
                await ws.stop()
                try:
                    await ws.start()
                except RuntimeError as exc:
                    errors.append(str(exc))

            ws.callback = on_message
            task = await ws.start()
            sock.push('{"data": 1}')
            await asyncio.wait_for(task, timeout=1)
            return seen

        self.assertEqual(asyncio.run(run()), ['{"data": 1}'])
        self.assertEqual(len(errors), 1)
        self.assertIn("still stopping", errors[0])


class TestNeedsLoginPredicate(unittest.TestCase):
    """One predicate answers "should this connection authenticate?".

    Truth table: client type x ever logged in x credentials x current login.
    The latch is what keeps a public client that logged in for the business
    channel logging in again after a reconnect.
    """

    def _ws(self, private, credentials, ever_logged_in, logged_in):
        ws = _private() if private else _public()
        if credentials:
            ws.apiKey, ws.passphrase, ws.secretKey = 'k', 'p', 's'
        else:
            ws.apiKey = ws.passphrase = ws.secretKey = ''
        ws._ever_logged_in = ever_logged_in
        ws._is_logged_in = logged_in
        return ws

    def test_truth_table(self):
        cases = [
            # private, credentials, ever_logged_in, logged_in, expected
            (False, False, False, False, False),
            (False, False, False, True, False),
            (False, False, True, False, False),
            (False, False, True, True, False),
            (False, True, False, False, False),
            (False, True, False, True, False),
            (False, True, True, False, True),
            (False, True, True, True, False),
            (True, False, False, False, False),
            (True, False, False, True, False),
            (True, False, True, False, False),
            (True, False, True, True, False),
            (True, True, False, False, True),
            (True, True, False, True, False),
            (True, True, True, False, True),
            (True, True, True, True, False),
        ]
        for private, credentials, ever, logged, expected in cases:
            with self.subTest(private=private, credentials=credentials,
                              ever_logged_in=ever, logged_in=logged):
                ws = self._ws(private, credentials, ever, logged)
                self.assertIs(ws._needs_login(), expected)

    def test_is_logged_in_is_read_only(self):
        ws = _public()
        with self.assertRaises(AttributeError):
            ws.isLoggedIn = True

if __name__ == '__main__':
    unittest.main()

"""
Unit tests for okxsdk.websocket.subscriptions

Mirrors: okxsdk/websocket/subscriptions.py
"""
import unittest

from okxsdk.websocket.subscriptions import Subscriptions

TICKERS = {'channel': 'tickers', 'instId': 'BTC-USDT'}
BOOKS = {'channel': 'books', 'instId': 'BTC-USDT'}
ETH = {'channel': 'tickers', 'instId': 'ETH-USDT'}


class TestArgRouting(unittest.TestCase):
    """Contract 1-6: routing is by the whole arg, then by id."""

    def test_two_inst_ids_reach_their_own_callbacks(self):
        subs = Subscriptions()
        btc, eth = object(), object()
        subs.add([TICKERS], btc)
        subs.add([ETH], eth)

        self.assertIs(subs.take({'arg': dict(TICKERS), 'data': []}), btc)
        self.assertIs(subs.take({'arg': dict(ETH), 'data': []}), eth)

    def test_arg_key_ignores_dict_key_order(self):
        subs = Subscriptions()
        callback = object()
        subs.add([{'instId': 'BTC-USDT', 'channel': 'tickers'}], callback)

        self.assertIs(subs.take({'arg': {'channel': 'tickers', 'instId': 'BTC-USDT'}}), callback)

    def test_same_arg_replaces_the_callback_and_keeps_one_entry(self):
        subs = Subscriptions()
        first, second = object(), object()
        subs.add([TICKERS], first)
        subs.add([TICKERS], second)

        self.assertEqual(len(subs.replay()), 1)
        self.assertIs(subs.take({'arg': dict(TICKERS)}), second)

    def test_arg_hit_keeps_the_subscription(self):
        subs = Subscriptions()
        callback = object()
        subs.add([TICKERS], callback)

        payload = {'arg': dict(TICKERS), 'data': ['first']}
        self.assertIs(subs.take(payload), callback)
        self.assertIs(subs.take(payload), callback)

    def test_request_hit_is_consumed(self):
        subs = Subscriptions()
        callback = object()
        subs.add_request('o1', callback)

        self.assertIs(subs.take({'id': 'o1', 'op': 'order'}), callback)
        self.assertIsNone(subs.take({'id': 'o1', 'op': 'order'}))

    def test_subscription_without_a_callback_returns_none(self):
        subs = Subscriptions()
        subs.add([TICKERS])

        self.assertIsNone(subs.take({'arg': dict(TICKERS)}))

    def test_arg_wins_over_id(self):
        subs = Subscriptions()
        routed, requested = object(), object()
        subs.add([TICKERS], routed)
        subs.add_request('x', requested)

        self.assertIs(subs.take({'arg': dict(TICKERS), 'id': 'x'}), routed)
        self.assertIs(subs.take({'id': 'x'}), requested)

    def test_added_entries_are_copies_of_the_caller_dicts(self):
        subs = Subscriptions()
        arg = dict(TICKERS)
        subs.add([arg])
        arg['instId'] = 'CHANGED'

        self.assertEqual(subs.replay(), [TICKERS])


class TestRemovalAndReplay(unittest.TestCase):
    """Contract 7-8: removal disappears from routing and from replay."""

    def test_removed_arg_no_longer_routes(self):
        subs = Subscriptions()
        subs.add([TICKERS], object())

        subs.remove([TICKERS])

        self.assertIsNone(subs.take({'arg': dict(TICKERS)}))
        self.assertEqual(subs.replay(), [])

    def test_removing_an_unknown_arg_is_harmless(self):
        subs = Subscriptions()

        self.assertIsNone(subs.remove([TICKERS]))
        self.assertEqual(subs.replay(), [])

    def test_replay_follows_add_order_and_excludes_requests(self):
        subs = Subscriptions()
        subs.add([TICKERS])
        subs.add([BOOKS])
        subs.add([ETH])
        subs.add_request('o1', object())

        self.assertEqual(subs.replay(), [TICKERS, BOOKS, ETH])

    def test_replay_returns_detached_copies(self):
        subs = Subscriptions()
        subs.add([TICKERS])

        replayed = subs.replay()
        replayed[0]['instId'] = 'CHANGED'

        self.assertEqual(subs.replay(), [TICKERS])

    def test_drop_requests_leaves_subscriptions_alone(self):
        subs = Subscriptions()
        callback = object()
        subs.add([TICKERS], callback)
        subs.add_request('o1', object())

        subs.drop_requests()

        self.assertIsNone(subs.take({'id': 'o1'}))
        self.assertIs(subs.take({'arg': dict(TICKERS)}), callback)


class TestArgValidation(unittest.TestCase):
    """Contract 10: only a routable arg enters the table, checked per batch."""

    UNROUTABLE = (
        'text',
        42,
        None,
        ['channel'],
        {},
        {'instId': 'BTC-USDT'},
        {'channel': ''},
        {'channel': '   '},
        {'channel': 1},
    )

    def test_add_rejects_every_unroutable_arg_and_keeps_the_table(self):
        subs = Subscriptions()
        for arg in self.UNROUTABLE:
            with self.subTest(arg=arg):
                with self.assertRaises(ValueError):
                    subs.add([arg])
                self.assertEqual(subs.replay(), [])

    def test_add_rejects_a_batch_atomically(self):
        subs = Subscriptions()
        first, second = object(), object()
        subs.add([TICKERS], first)

        with self.assertRaises(ValueError):
            subs.add([TICKERS, {'channel': '  '}], second)
        with self.assertRaises(ValueError):
            subs.add([{'channel': 'books'}, {'channel': ''}])

        self.assertEqual(subs.replay(), [TICKERS])
        self.assertIs(subs.take({'arg': dict(TICKERS)}), first)

    def test_remove_rejects_every_unroutable_arg_and_keeps_the_table(self):
        subs = Subscriptions()
        for arg in self.UNROUTABLE:
            with self.subTest(arg=arg):
                with self.assertRaises(ValueError):
                    subs.remove([arg])
                self.assertEqual(subs.replay(), [])

    def test_remove_rejects_a_batch_atomically(self):
        subs = Subscriptions()
        subs.add([TICKERS, BOOKS])

        with self.assertRaises(ValueError):
            subs.remove([TICKERS, 'x'])
        with self.assertRaises(ValueError):
            subs.remove([TICKERS, {'channel': '  '}])

        self.assertEqual(subs.replay(), [TICKERS, BOOKS])


class TestDirtyPayloads(unittest.TestCase):
    """Contract 9: server data must never turn a miss into an exception."""

    def test_non_dict_payloads_return_none(self):
        subs = Subscriptions()

        for payload in (None, 'text', 42, [], [{'arg': dict(TICKERS)}]):
            with self.subTest(payload=payload):
                self.assertIsNone(subs.take(payload))

    def test_malformed_fields_return_none(self):
        subs = Subscriptions()
        subs.add([TICKERS], object())
        subs.add_request('o1', object())

        for payload in ({}, {'arg': 'x'}, {'arg': ['x']}, {'id': 123}, {'id': []}, {'id': {}}):
            with self.subTest(payload=payload):
                self.assertIsNone(subs.take(payload))

        # A malformed payload must not consume a real request either.
        self.assertIsNotNone(subs.take({'id': 'o1'}))


if __name__ == '__main__':
    unittest.main()

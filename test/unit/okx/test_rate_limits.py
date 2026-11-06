"""The rate-limit table must match the frozen acceptance set."""

import unittest

from okx.consts.rate_limits import RATE_LIMITS

from .rate_limit_acceptance import ACCEPTANCE_PATHS, ORDERS_ONLY_PATHS


class TestRateLimitTable(unittest.TestCase):
    def test_table_covers_exactly_the_acceptance_set(self):
        self.assertEqual(set(RATE_LIMITS), set(ACCEPTANCE_PATHS))

    def test_orders_only_paths_are_not_throttled(self):
        self.assertFalse(set(RATE_LIMITS) & set(ORDERS_ONLY_PATHS))

    def test_entries_are_positive_request_counts_and_windows(self):
        for path, entry in RATE_LIMITS.items():
            with self.subTest(path=path):
                self.assertTrue(path.startswith('/api/v5/'))
                count, window = entry
                self.assertIsInstance(count, int)
                self.assertGreater(count, 0)
                self.assertGreater(window, 0)

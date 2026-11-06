"""The rate-limit table must match the frozen acceptance set.

The table is also one half of a partition: every path declared in okxsdk/consts
is either throttled or exempt with a known reason. A new endpoint therefore
fails CI until it is classified.
"""

import unittest

from okxsdk.consts.rate_limits import (
    RATE_LIMIT_EXEMPTIONS,
    RATE_LIMIT_EXEMPTION_REASONS,
    RATE_LIMITS,
)

from .rate_limit_acceptance import ACCEPTANCE_PATHS, ORDERS_ONLY_PATHS
from .test_contract import ENDPOINT_PATHS, reachable_paths


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


class TestCoveragePartition(unittest.TestCase):
    """No declared path may escape the limiter without a recorded reason."""

    def test_reachable_paths_are_limited_or_exempt(self):
        uncovered = sorted(reachable_paths() - set(RATE_LIMITS) - set(RATE_LIMIT_EXEMPTIONS))
        self.assertEqual(uncovered, [], f"paths with no rate-limit decision: {uncovered}")

    def test_limited_and_exempt_paths_do_not_overlap(self):
        both = sorted(set(RATE_LIMITS) & set(RATE_LIMIT_EXEMPTIONS))
        self.assertEqual(both, [], f"paths both limited and exempt: {both}")

    def test_exemptions_are_declared_paths(self):
        unknown = sorted(set(RATE_LIMIT_EXEMPTIONS) - ENDPOINT_PATHS)
        self.assertEqual(unknown, [], f"exempt paths not declared in okxsdk/consts: {unknown}")

    def test_exemptions_use_a_known_reason(self):
        unknown = {
            path: reason
            for path, reason in RATE_LIMIT_EXEMPTIONS.items()
            if reason not in RATE_LIMIT_EXEMPTION_REASONS
        }
        self.assertEqual(unknown, {}, f"exemptions with an unknown reason: {unknown}")

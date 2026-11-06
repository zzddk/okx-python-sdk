"""
Unit tests for okxsdk.Affiliate constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okxsdk import consts as c


class TestAffiliateConstants(unittest.TestCase):
    def test_constant_paths(self):
        self.assertEqual(c.AFFILIATE_INVITEE_DETAIL, '/api/v5/affiliate/invitee/detail')
        self.assertEqual(c.AFFILIATE_INVITEE_LIST, '/api/v5/affiliate/invitee/list')
        self.assertEqual(c.AFFILIATE_LINK_LIST, '/api/v5/affiliate/link/list')
        self.assertEqual(c.AFFILIATE_PERFORMANCE_SUMMARY, '/api/v5/affiliate/performance/summary')
        self.assertEqual(c.AFFILIATE_TVB_TIER_BREAKDOWN, '/api/v5/affiliate/tvb/tier-breakdown')


if __name__ == '__main__':
    unittest.main()

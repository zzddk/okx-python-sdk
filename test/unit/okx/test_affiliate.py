"""
Unit tests for okx.Affiliate constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okx import consts as c


class TestAffiliateConstants(unittest.TestCase):
    def test_constant_paths(self):
        self.assertEqual(c.AFFILIATE_TVB_INVITEE_DETAIL, '/api/v5/affiliate/tvb/invitee/detail')
        self.assertEqual(c.AFFILIATE_TVB_INVITEE_LIST, '/api/v5/affiliate/tvb/invitee/list')
        self.assertEqual(c.AFFILIATE_TVB_LINK_LIST, '/api/v5/affiliate/tvb/link/list')
        self.assertEqual(c.AFFILIATE_TVB_PERFORMANCE_SUMMARY, '/api/v5/affiliate/tvb/performance/summary')
        self.assertEqual(c.AFFILIATE_TVB_TIER_BREAKDOWN, '/api/v5/affiliate/tvb/tier-breakdown')


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for okx.Finance.Okusd constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okx import consts as c


class TestOkusdConstants(unittest.TestCase):
    def test_constant_paths(self):
        self.assertEqual(c.OKUSD_ACCOUNT, '/api/v5/finance/okusd/account')
        self.assertEqual(c.OKUSD_RATE_HISTORY, '/api/v5/finance/okusd/rate/history')
        self.assertEqual(c.OKUSD_SUBSCRIBE_HISTORY, '/api/v5/finance/okusd/subscribe/history')
        self.assertEqual(c.OKUSD_REDEEM_HISTORY, '/api/v5/finance/okusd/redeem/history')
        self.assertEqual(c.OKUSD_REWARDS_HISTORY, '/api/v5/finance/okusd/rewards/history')


if __name__ == '__main__':
    unittest.main()

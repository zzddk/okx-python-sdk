"""
Unit tests for okx.DualInvest constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okx import consts as c


class TestDualInvestConstants(unittest.TestCase):
    def test_all_eight_paths_defined(self):
        expected = {
            c.DUAL_INVEST_CURRENCY_PAIRS: '/api/v5/finance/sfp/dcd/currency-pair',
            c.DUAL_INVEST_PRODUCT_INFO: '/api/v5/finance/sfp/dcd/products',
            c.DUAL_INVEST_REQUEST_QUOTE: '/api/v5/finance/sfp/dcd/quote',
            c.DUAL_INVEST_TRADE: '/api/v5/finance/sfp/dcd/trade',
            c.DUAL_INVEST_REQUEST_REDEEM_QUOTE: '/api/v5/finance/sfp/dcd/redeem-quote',
            c.DUAL_INVEST_REDEEM: '/api/v5/finance/sfp/dcd/redeem',
            c.DUAL_INVEST_ORDER_STATE: '/api/v5/finance/sfp/dcd/order-status',
            c.DUAL_INVEST_ORDER_HISTORY: '/api/v5/finance/sfp/dcd/order-history',
        }
        for const_value, path in expected.items():
            self.assertEqual(const_value, path)


if __name__ == '__main__':
    unittest.main()

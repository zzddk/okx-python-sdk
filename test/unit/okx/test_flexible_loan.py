"""
Unit tests for okx.Finance.FlexibleLoan constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okx import consts as c


class TestFlexibleLoanConstants(unittest.TestCase):
    def test_borrow_constant_path(self):
        self.assertEqual(c.FINANCE_FLEXIBLE_LOAN_BORROW,
                         '/api/v5/finance/flexible-loan/borrow')

    def test_repay_constant_path(self):
        self.assertEqual(c.FINANCE_FLEXIBLE_LOAN_REPAY,
                         '/api/v5/finance/flexible-loan/repay')

    def test_emode_info_constant_path(self):
        self.assertEqual(c.FINANCE_FLEXIBLE_LOAN_EMODE_INFO,
                         '/api/v5/finance/flexible-loan/emode-info')


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for okxsdk.Finance.EthStaking constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okxsdk import consts as c


class TestEthStakingConstants(unittest.TestCase):
    def test_cancel_redeem_constant_path(self):
        # constant targets the official cancel-redeem endpoint
        self.assertEqual(
            c.STACK_ETH_CANCEL_REDEEM,
            '/api/v5/finance/staking-defi/eth/cancel-redeem',
        )


if __name__ == '__main__':
    unittest.main()

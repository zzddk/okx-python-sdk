"""
Unit tests for okxsdk.MarketData constants.

The endpoint surface itself is covered by test_endpoint_table.py.
"""
import unittest

from okxsdk import consts as c


class TestMarketConstants(unittest.TestCase):
    def test_books_rpi_constant_path(self):
        self.assertEqual(c.MARKET_BOOKS_RPI, '/api/v5/market/books-rpi')


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for okx.Convert v5 API sync batch (0.4.3) — item #4 convertMode.
"""
import unittest
from unittest.mock import patch
from okx.Convert import ConvertAPI
from okx import consts as c
from .fakes import FakeTransport, assert_request, sent_params

# Placeholder client identifiers — every request is mocked; not real credentials.
_STUB_ID = 'test_key'
_STUB_SIGN = 'test_secret'
_STUB_PHRASE = 'test_pass'


class _Base(unittest.TestCase):
    def setUp(self):
        self.api = ConvertAPI(FakeTransport())


class TestConvertModeBackwardCompatible(_Base):
    @patch.object(ConvertAPI, 'request')
    def test_get_currency_pair_omits_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.get_currency_pair(fromCcy='BTC', toCcy='USDT')
        assert_request(mock_request, c.GET, c.GET_CURRENCY_PAIR, {'fromCcy': 'BTC', 'toCcy': 'USDT'})

    @patch.object(ConvertAPI, 'request')
    def test_estimate_quote_omits_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.estimate_quote(baseCcy='BTC', quoteCcy='USDT', side='buy', rfqSz='1', rfqSzCcy='BTC')
        self.assertNotIn('convertMode', sent_params(mock_request))

    @patch.object(ConvertAPI, 'request')
    def test_convert_trade_omits_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.convert_trade(quoteId='q1', baseCcy='BTC', quoteCcy='USDT', side='buy', sz='1', szCcy='BTC')
        self.assertNotIn('convertMode', sent_params(mock_request))


class TestConvertModeWritten(_Base):
    @patch.object(ConvertAPI, 'request')
    def test_get_currency_pair_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.get_currency_pair(fromCcy='BTC', toCcy='USDT', convertMode='1')
        params = mock_request.call_args[0][2]
        self.assertEqual(params['convertMode'], '1')

    @patch.object(ConvertAPI, 'request')
    def test_estimate_quote_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.estimate_quote(baseCcy='BTC', quoteCcy='USDT', side='buy', convertMode='1')
        self.assertEqual(mock_request.call_args[0][2]['convertMode'], '1')
        self.assertEqual(mock_request.call_args[0][1], c.ESTIMATE_QUOTE)

    @patch.object(ConvertAPI, 'request')
    def test_convert_trade_convertMode(self, mock_request):
        mock_request.return_value = {'code': '0'}
        self.api.convert_trade(quoteId='q1', baseCcy='BTC', quoteCcy='USDT', side='buy', convertMode='1')
        self.assertEqual(mock_request.call_args[0][2]['convertMode'], '1')
        self.assertEqual(mock_request.call_args[0][1], c.CONVERT_TRADE)


if __name__ == '__main__':
    unittest.main()

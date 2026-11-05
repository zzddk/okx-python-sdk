"""
Unit tests for okx.Account module: the parts the endpoint table cannot state.

Which (method, path, params) each endpoint sends is covered by
test_endpoint_table.py. What remains here is value and signature semantics:
None is not sent, while False / 0 / [] are; positional callers still bind.

Mirrors the structure: okx/Account.py -> test/unit/okx/test_account.py
"""
import unittest
from unittest.mock import patch

from okx import consts as c
from okx.Account import AccountAPI

from .fakes import FakeTransport, assert_request


class TestAccountAPIPositionBuilderParameterHandling(unittest.TestCase):
    """Test parameter handling and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.account_api = AccountAPI(FakeTransport())

    @patch.object(AccountAPI, 'request')
    def test_none_parameters_are_excluded(self, mock_request):
        """Test that None parameters are not included in the request"""
        # Arrange
        mock_response = {'code': '0', 'msg': '', 'data': []}
        mock_request.return_value = mock_response

        # Act
        self.account_api.position_builder(
            acctLv='2',
            inclRealPosAndEq=None,  # Should be excluded
            lever=None,  # Should be excluded
            greeksType='PA',
            simPos=None,  # Should be excluded
            simAsset=None,  # Should be excluded
            idxVol='0.05'
        )

        # Assert - Only non-None params should be in the call
        expected_params = {
            'acctLv': '2',
            'greeksType': 'PA',
            'idxVol': '0.05'
        }
        assert_request(mock_request, c.POST, c.POSITION_BUILDER, expected_params)

    @patch.object(AccountAPI, 'request')
    def test_false_value_for_inclRealPosAndEq_is_included(self, mock_request):
        """Test that False value for inclRealPosAndEq is included (not treated as None)"""
        # Arrange
        mock_response = {'code': '0', 'msg': '', 'data': []}
        mock_request.return_value = mock_response

        # Act
        self.account_api.position_builder(inclRealPosAndEq=False)

        # Assert - False should be included
        expected_params = {
            'inclRealPosAndEq': False
        }
        assert_request(mock_request, c.POST, c.POSITION_BUILDER, expected_params)

    @patch.object(AccountAPI, 'request')
    def test_empty_lists_are_included(self, mock_request):
        """Test that empty lists are included in the request"""
        # Arrange
        mock_response = {'code': '0', 'msg': '', 'data': []}
        mock_request.return_value = mock_response

        # Act
        self.account_api.position_builder(
            simPos=[],
            simAsset=[]
        )

        # Assert
        expected_params = {
            'simPos': [],
            'simAsset': []
        }
        assert_request(mock_request, c.POST, c.POSITION_BUILDER, expected_params)

    @patch.object(AccountAPI, 'request')
    def test_zero_idxVol_is_included(self, mock_request):
        """Test that zero idxVol is included (represents no volatility change)"""
        # Arrange
        mock_response = {'code': '0', 'msg': '', 'data': []}
        mock_request.return_value = mock_response

        # Act
        self.account_api.position_builder(idxVol='0')

        # Assert
        expected_params = {
            'idxVol': '0'
        }
        assert_request(mock_request, c.POST, c.POSITION_BUILDER, expected_params)


class TestAccountAPIGetAccountBills(unittest.TestCase):
    """Signature and cross-endpoint symmetry for get_account_bills (GH#141)"""

    def setUp(self):
        """Set up test fixtures"""
        self.account_api = AccountAPI(FakeTransport())

    @patch.object(AccountAPI, 'request')
    def test_get_account_bills_positional_backward_compatible(self, mock_request):
        """Legacy positional callers (up to limit) still bind correctly"""
        mock_response = {'code': '0', 'msg': '', 'data': []}
        mock_request.return_value = mock_response

        # instType, ccy, mgnMode, ctType, type, subType, after, before, limit
        self.account_api.get_account_bills('SPOT', 'BTC', 'cross', '', '1', '', '', '', '10')

        call_args = mock_request.call_args[0][2]
        self.assertEqual(call_args['instType'], 'SPOT')
        self.assertEqual(call_args['ccy'], 'BTC')
        self.assertEqual(call_args['limit'], '10')
        # New params default to None -> identical request to today
        self.assertEqual(call_args['begin'], None)
        self.assertEqual(call_args['end'], None)

    @patch.object(AccountAPI, 'request')
    def test_get_account_bills_mirrors_archive_param_keys(self, mock_request):
        """get_account_bills param keys match get_account_bills_archive (GH#141 symmetry)"""
        mock_request.return_value = {'code': '0', 'msg': '', 'data': []}

        self.account_api.get_account_bills(begin='1', end='2')
        bills_keys = set(mock_request.call_args[0][2].keys())

        mock_request.reset_mock()
        self.account_api.get_account_bills_archive(begin='1', end='2')
        archive_keys = set(mock_request.call_args[0][2].keys())

        self.assertEqual(bills_keys, archive_keys)


class TestAccountAPIGlpPerformance(unittest.TestCase):
    """GLP path constants (TD 0.4.4 items #2-3)"""

    def test_glp_constant_paths(self):
        self.assertEqual(c.GLP_HISTORICAL_PERFORMANCE, '/api/v5/users/glp/historicalperformance')
        self.assertEqual(c.GLP_TODAY_PERFORMANCE, '/api/v5/users/glp/todayperformance')


if __name__ == '__main__':
    unittest.main()

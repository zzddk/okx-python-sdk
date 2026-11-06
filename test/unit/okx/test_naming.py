"""Public naming contract: the 0.5.0 renames leave no aliases behind."""

from unittest.mock import patch

import pytest

from okx import consts as c
from okx import exceptions
from okx.Account import AccountAPI
from okx.Affiliate import AffiliateAPI
from okx.PublicData import PublicAPI
from okx.SubAccount import SubAccountAPI

from .fakes import FakeTransport

RENAMED_CONSTANTS = {
    "ACEEPT": "ACCEPT",
    "ACTIVSTE_OPTION": "ACTIVATE_OPTION",
    "INDEX_CANSLES": "INDEX_CANDLES",
    "VOLUMNE": "VOLUME",
    "PLACR_ORDER": "PLACE_ORDER",
    "BILLs": "SUBACCOUNT_BILLS",
    "SET_TRSNSFER_OUT": "SET_TRANSFER_OUT",
    "DICCOUNT_INTETEST_INFO": "DISCOUNT_INTEREST_INFO",
    "GET_DEPOSIT_WITHDrAW_STATUS": "GET_DEPOSIT_WITHDRAW_STATUS",
    "GRID_COMPUTE_MARIGIN_BALANCE": "GRID_COMPUTE_MARGIN_BALANCE",
    "CANCEL_ALL_RSQS": "CANCEL_ALL_RFQS",
    "MARKER_INSTRUMENT_SETTING": "MAKER_INSTRUMENT_SETTING",
    "AFFILIATE_TVB_INVITEE_DETAIL": "AFFILIATE_INVITEE_DETAIL",
    "AFFILIATE_TVB_INVITEE_LIST": "AFFILIATE_INVITEE_LIST",
    "AFFILIATE_TVB_LINK_LIST": "AFFILIATE_LINK_LIST",
    "AFFILIATE_TVB_PERFORMANCE_SUMMARY": "AFFILIATE_PERFORMANCE_SUMMARY",
}

REMOVED_EXCEPTIONS = ["OkxRequestException", "OkxParamsException"]

RENAMED_METHODS = [
    (PublicAPI, "get_option_tickBands", "get_option_tickbands"),
    (SubAccountAPI, "subAccount_transfer", "subaccount_transfer"),
    (SubAccountAPI, "set_sub_accounts_VIP_loan", "set_sub_accounts_vip_loan"),
    (AffiliateAPI, "get_tvb_invitee_detail", "get_invitee_detail"),
    (AffiliateAPI, "get_tvb_invitee_list", "get_invitee_list"),
    (AffiliateAPI, "get_tvb_link_list", "get_link_list"),
    (AffiliateAPI, "get_tvb_performance_summary", "get_performance_summary"),
]


@pytest.mark.parametrize("name", REMOVED_EXCEPTIONS)
def test_removed_exception_has_no_alias(name):
    assert not hasattr(exceptions, name)


@pytest.mark.parametrize("old, new", RENAMED_CONSTANTS.items())
def test_renamed_constant_has_no_alias(old, new):
    assert not hasattr(c, old)
    assert hasattr(c, new)


@pytest.mark.parametrize("cls, old, new", RENAMED_METHODS)
def test_renamed_method_has_no_alias(cls, old, new):
    assert not hasattr(cls, old)
    assert hasattr(cls, new)


def test_get_instruments_sends_uly_not_ugly():
    api = AccountAPI(FakeTransport())
    with patch.object(AccountAPI, "request") as mock_request:
        mock_request.return_value = {"code": "0"}
        api.get_instruments(instType="SWAP", uly="BTC-USDT")

    params = mock_request.call_args[0][2]
    assert params["uly"] == "BTC-USDT"
    assert "ugly" not in params

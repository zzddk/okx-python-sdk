"""Public naming contract: the 0.5.0 renames leave no aliases behind."""

from unittest.mock import patch

import pytest

from okx import consts as c
from okx.Account import AccountAPI
from okx.PublicData import PublicAPI
from okx.SubAccount import SubAccountAPI

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
}

RENAMED_METHODS = [
    (AccountAPI, "set_risk_offset_typel", "set_risk_offset_type"),
    (AccountAPI, "get_VIP_interest_accrued_data", "get_vip_interest_accrued_data"),
    (AccountAPI, "get_VIP_interest_deducted_data", "get_vip_interest_deducted_data"),
    (AccountAPI, "get_VIP_loan_order_list", "get_vip_loan_order_list"),
    (AccountAPI, "get_VIP_loan_order_detail", "get_vip_loan_order_detail"),
    (PublicAPI, "get_option_tickBands", "get_option_tickbands"),
    (SubAccountAPI, "subAccount_transfer", "subaccount_transfer"),
    (SubAccountAPI, "set_sub_accounts_VIP_loan", "set_sub_accounts_vip_loan"),
]


@pytest.mark.parametrize("old, new", RENAMED_CONSTANTS.items())
def test_renamed_constant_has_no_alias(old, new):
    assert not hasattr(c, old)
    assert hasattr(c, new)


@pytest.mark.parametrize("cls, old, new", RENAMED_METHODS)
def test_renamed_method_has_no_alias(cls, old, new):
    assert not hasattr(cls, old)
    assert hasattr(cls, new)


def test_get_instruments_sends_uly_not_ugly():
    api = AccountAPI(api_key="k", api_secret_key="s", passphrase="p", flag="0")
    with patch.object(AccountAPI, "_request_with_params") as mock_request:
        mock_request.return_value = {"code": "0"}
        api.get_instruments(instType="SWAP", uly="BTC-USDT")

    params = mock_request.call_args[0][2]
    assert params["uly"] == "BTC-USDT"
    assert "ugly" not in params

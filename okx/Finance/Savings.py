from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import *


class SavingsAPI(OkxClient):
    # - Get saving balance
    def get_saving_balance(self, ccy: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy
        }
        return self._request_with_params(GET, GET_SAVING_BALANCE, params)

    # - Savings purchase/redemption
    def savings_purchase_redemption(self, ccy: Any = None, amt: Any = None, side: Any = None, rate: Any = None) -> Dict[str, Any]:

        params = {
            'ccy': ccy,
            'amt': amt,
            'side': side,
            'rate': rate
        }
        return self._request_with_params(POST, SAVING_PURCHASE_REDEMPTION, params)

    # - Set lending rate
    def set_lending_rate(self, ccy: Any = None, rate: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy,
            'rate': rate
        }
        return self._request_with_params(POST, SET_LENDING_RATE, params)

    # - Get lending history
    def get_lending_history(self, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, GET_LENDING_HISTORY, params)

    # - Get public borrow history (public)
    def get_public_borrow_history(self, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, GET_PUBLIC_BORROW_HISTORY, params)

    # GET / Public borrow info (public)
    def get_public_borrow_info(self, ccy: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy
        }
        return self._request_with_params(GET, GET_PUBLIC_BORROW_INFO, params)



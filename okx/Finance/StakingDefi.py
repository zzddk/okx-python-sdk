from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import *


class StakingDefiAPI(OkxClient):
    def get_offers(self, productId: Any = None, protocolType: Any = None, ccy: Any = None) -> Dict[str, Any]:
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy
        }
        return self._request_with_params(GET, STACK_DEFI_OFFERS, params)

    def purchase(self, productId: Any = None, investData: Any = None, term: Any = None, tag: Any = None) -> Dict[str, Any]:
        if investData is None:
            investData = []
        params = {
            'productId': productId,
            'investData': investData
        }
        if term is not None:
            params['term'] = term
        if tag is not None:
            params['tag'] = tag
        return self._request_with_params(POST, STACK_DEFI_PURCHASE, params)

    def redeem(self, ordId: Any = None, protocolType: Any = None, allowEarlyRedeem: Any = None) -> Dict[str, Any]:
        params = {
            'ordId': ordId,
            'protocolType': protocolType,
            'allowEarlyRedeem': allowEarlyRedeem
        }
        return self._request_with_params(POST, STACK_DEFI_REDEEM, params)

    def cancel(self, ordId: Any = None, protocolType: Any = None) -> Dict[str, Any]:
        params = {
            'ordId': ordId,
            'protocolType': protocolType
        }
        return self._request_with_params(POST, STACK_DEFI_CANCEL, params)

    def get_activity_orders(self, productId: Any = None, protocolType: Any = None, ccy: Any = None, state: Any = None) -> Dict[str, Any]:
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy,
            'state': state
        }
        return self._request_with_params(GET, STACK_DEFI_ORDERS_ACTIVITY, params)

    def get_orders_history(self, productId: Any = None, protocolType: Any = None, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, STACK_DEFI_ORDERS_HISTORY, params)


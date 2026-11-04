from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import *


class EthStakingAPI(OkxClient):
    def eth_product_info(self) -> Dict[str, Any]:

        return self._request_without_params(GET, STACK_ETH_PRODUCT_INFO)

    def eth_purchase(self, amt: Any = None) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self._request_with_params(POST, STACK_ETH_PURCHASE, params)

    def eth_redeem(self, amt: Any = None) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self._request_with_params(POST, STACK_ETH_REDEEM, params)

    def eth_cancel_redeem(self, ordId: Any = None) -> Dict[str, Any]:

        params = {
            'ordId': ordId,
        }
        return self._request_with_params(POST, STACK_ETH_CANCEL_REDEEM, params)

    def eth_balance(self) -> Dict[str, Any]:

        params = {}
        return self._request_with_params(GET, STACK_ETH_BALANCE, params)

    def eth_purchase_redeem_history(self, type: Any = None, status: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:

        params = {}
        if type is not None:
            params['type'] = type
        if status is not None:
            params['status'] = status
        if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, STACK_ETH_PURCHASE_REDEEM_HISTORY, params)

    def eth_apy_history(self, days: Any) -> Dict[str, Any]:

        params = {
            'days': days,
        }
        return self._request_with_params(GET, STACK_ETH_APY_HISTORY, params)

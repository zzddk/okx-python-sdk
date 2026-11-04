from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import *


class SolStakingAPI(OkxClient):
    def sol_purchase(self, amt: Any) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self.request(POST, STACK_SOL_PURCHASE, params)

    def sol_redeem(self, amt: Any = None) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self.request(POST, STACK_SOL_REDEEM, params)

    def sol_balance(self) -> Dict[str, Any]:

        params = {}
        return self.request(GET, STACK_SOL_BALANCE, params)

    def sol_purchase_redeem_history(self, type: Any = None, status: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:

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
        return self.request(GET, STACK_SOL_PURCHASE_REDEEM_HISTORY, params)

    def sol_apy_history(self, days: Any) -> Dict[str, Any]:

        params = {
            'days': days,
        }
        return self.request(GET, STACK_SOL_APY_HISTORY, params)

    def sol_product_info(self) -> Dict[str, Any]:
        return self.request(GET, STACK_SOL_PRODUCT_INFO)

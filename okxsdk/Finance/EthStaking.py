from typing import Any, Dict

from okxsdk.okxclient import OkxClient
from okxsdk.consts import *


class EthStakingAPI(OkxClient):
    def eth_product_info(self) -> Dict[str, Any]:

        return self.request(GET, STACK_ETH_PRODUCT_INFO)

    def eth_purchase(self, amt: Any = None) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self.request(POST, STACK_ETH_PURCHASE, params)

    def eth_redeem(self, amt: Any = None) -> Dict[str, Any]:

        params = {
            'amt': amt,
        }
        return self.request(POST, STACK_ETH_REDEEM, params)

    def eth_cancel_redeem(self, ordId: Any = None) -> Dict[str, Any]:

        params = {
            'ordId': ordId,
        }
        return self.request(POST, STACK_ETH_CANCEL_REDEEM, params)

    def eth_balance(self) -> Dict[str, Any]:

        params = {}
        return self.request(GET, STACK_ETH_BALANCE, params)

    def eth_purchase_redeem_history(self, type: Any = None, status: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:

        params = {'type': type, 'status': status, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, STACK_ETH_PURCHASE_REDEEM_HISTORY, params)

    def eth_apy_history(self, days: Any) -> Dict[str, Any]:

        params = {
            'days': days,
        }
        return self.request(GET, STACK_ETH_APY_HISTORY, params)

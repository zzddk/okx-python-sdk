from okx.okxclient import OkxClient
from okx.consts import *


class SolStakingAPI(OkxClient):
    def sol_purchase(self, amt):

        params = {
            'amt': amt,
        }
        return self._request_with_params(POST, STACK_SOL_PURCHASE, params)

    def sol_redeem(self, amt=''):

        params = {
            'amt': amt,
        }
        return self._request_with_params(POST, STACK_SOL_REDEEM, params)

    def sol_balance(self):

        params = {}
        return self._request_with_params(GET, STACK_SOL_BALANCE, params)

    def sol_purchase_redeem_history(self, type='', status='', after='', before='', limit=''):

        params = {}
        if type != '':
            params['type'] = type
        if status != '':
            params['status'] = status
        if after != '':
            params['after'] = after
        if before != '':
            params['before'] = before
        if limit != '':
            params['limit'] = limit
        return self._request_with_params(GET, STACK_SOL_PURCHASE_REDEEM_HISTORY, params)

    def sol_apy_history(self, days):

        params = {
            'days': days,
        }
        return self._request_with_params(GET, STACK_SOL_APY_HISTORY, params)

    def sol_product_info(self):
        return self._request_without_params(GET, STACK_SOL_PRODUCT_INFO)

from okx.okxclient import OkxClient
from okx.consts import *


class StakingDefiAPI(OkxClient):
    def get_offers(self, productId='', protocolType='', ccy=''):
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy
        }
        return self._request_with_params(GET, STACK_DEFI_OFFERS, params)

    def purchase(self, productId='', investData=None, term='', tag=''):
        if investData is None:
            investData = []
        params = {
            'productId': productId,
            'investData': investData
        }
        if term != '':
            params['term'] = term
        if tag != '':
            params['tag'] = tag
        return self._request_with_params(POST, STACK_DEFI_PURCHASE, params)

    def redeem(self, ordId='', protocolType='', allowEarlyRedeem=''):
        params = {
            'ordId': ordId,
            'protocolType': protocolType,
            'allowEarlyRedeem': allowEarlyRedeem
        }
        return self._request_with_params(POST, STACK_DEFI_REDEEM, params)

    def cancel(self, ordId='', protocolType=''):
        params = {
            'ordId': ordId,
            'protocolType': protocolType
        }
        return self._request_with_params(POST, STACK_DEFI_CANCEL, params)

    def get_activity_orders(self, productId='', protocolType='', ccy='', state=''):
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy,
            'state': state
        }
        return self._request_with_params(GET, STACK_DEFI_ORDERS_ACTIVITY, params)

    def get_orders_history(self, productId='', protocolType='', ccy='', after='', before='', limit=''):
        params = {
            'productId': productId,
            'protocolType': protocolType,
            'ccy': ccy,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, STACK_DEFI_ORDERS_HISTORY, params)


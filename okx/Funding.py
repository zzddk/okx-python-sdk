from .okxclient import OkxClient
from .consts import *


class FundingAPI(OkxClient):


    # Get Non Tradable Assets
    def get_non_tradable_assets(self, ccy: str = None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, NON_TRADABLE_ASSETS, params)

    # Get Deposit Address
    def get_deposit_address(self, ccy):
        params = {'ccy': ccy}
        return self._request_with_params(GET, DEPOSIT_ADDRESS, params)

    # Get Transfer State
    def transfer_state(self, transId,type = None):
        params = {'transId': transId, 'type': type}
        return self._request_with_params(GET, TRANSFER_STATE, params)

    # Get Balance
    def get_balances(self, ccy = None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, GET_BALANCES, params)

    # Get Account Configuration
    def funds_transfer(self, ccy, amt, from_, to, type='0', subAcct = None, instId = None, toInstId = None,loanTrans = None):
        params = {'ccy': ccy, 'amt': amt, 'from': from_, 'to': to, 'type': type, 'subAcct': subAcct, 'instId': instId,
                  'toInstId': toInstId,'loanTrans':loanTrans}
        return self._request_with_params(POST, FUNDS_TRANSFER, params)

    # Withdrawal
    def withdrawal(self, ccy, amt, dest, toAddr, chain = None, areaCode = None, clientId = None, toAddrType = None):
        params = {'ccy': ccy, 'amt': amt, 'dest': dest, 'toAddr': toAddr, 'chain': chain,
                  'areaCode': areaCode, 'clientId': clientId}
        if toAddrType is not None:
            params['toAddrType'] = toAddrType
        return self._request_with_params(POST, WITHDRAWAL_COIN, params)

    # Get Deposit History
    def get_deposit_history(self, ccy = None, type = None, state = None, after = None, before = None, limit = None, txId = None, depId = None, fromWdId = None):
        params = {'ccy': ccy, 'type': type, 'state': state, 'after': after, 'before': before, 'limit': limit, 'txId': txId,
                  'depId': depId, 'fromWdId': fromWdId}
        return self._request_with_params(GET, DEPOSIT_HISTORY, params)



    # Get Currencies
    def get_currencies(self, ccy = None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, CURRENCY_INFO, params)

    # PiggyBank Purchase/Redemption
    def purchase_redempt(self, ccy, amt, side, rate):
        params = {'ccy': ccy, 'amt': amt, 'side': side,'rate':rate}
        return self._request_with_params(POST, PURCHASE_REDEMPT, params)

    # Get Withdrawal History
    def get_bills(self, ccy = None, type = None, after = None, before = None, limit = None):
        params = {'ccy': ccy, 'type': type, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLS_INFO, params)


    #Get Deposit Lightning
    def get_deposit_lightning(self, ccy,amt,to=""):
        params = {'ccy':ccy,'amt':amt}
        if to is not None:
            params = {'to':to}
        return self._request_with_params(GET, DEPOSIT_LIGHTNING, params)

    # Withdrawal Lightning
    def withdrawal_lightning(self, ccy,invoice,memo = None):
        params = {'ccy':ccy, 'invoice':invoice, 'memo':memo}
        return self._request_with_params(POST, WITHDRAWAL_LIGHTNING, params)

    #POST /api/v5/asset/cancel-withdrawal
    def cancel_withdrawal(self,wdId = None):
        params = {
            'wdId':wdId
        }
        return self._request_with_params(POST, CANCEL_WITHDRAWAL, params)

    #POST /api/v5/asset/convert-dust-assets
    def convert_dust_assets(self,ccy = []):
        params = {
            'ccy':ccy
        }
        return self._request_with_params(POST, CONVERT_DUST_ASSETS, params)

    #GET /api/v5/asset/asset-valuation
    def get_asset_valuation(self,ccy = None):
        params = {
            'ccy':ccy
        }
        return self._request_with_params(GET, ASSET_VALUATION, params)

    #Get non-tradable assets
    def get_non_tradable_assets(self, ccy = None):
        params = {
            'ccy': ccy
        }
        return self._request_with_params(GET, GET_NON_TRADABLE_ASSETS, params)

    #Get deposit withdraw status
    def get_deposit_withdraw_status(self, wdId = None, txId = None, ccy = None, to = None, chain = None):
        params = {'wdId': wdId, 'txId': txId, 'ccy': ccy, 'to': to, 'chain': chain}
        return self._request_with_params(GET, GET_DEPOSIT_WITHDRAW_STATUS, params)

    #Get withdrawal history
    def get_withdrawal_history(self, ccy = None, wdId = None, clientId = None, txId = None, type = None, state = None, after = None, before = None, limit = None, toAddrType = None):
        params = {'ccy': ccy, 'wdId': wdId, 'clientId': clientId, 'txId': txId, 'type': type, 'state': state, 'after': after, 'before': before, 'limit': limit}
        if toAddrType is not None:
            params['toAddrType'] = toAddrType
        return self._request_with_params(GET, GET_WITHDRAWAL_HISTORY, params)


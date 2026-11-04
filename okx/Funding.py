from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class FundingAPI(OkxClient):


    # Get Non Tradable Assets
    def get_non_tradable_assets(self, ccy: str = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, NON_TRADABLE_ASSETS, params)

    # Get Deposit Address
    def get_deposit_address(self, ccy: Any) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, DEPOSIT_ADDRESS, params)

    # Get Transfer State
    def transfer_state(self, transId: Any,type: Any = None) -> Dict[str, Any]:
        params = {'transId': transId, 'type': type}
        return self._request_with_params(GET, TRANSFER_STATE, params)

    # Get Balance
    def get_balances(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, GET_BALANCES, params)

    # Get Account Configuration
    def funds_transfer(self, ccy: Any, amt: Any, from_: Any, to: Any, type: Any='0', subAcct: Any = None, instId: Any = None, toInstId: Any = None,loanTrans: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'amt': amt, 'from': from_, 'to': to, 'type': type, 'subAcct': subAcct, 'instId': instId,
                  'toInstId': toInstId,'loanTrans':loanTrans}
        return self._request_with_params(POST, FUNDS_TRANSFER, params)

    # Withdrawal
    def withdrawal(self, ccy: Any, amt: Any, dest: Any, toAddr: Any, chain: Any = None, areaCode: Any = None, clientId: Any = None, toAddrType: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'amt': amt, 'dest': dest, 'toAddr': toAddr, 'chain': chain,
                  'areaCode': areaCode, 'clientId': clientId}
        if toAddrType is not None:
            params['toAddrType'] = toAddrType
        return self._request_with_params(POST, WITHDRAWAL_COIN, params)

    # Get Deposit History
    def get_deposit_history(self, ccy: Any = None, type: Any = None, state: Any = None, after: Any = None, before: Any = None, limit: Any = None, txId: Any = None, depId: Any = None, fromWdId: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'type': type, 'state': state, 'after': after, 'before': before, 'limit': limit, 'txId': txId,
                  'depId': depId, 'fromWdId': fromWdId}
        return self._request_with_params(GET, DEPOSIT_HISTORY, params)



    # Get Currencies
    def get_currencies(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, CURRENCY_INFO, params)

    # PiggyBank Purchase/Redemption
    def purchase_redempt(self, ccy: Any, amt: Any, side: Any, rate: Any) -> Dict[str, Any]:
        params = {'ccy': ccy, 'amt': amt, 'side': side,'rate':rate}
        return self._request_with_params(POST, PURCHASE_REDEMPT, params)

    # Get Withdrawal History
    def get_bills(self, ccy: Any = None, type: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'type': type, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLS_INFO, params)


    #Get Deposit Lightning
    def get_deposit_lightning(self, ccy: Any,amt: Any,to: Any="") -> Dict[str, Any]:
        params = {'ccy':ccy,'amt':amt}
        if to is not None:
            params = {'to':to}
        return self._request_with_params(GET, DEPOSIT_LIGHTNING, params)

    # Withdrawal Lightning
    def withdrawal_lightning(self, ccy: Any,invoice: Any,memo: Any = None) -> Dict[str, Any]:
        params = {'ccy':ccy, 'invoice':invoice, 'memo':memo}
        return self._request_with_params(POST, WITHDRAWAL_LIGHTNING, params)

    #POST /api/v5/asset/cancel-withdrawal
    def cancel_withdrawal(self,wdId: Any = None) -> Dict[str, Any]:
        params = {
            'wdId':wdId
        }
        return self._request_with_params(POST, CANCEL_WITHDRAWAL, params)

    #POST /api/v5/asset/convert-dust-assets
    def convert_dust_assets(self,ccy: Any = []) -> Dict[str, Any]:
        params = {
            'ccy':ccy
        }
        return self._request_with_params(POST, CONVERT_DUST_ASSETS, params)

    #GET /api/v5/asset/asset-valuation
    def get_asset_valuation(self,ccy: Any = None) -> Dict[str, Any]:
        params = {
            'ccy':ccy
        }
        return self._request_with_params(GET, ASSET_VALUATION, params)

    #Get non-tradable assets
    def get_non_tradable_assets(self, ccy: Any = None) -> Dict[str, Any]:
        params = {
            'ccy': ccy
        }
        return self._request_with_params(GET, GET_NON_TRADABLE_ASSETS, params)

    #Get deposit withdraw status
    def get_deposit_withdraw_status(self, wdId: Any = None, txId: Any = None, ccy: Any = None, to: Any = None, chain: Any = None) -> Dict[str, Any]:
        params = {'wdId': wdId, 'txId': txId, 'ccy': ccy, 'to': to, 'chain': chain}
        return self._request_with_params(GET, GET_DEPOSIT_WITHDRAW_STATUS, params)

    #Get withdrawal history
    def get_withdrawal_history(self, ccy: Any = None, wdId: Any = None, clientId: Any = None, txId: Any = None, type: Any = None, state: Any = None, after: Any = None, before: Any = None, limit: Any = None, toAddrType: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'wdId': wdId, 'clientId': clientId, 'txId': txId, 'type': type, 'state': state, 'after': after, 'before': before, 'limit': limit}
        if toAddrType is not None:
            params['toAddrType'] = toAddrType
        return self._request_with_params(GET, GET_WITHDRAWAL_HISTORY, params)


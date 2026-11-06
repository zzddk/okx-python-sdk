from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class SubAccountAPI(OkxClient):
    def get_account_balance(self, subAcct: Any) -> Dict[str, Any]:
        params = {"subAcct": subAcct}
        return self.request(GET, BALANCE, params)

    def bills(self, ccy: Any = None, type: Any = None, subAcct: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {"ccy": ccy, 'type': type, 'subAcct': subAcct, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, SUBACCOUNT_BILLS, params)


    def reset_subaccount_apikey(self, subAcct: Any,apiKey: Any, label: Any = None, perm: Any = None, ip: Any='-1') -> Dict[str, Any]:
        params = {'subAcct': subAcct, 'apiKey': apiKey, 'label': label, 'perm': perm}
        if ip != '-1':
            params['ip'] = ip
        return self.request(POST, RESET, params)


    def get_subaccount_list(self, enable: Any = None, subAcct: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'enable': enable, 'subAcct': subAcct, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, VIEW_LIST, params)

    def subaccount_transfer(self, ccy: Any, amt: Any, froms: Any, to: Any, fromSubAccount: Any,toSubAccount: Any,loanTrans: Any='false',omitPosRisk: Any = 'false') -> Dict[str, Any]:
        params = {'ccy': ccy, 'amt': amt, 'from': froms, 'to': to, 'fromSubAccount': fromSubAccount, 'toSubAccount': toSubAccount,'loanTrans':loanTrans,'omitPosRisk':omitPosRisk}
        return self.request(POST, SUBACCOUNT_TRANSFER, params)

    #GET /api/v5/users/entrust-subaccount-list
    def get_entrust_subaccount_list(self,subAcct: Any = None) -> Dict[str, Any]:
        params = {
            'subAcct':subAcct
        }
        return self.request(GET, ENTRUST_SUBACCOUNT_LIST, params)

    #POST /api/v5/users/subaccount/set-transfer-out
    def set_permission_transfer_out(self,subAcct: Any = None,canTransOut: Any = None) -> Dict[str, Any]:
        params = {
            'subAcct':subAcct,
            'canTransOut':canTransOut
        }
        return self.request(POST, SET_TRANSFER_OUT, params)

    #GET /api/v5/asset/subaccount/balances
    def get_funding_balance(self,subAcct: Any = None,ccy: Any = None) -> Dict[str, Any]:
        params = {
            'subAcct':subAcct,
            'ccy':ccy
        }
        return self.request(GET, GET_ASSET_SUBACCOUNT_BALANCE, params)

    # - Set sub_accounts VIP loan%
    def set_sub_accounts_vip_loan(self, enable: Any = None, alloc: Any = []) -> Dict[str, Any]:
        params = {
            'enable': enable,
            'alloc': alloc
        }
        return self.request(POST, SET_SUB_ACCOUNTS_VIP_LOAN, params)

    # - Get sub_account borrow interest and limit
    def get_sub_account_borrow_interest_and_limit(self, subAcct: Any = None, ccy: Any = None) -> Dict[str, Any]:
        params = {
            'subAcct': subAcct,
            'ccy': ccy
        }
        return self.request(GET, GET_SUB_ACCOUNT_BORROW_INTEREST_AND_LIMIT, params)

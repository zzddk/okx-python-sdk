from okx.okxclient import OkxClient
from okx.consts import *


class FlexibleLoanAPI(OkxClient):
    def borrow_currencies(self):
        return self._request_without_params(GET, FINANCE_BORROW_CURRENCIES)

    def collateral_assets(self, ccy = None):
        params = {}
        if ccy is not None:
            params['ccy'] = ccy
        return self._request_with_params(GET, FINANCE_COLLATERAL_ASSETS, params)

    def max_loan(self, borrowCcy = None, supCollateral = None):
        if supCollateral is None:
            supCollateral = []
        params = {
            'borrowCcy': borrowCcy,
            'supCollateral': supCollateral,
        }
        return self._request_with_params(POST, FINANCE_MAX_LOAN, params)

    def max_collateral_redeem_amount(self, ccy = None):
        params = {}
        if ccy is not None:
            params['ccy'] = ccy
        return self._request_with_params(GET, FINANCE_MAX_REDEEM, params)

    def adjust_collateral(self, type = None, collateralCcy = None, collateralAmt = None):
        params = {
            'type': type,
            'collateralCcy': collateralCcy,
            'collateralAmt': collateralAmt,
        }
        return self._request_with_params(POST, FINANCE_ADJUST_COLLATERAL, params)

    def loan_info(self):
        return self._request_without_params(GET, FINANCE_LOAN_INFO)

    def loan_history(self, type = None, after = None, before = None, limit = None):
        params = {}
        if type is not None:
            params['type'] = type
        if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, FINANCE_LOAN_HISTORY, params)

    def interest_accrued(self, ccy = None, after = None, before = None, limit = None):
        params = {}
        if ccy is not None:
            params['ccy'] = ccy
        if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, FINANCE_INTEREST_ACCRUED, params)

    def borrow(self, loanData, clOrdId, ordId = None, collateralData = None, eMode = None):
        params = {
            'loanData': loanData,
            'clOrdId': clOrdId,
        }
        if ordId is not None:
            params['ordId'] = ordId
        if collateralData is not None:
            params['collateralData'] = collateralData
        if eMode is not None:
            params['eMode'] = eMode
        return self._request_with_params(POST, FINANCE_FLEXIBLE_LOAN_BORROW, params)

    def repay(self, ordId, ccy, amt, clOrdId):
        params = {
            'ordId': ordId,
            'ccy': ccy,
            'amt': amt,
            'clOrdId': clOrdId,
        }
        return self._request_with_params(POST, FINANCE_FLEXIBLE_LOAN_REPAY, params)

    def emode_info(self):
        return self._request_without_params(GET, FINANCE_FLEXIBLE_LOAN_EMODE_INFO)

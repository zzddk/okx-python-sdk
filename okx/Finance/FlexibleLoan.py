from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import *


class FlexibleLoanAPI(OkxClient):
    def borrow_currencies(self) -> Dict[str, Any]:
        return self.request(GET, FINANCE_BORROW_CURRENCIES)

    def collateral_assets(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self.request(GET, FINANCE_COLLATERAL_ASSETS, params)

    def max_loan(self, borrowCcy: Any = None, supCollateral: Any = []) -> Dict[str, Any]:
        params = {
            'borrowCcy': borrowCcy,
            'supCollateral': supCollateral,
        }
        return self.request(POST, FINANCE_MAX_LOAN, params)

    def max_collateral_redeem_amount(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self.request(GET, FINANCE_MAX_REDEEM, params)

    def adjust_collateral(self, type: Any = None, collateralCcy: Any = None, collateralAmt: Any = None) -> Dict[str, Any]:
        params = {
            'type': type,
            'collateralCcy': collateralCcy,
            'collateralAmt': collateralAmt,
        }
        return self.request(POST, FINANCE_ADJUST_COLLATERAL, params)

    def loan_info(self) -> Dict[str, Any]:
        return self.request(GET, FINANCE_LOAN_INFO)

    def loan_history(self, type: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'type': type, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, FINANCE_LOAN_HISTORY, params)

    def interest_accrued(self, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, FINANCE_INTEREST_ACCRUED, params)

    def borrow(self, loanData: Any, clOrdId: Any, ordId: Any = None, collateralData: Any = None, eMode: Any = None) -> Dict[str, Any]:
        params = {'loanData': loanData, 'clOrdId': clOrdId, 'ordId': ordId, 'collateralData': collateralData,
                  'eMode': eMode}
        return self.request(POST, FINANCE_FLEXIBLE_LOAN_BORROW, params)

    def repay(self, ordId: Any, ccy: Any, amt: Any, clOrdId: Any) -> Dict[str, Any]:
        params = {
            'ordId': ordId,
            'ccy': ccy,
            'amt': amt,
            'clOrdId': clOrdId,
        }
        return self.request(POST, FINANCE_FLEXIBLE_LOAN_REPAY, params)

    def emode_info(self) -> Dict[str, Any]:
        return self.request(GET, FINANCE_FLEXIBLE_LOAN_EMODE_INFO)

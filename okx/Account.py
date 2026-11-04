from typing import Any, Dict

from .consts import *
from .okxclient import OkxClient


class AccountAPI(OkxClient):

    # Get Positions
    def get_position_risk(self, instType: Any = None) -> Dict[str, Any]:
        params = {}
        if instType is not None:
            params['instType'] = instType
        return self._request_with_params(GET, POSITION_RISK, params)

    # Get Balance
    def get_account_balance(self, ccy: Any = None) -> Dict[str, Any]:
        params = {}
        if ccy is not None:
            params['ccy'] = ccy
        return self._request_with_params(GET, ACCOUNT_INFO, params)

    # Get Positions
    def get_positions(self, instType: Any = None, instId: Any = None, posId: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'instId': instId, 'posId': posId}
        return self._request_with_params(GET, POSITION_INFO, params)

    def position_builder(self, acctLv: Any = None, inclRealPosAndEq: Any = None, lever: Any = None, greeksType: Any = None, simPos: Any = None,
                         simAsset: Any = None, idxVol: Any = None) -> Dict[str, Any]:
        params = {}
        if acctLv is not None:
            params['acctLv'] = acctLv
        if inclRealPosAndEq is not None:
            params['inclRealPosAndEq'] = inclRealPosAndEq
        if lever is not None:
            params['lever'] = lever
        if greeksType is not None:
            params['greeksType'] = greeksType
        if simPos is not None:
            params['simPos'] = simPos
        if simAsset is not None:
            params['simAsset'] = simAsset
        if idxVol is not None:
            params['idxVol'] = idxVol
        return self._request_with_params(POST, POSITION_BUILDER, params)

    # Get Bills Details (recent 7 days)
    def get_account_bills(self, instType: Any = None, ccy: Any = None, mgnMode: Any = None, ctType: Any = None, type: Any = None, subType: Any = None, after: Any = None, before: Any = None,
                          limit: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'ccy': ccy, 'mgnMode': mgnMode, 'ctType': ctType, 'type': type,
                  'subType': subType, 'after': after, 'before': before, 'limit': limit, 'begin': begin, 'end': end}
        return self._request_with_params(GET, BILLS_DETAIL, params)

    # Get Bills Details (recent 3 months)
    def get_account_bills_archive(self, instType: Any = None, ccy: Any = None, mgnMode: Any = None, ctType: Any = None, type: Any = None, subType: Any = None, after: Any = None,
                                  before: Any = None,
                                  limit: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'ccy': ccy, 'mgnMode': mgnMode, 'ctType': ctType, 'type': type,
                  'subType': subType, 'after': after, 'before': before, 'limit': limit, 'begin': begin, 'end': end}
        return self._request_with_params(GET, BILLS_ARCHIVE, params)

    # Get Account Configuration
    def get_account_config(self) -> Dict[str, Any]:
        return self._request_without_params(GET, ACCOUNT_CONFIG)

    # Get Account Configuration
    def set_position_mode(self, posMode: Any) -> Dict[str, Any]:
        params = {'posMode': posMode}
        return self._request_with_params(POST, POSITION_MODE, params)

    # Get Account Configuration
    def set_leverage(self, lever: Any, mgnMode: Any, instId: Any = None, ccy: Any = None, posSide: Any = None) -> Dict[str, Any]:
        params = {'lever': lever, 'mgnMode': mgnMode, 'instId': instId, 'ccy': ccy, 'posSide': posSide}
        return self._request_with_params(POST, SET_LEVERAGE, params)

    # Get Maximum Tradable Size For Instrument
    def get_max_order_size(self, instId: Any, tdMode: Any, ccy: Any = None, px: Any = None, tradeQuoteCcy: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'tdMode': tdMode, 'ccy': ccy, 'px': px}
        if tradeQuoteCcy is not None:
            params['tradeQuoteCcy'] = tradeQuoteCcy
        return self._request_with_params(GET, MAX_TRADE_SIZE, params)

    # Get Maximum Available Tradable Amount
    def get_max_avail_size(self, instId: Any, tdMode: Any, ccy: Any = None, reduceOnly: Any = None, unSpotOffset: Any = None, quickMgnType: Any = None, tradeQuoteCcy: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'tdMode': tdMode, 'ccy': ccy, 'reduceOnly': reduceOnly,
                  'unSpotOffset': unSpotOffset, 'quickMgnType': quickMgnType}
        if tradeQuoteCcy is not None:
            params['tradeQuoteCcy'] = tradeQuoteCcy
        return self._request_with_params(GET, MAX_AVAIL_SIZE, params)

    # Increase / Decrease margin
    def adjustment_margin(self, instId: Any, posSide: Any, type: Any, amt: Any, loanTrans: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'posSide': posSide, 'type': type, 'amt': amt, 'loanTrans': loanTrans}
        return self._request_with_params(POST, ADJUSTMENT_MARGIN, params)

    # Get Leverage
    def get_leverage(self, mgnMode: Any, ccy: Any = None, instId: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'mgnMode': mgnMode, 'ccy': ccy}
        return self._request_with_params(GET, GET_LEVERAGE, params)

    # Get instruments
    def get_instruments(self, instType: Any = None, uly: Any = None, instFamily: Any = None, instId: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'instFamily': instFamily, 'instId': instId}
        return self._request_with_params(GET, GET_INSTRUMENTS, params)

    # Get the maximum loan of isolated MARGIN
    def get_max_loan(self, instId: Any, mgnMode: Any, mgnCcy: Any = None, tradeQuoteCcy: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'mgnMode': mgnMode, 'mgnCcy': mgnCcy}
        if tradeQuoteCcy is not None:
            params['tradeQuoteCcy'] = tradeQuoteCcy
        return self._request_with_params(GET, MAX_LOAN, params)

    # Get Fee Rates
    def get_fee_rates(self, instType: Any, instId: Any = None, uly: Any = None, category: Any = None, instFamily: Any = None, groupId: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'instId': instId, 'uly': uly, 'category': category, 'instFamily': instFamily}
        if groupId is not None:
            params['groupId'] = groupId
        return self._request_with_params(GET, FEE_RATES, params)

    # Get interest-accrued
    def get_interest_accrued(self, instId: Any = None, ccy: Any = None, mgnMode: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'ccy': ccy, 'mgnMode': mgnMode, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, INTEREST_ACCRUED, params)

    # Get interest-accrued
    def get_interest_rate(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, INTEREST_RATE, params)

    # Set Greeks (PA/BS)
    def set_greeks(self, greeksType: Any) -> Dict[str, Any]:
        params = {'greeksType': greeksType}
        return self._request_with_params(POST, SET_GREEKS, params)

    # Set Isolated Mode
    def set_isolated_mode(self, isoMode: Any, type: Any) -> Dict[str, Any]:
        params = {'isoMode': isoMode, 'type': type}
        return self._request_with_params(POST, ISOLATED_MODE, params)

    # Get Maximum Withdrawals
    def get_max_withdrawal(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, MAX_WITHDRAWAL, params)

    # Get borrow repay
    def borrow_repay(self, ccy: Any = None, side: Any = None, amt: Any = None, ordId: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'side': side, 'amt': amt, 'ordId': ordId}
        return self._request_with_params(POST, BORROW_REPAY, params)

    # Get borrow repay history
    def get_borrow_repay_history(self, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BORROW_REPAY_HISTORY, params)

    # Get Obtain borrowing rate and limit
    def get_interest_limits(self, type: Any = None, ccy: Any = None) -> Dict[str, Any]:
        params = {'type': type, 'ccy': ccy}
        return self._request_with_params(GET, INTEREST_LIMITS, params)

    # Get Simulated Margin
    def get_simulated_margin(self, instType: Any = None, inclRealPos: Any=True, spotOffsetType: Any = None, simPos: Any = None) -> Dict[str, Any]:
        if simPos is None:
            simPos = []
        params = {'instType': instType, 'inclRealPos': inclRealPos, 'spotOffsetType': spotOffsetType, 'simPos': simPos}
        return self._request_with_params(POST, SIMULATED_MARGIN, params)

    # Get  Greeks
    def get_greeks(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self._request_with_params(GET, GREEKS, params)

    # GET /api/v5/account/risk-state
    def get_account_position_risk(self) -> Dict[str, Any]:
        return self._request_without_params(GET, ACCOUNT_RISK)

    # GET /api/v5/account/positions-history
    def get_positions_history(self, instType: Any = None, instId: Any = None, mgnMode: Any = None, type: Any = None, posId: Any = None, after: Any = None, before: Any = None,
                              limit: Any = None) -> Dict[str, Any]:
        params = {
            'instType': instType,
            'instId': instId,
            'mgnMode': mgnMode,
            'type': type,
            'posId': posId,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, POSITIONS_HISTORY, params)

    # GET /api/v5/account/position-tiers
    def get_account_position_tiers(self, instType: Any = None, uly: Any = None, instFamily: Any = None) -> Dict[str, Any]:
        params = {
            'instType': instType,
            'uly': uly,
            'instFamily': instFamily
        }
        return self._request_with_params(GET, GET_PM_LIMIT, params)

    # - Get VIP interest accrued data
    def get_vip_interest_accrued_data(self, ccy: Any = None, ordId: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_VIP_INTEREST_ACCRUED_DATA, params)

    # - Get VIP interest deducted data
    def get_vip_interest_deducted_data(self, ccy: Any = None, ordId: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_VIP_INTEREST_DEDUCTED_DATA, params)

    # - Get VIP loan order list
    def get_vip_loan_order_list(self, ordId: Any = None, state: Any = None, ccy: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId, 'state': state, 'ccy': ccy, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_VIP_LOAN_ORDER_LIST, params)

    # - Get VIP loan order detail
    def get_vip_loan_order_detail(self, ccy: Any = None, ordId: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_VIP_LOAN_ORDER_DETAIL, params)

    # - Set risk offset type
    def set_risk_offset_type(self, type: Any = None) -> Dict[str, Any]:
        params = {'type': type}
        return self._request_with_params(POST, SET_RISK_OFFSET_TYPE, params)

    # - Set auto loan
    def set_auto_loan(self, autoLoan: Any = None) -> Dict[str, Any]:
        params = {
            'autoLoan': autoLoan
        }
        return self._request_with_params(POST, SET_AUTO_LOAN, params)

    # - Set account level
    def set_account_level(self, acctLv: Any) -> Dict[str, Any]:
        params = {
            'acctLv': acctLv
        }
        return self._request_with_params(POST, SET_ACCOUNT_LEVEL, params)

    # - Activate option
    def activate_option(self) -> Dict[str, Any]:
        return self._request_without_params(POST, ACTIVATE_OPTION)

    def get_fix_loan_borrowing_limit(self) -> Dict[str, Any]:
        return self._request_without_params(GET, BORROWING_LIMIT)

    def get_fix_loan_borrowing_quote(self, type: Any = None, ccy: Any = None, amt: Any = None, maxRate: Any = None, term: Any = None, ordId: Any = None) -> Dict[str, Any]:
        params = {}
        if type is not None:
            params['type'] = type
        if ccy is not None:
            params['ccy'] =ccy
        if amt is not None:
            params['amt'] = amt
        if maxRate is not None:
            params['maxRate'] = maxRate
        if term is not None:
            params['term'] = term
        if ordId is not None:
            params['ordId'] = ordId
        return self._request_with_params(GET, BORROWING_QUOTE, params)

    def place_fix_loan_borrowing_order(self, ccy: Any = None, amt: Any = None, maxRate: Any = None, term: Any = None, reborrow: Any=False, reborrowRate: Any = None) -> Dict[str, Any]:
        params = {}
        if ccy is not None:
            params['ccy'] =ccy
        if amt is not None:
            params['amt'] = amt
        if maxRate is not None:
            params['maxRate'] = maxRate
        if term is not None:
            params['term'] = term
        if reborrow is not None:
            params['reborrow'] = reborrow
        if reborrowRate is not None:
            params['reborrowRate'] = reborrowRate
        return self._request_with_params(POST, PLACE_BORROWING_ORDER, params)

    def amend_fix_loan_borrowing_order(self, ordId: Any = None, reborrow: Any = None, renewMaxRate: Any = None) -> Dict[str, Any]:
        params = {}
        if ordId is not None:
            params['ordId'] = ordId
        if reborrow is not None:
            params['reborrow'] = reborrow
        if renewMaxRate is not None:
            params['renewMaxRate'] = renewMaxRate
        return self._request_with_params(POST, AMEND_BORROWING_ORDER, params)

    def fix_loan_manual_reborrow(self, ordId: Any = None, maxRate: Any = None) -> Dict[str, Any]:
        params = {}
        if ordId is not None:
            params['ordId'] = ordId
        if maxRate is not None:
            params['maxRate'] = maxRate
        return self._request_with_params(POST, MANUAL_REBORROW, params)

    def repay_fix_loan_borrowing_order(self, ordId: Any = None) -> Dict[str, Any]:
        params = {}
        if ordId is not None:
            params['ordId'] = ordId
        return self._request_with_params(POST, REPAY_BORROWING_ORDER, params)
    def get_fix_loan_borrowing_orders_list(self, ordId: Any = None, ccy: Any = None, state: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {}
        if ordId is not None:
            params['ordId'] = ordId
        if ccy is not None:
            params['ccy'] =ccy
        if state is not None:
            params['state'] = state
        if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, BORROWING_ORDERS_LIST, params)

    def spot_manual_borrow_repay(self, ccy: Any = None, side: Any = None, amt: Any = None) -> Dict[str, Any]:
        params = {}
        if ccy is not None:
            params['ccy'] = ccy
        if side is not None:
            params['side'] = side
        if amt is not None:
            params['amt'] = amt
        return self._request_with_params(POST, MANUAL_REBORROW_REPAY, params)

    def set_auto_repay(self, autoRepay: Any=False) -> Dict[str, Any]:
        params = {}
        if autoRepay is not None:
            params['autoRepay'] = autoRepay
        return self._request_with_params(POST, SET_AUTO_REPAY, params)

    def spot_borrow_repay_history(self, ccy: Any = None, type: Any = None, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'type': type, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_BORROW_REPAY_HISTORY, params)

    def set_auto_earn(self, ccy: Any, action: Any, earnType: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'action': action}
        if earnType is not None:
            params['earnType'] = earnType
        return self._request_with_params(POST, SET_AUTO_EARN, params)

    # Set trading config (BROK-1724). type is required (e.g. 'stgyType');
    # stgyType (0=general, 1=delta neutral) applies only when type == 'stgyType'.
    def set_trading_config(self, type: Any = None, stgyType: Any = None) -> Dict[str, Any]:
        params = {'type': type}
        if stgyType is not None:
            params['stgyType'] = stgyType
        return self._request_with_params(POST, SET_TRADING_CONFIG, params)

    # Pre-check whether the delta-neutral switch is allowed (BROK-1724)
    def precheck_set_delta_neutral(self, stgyType: Any = None) -> Dict[str, Any]:
        params = {'stgyType': stgyType}
        return self._request_with_params(GET, PRECHECK_SET_DELTA_NEUTRAL, params)

    # Get the list of supported bill subtypes (BROK-1728)
    def get_bill_type(self, type: Any = None) -> Dict[str, Any]:
        params = {}
        if type is not None:
            params['type'] = type
        return self._request_with_params(GET, BILL_TYPE, params)

    # Apply for an asynchronous bill history archive by year + quarter (BROK-1728)
    def apply_bills(self, year: Any = None, quarter: Any = None, type: Any = None) -> Dict[str, Any]:
        params = {'year': year, 'quarter': quarter}
        if type is not None:
            params['type'] = type
        return self._request_with_params(POST, BILLS_APPLY, params)

    # Get GLP daily performance history for a program
    def get_glp_historical_performance(self, program: Any, begin: Any = None, end: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'program': program}
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, GLP_HISTORICAL_PERFORMANCE, params)

    # Get current-day + MTD GLP snapshot for all enrolled programs
    def get_glp_today_performance(self) -> Dict[str, Any]:
        return self._request_without_params(GET, GLP_TODAY_PERFORMANCE)

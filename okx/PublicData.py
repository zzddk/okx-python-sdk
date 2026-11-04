from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class PublicAPI(OkxClient):

    # Get Instruments
    def get_instruments(self, instType: Any, uly: Any = None, instId: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self.request(GET, INSTRUMENT_INFO, params)

    # Get Delivery/Exercise History
    def get_delivery_exercise_history(self, instType: Any, uly: Any = None, after: Any = None, before: Any = None, limit: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'after': after, 'before': before, 'limit': limit,'instFamily':instFamily}
        return self.request(GET, DELIVERY_EXERCISE, params)

    # Get Open Interest
    def get_open_interest(self, instType: Any, uly: Any = None, instId: Any = None ,instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self.request(GET, OPEN_INTEREST, params)

    # Get Funding Rate
    def get_funding_rate(self, instId: Any) -> Dict[str, Any]:
        params = {'instId': instId}
        return self.request(GET, FUNDING_RATE, params)

    # Get Funding Rate History
    def funding_rate_history(self, instId: Any, after: Any = None, before: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'after': after, 'before': before, 'limit': limit}
        return self.request(GET, FUNDING_RATE_HISTORY, params)

    # Get Limit Price
    def get_price_limit(self, instId: Any) -> Dict[str, Any]:
        params = {'instId': instId}
        return self.request(GET, PRICE_LIMIT, params)

    # Get Option Market Data
    def get_opt_summary(self, uly: Any = None, expTime: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {'uly': uly, 'expTime': expTime,'instFamily':instFamily}
        return self.request(GET, OPT_SUMMARY, params)

    # Get Estimated Delivery/Excercise Price
    def get_estimated_price(self, instId: Any) -> Dict[str, Any]:
        params = {'instId': instId}
        return self.request(GET, ESTIMATED_PRICE, params)

    # Get Discount Rate And Interest-Free Quota
    def discount_interest_free_quota(self, ccy: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy}
        return self.request(GET, DISCOUNT_INTEREST_INFO, params)

    # Get System Time
    def get_system_time(self) -> Dict[str, Any]:
        return self.request(GET, SYSTEM_TIME)

    # Get Mark Price
    def get_mark_price(self, instType: Any, uly: Any = None, instId: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self.request(GET, MARK_PRICE, params)

    # Get Tier
    def get_position_tiers(self, instType: Any, tdMode: Any, uly: Any = None, instId: Any = None, ccy: Any = None, tier: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'tdMode': tdMode, 'uly': uly, 'instId': instId, 'ccy': ccy, 'tier': tier,'instFamily':instFamily}
        return self.request(GET, TIER, params)

    #GET /api/v5/public/interest-rate-loan-quota
    def get_interest_rate_loan_quota(self) -> Dict[str, Any]:
        return self.request(GET,INTEREST_LOAN)

    #GET /api/v5/public/vip-interest-rate-loan-quota
    def get_vip_interest_rate_loan_quota(self) -> Dict[str, Any]:
        return self.request(GET, VIP_INTEREST_RATE_LOAN_QUOTA)

    #GET /api/v5/public/underlying
    def get_underlying(self,instType: Any = None) -> Dict[str, Any]:
        params = {
            'instType':instType
        }
        return self.request(GET, UNDERLYING, params)

    #GET /api/v5/public/insurance-fund
    def get_insurance_fund(self,instType: Any = None,type: Any = None,uly: Any = None,ccy: Any = None,before: Any = None,after: Any = None,limit: Any = None,instFamily: Any = None) -> Dict[str, Any]:
        params = {
            'instType':instType,
            'type':type,
            'uly':uly,
            'ccy':ccy,
            'before':before,
            'after':after,
            'limit':limit,
            'instFamily':instFamily
        }
        return self.request(GET, INSURANCE_FUND, params)

    #GET /api/v5/public/convert-contract-coin
    def get_convert_contract_coin(self,type: Any = None,instId: Any = None,sz: Any = None,px: Any = None,unit: Any = None) -> Dict[str, Any]:
        params = {
            'type':type,
            'instId':instId,
            'sz':sz,
            'px':px,
            'unit':unit
        }
        return self.request(GET, CONVERT_CONTRACT_COIN, params)

    # Get option tickbands
    def get_option_tickbands(self, instType: Any = None, instFamily: Any = None) -> Dict[str, Any]:
        params = {
            'instType': instType,
            'instFamily': instFamily
        }
        return self.request(GET, GET_OPTION_TICKBANDS, params)

    # Get option trades
    def get_option_trades(self, instId: Any = None, instFamily: Any = None, optType: Any = None) -> Dict[str, Any]:
        params = {
            'instId': instId,
            'instFamily': instFamily,
            'optType': optType
        }
        return self.request(GET, GET_OPTION_TRADES, params)

    # Get historical market data
    def get_market_data_history(self, module: Any, instType: Any, dateAggrType: Any, begin: Any, end: Any, instIdList: Any = None, instFamilyList: Any = None) -> Dict[str, Any]:
        params = {
            'module': module,
            'instType': instType,
            'dateAggrType': dateAggrType,
            'begin': begin,
            'end': end
        }
        if instIdList is not None:
            params['instIdList'] = instIdList
        if instFamilyList is not None:
            params['instFamilyList'] = instFamilyList
        return self.request(GET, MARKET_DATA_HISTORY, params)

    # Get announcements (BROK-1730)
    def get_announcements(self, annType: Any = None, page: Any = None) -> Dict[str, Any]:
        params = {'annType': annType, 'page': page}
        return self.request(GET, ANNOUNCEMENTS, params)

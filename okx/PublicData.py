from .okxclient import OkxClient
from .consts import *


class PublicAPI(OkxClient):

    # Get Instruments
    def get_instruments(self, instType, uly = None, instId = None,instFamily = None):
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self._request_with_params(GET, INSTRUMENT_INFO, params)

    # Get Delivery/Exercise History
    def get_delivery_exercise_history(self, instType, uly = None, after = None, before = None, limit = None,instFamily = None):
        params = {'instType': instType, 'uly': uly, 'after': after, 'before': before, 'limit': limit,'instFamily':instFamily}
        return self._request_with_params(GET, DELIVERY_EXERCISE, params)

    # Get Open Interest
    def get_open_interest(self, instType, uly = None, instId = None ,instFamily = None):
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self._request_with_params(GET, OPEN_INTEREST, params)

    # Get Funding Rate
    def get_funding_rate(self, instId):
        params = {'instId': instId}
        return self._request_with_params(GET, FUNDING_RATE, params)

    # Get Funding Rate History
    def funding_rate_history(self, instId, after = None, before = None, limit = None):
        params = {'instId': instId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, FUNDING_RATE_HISTORY, params)

    # Get Limit Price
    def get_price_limit(self, instId):
        params = {'instId': instId}
        return self._request_with_params(GET, PRICE_LIMIT, params)

    # Get Option Market Data
    def get_opt_summary(self, uly = None, expTime = None,instFamily = None):
        params = {'uly': uly, 'expTime': expTime,'instFamily':instFamily}
        return self._request_with_params(GET, OPT_SUMMARY, params)

    # Get Estimated Delivery/Excercise Price
    def get_estimated_price(self, instId):
        params = {'instId': instId}
        return self._request_with_params(GET, ESTIMATED_PRICE, params)

    # Get Discount Rate And Interest-Free Quota
    def discount_interest_free_quota(self, ccy = None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, DISCOUNT_INTEREST_INFO, params)

    # Get System Time
    def get_system_time(self):
        return self._request_without_params(GET, SYSTEM_TIME)

    # Get Mark Price
    def get_mark_price(self, instType, uly = None, instId = None,instFamily = None):
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        return self._request_with_params(GET, MARK_PRICE, params)

    # Get Tier
    def get_position_tiers(self, instType, tdMode, uly = None, instId = None, ccy = None, tier = None,instFamily = None):
        params = {'instType': instType, 'tdMode': tdMode, 'uly': uly, 'instId': instId, 'ccy': ccy, 'tier': tier,'instFamily':instFamily}
        return self._request_with_params(GET, TIER, params)

    #GET /api/v5/public/interest-rate-loan-quota
    def get_interest_rate_loan_quota(self):
        return self._request_without_params(GET,INTEREST_LOAN)

    #GET /api/v5/public/vip-interest-rate-loan-quota
    def get_vip_interest_rate_loan_quota(self):
        return self._request_without_params(GET, VIP_INTEREST_RATE_LOAN_QUOTA)

    #GET /api/v5/public/underlying
    def get_underlying(self,instType = None):
        params = {
            'instType':instType
        }
        return self._request_with_params(GET, UNDERLYING, params)

    #GET /api/v5/public/insurance-fund
    def get_insurance_fund(self,instType = None,type = None,uly = None,ccy = None,before = None,after = None,limit = None,instFamily = None):
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
        return self._request_with_params(GET, INSURANCE_FUND, params)

    #GET /api/v5/public/convert-contract-coin
    def get_convert_contract_coin(self,type = None,instId = None,sz = None,px = None,unit = None):
        params = {
            'type':type,
            'instId':instId,
            'sz':sz,
            'px':px,
            'unit':unit
        }
        return self._request_with_params(GET, CONVERT_CONTRACT_COIN, params)

    # Get option tickbands
    def get_option_tickbands(self, instType = None, instFamily = None):
        params = {
            'instType': instType,
            'instFamily': instFamily
        }
        return self._request_with_params(GET, GET_OPTION_TICKBANDS, params)

    # Get option trades
    def get_option_trades(self, instId = None, instFamily = None, optType = None):
        params = {
            'instId': instId,
            'instFamily': instFamily,
            'optType': optType
        }
        return self._request_with_params(GET, GET_OPTION_TRADES, params)

    # Get historical market data
    def get_market_data_history(self, module, instType, dateAggrType, begin, end, instIdList = None, instFamilyList = None):
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
        return self._request_with_params(GET, MARKET_DATA_HISTORY, params)

    # Get announcements (BROK-1730)
    def get_announcements(self, annType = None, page = None):
        params = {'annType': annType, 'page': page}
        return self._request_with_params(GET, ANNOUNCEMENTS, params)

from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class TradingDataAPI(OkxClient):

    def get_support_coin(self) -> Dict[str, Any]:
        return self.request(GET, SUPPORT_COIN)

    def get_taker_volume(self, ccy: Any, instType: Any, begin: Any = None, end: Any = None, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'instType': instType, 'begin': begin, 'end': end, 'period': period}
        return self.request(GET, TAKER_VOLUME, params)

    def get_margin_lending_ratio(self, ccy: Any, begin: Any = None, end: Any = None, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        return self.request(GET, MARGIN_LENDING_RATIO, params)

    def get_long_short_ratio(self, ccy: Any, begin: Any = None, end: Any = None, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        return self.request(GET, LONG_SHORT_RATIO, params)

    def get_contracts_interest_volume(self, ccy: Any, begin: Any = None, end: Any = None, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        return self.request(GET, CONTRACTS_INTEREST_VOLUME, params)

    def get_options_interest_volume(self, ccy: Any, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'period': period}
        return self.request(GET, OPTIONS_INTEREST_VOLUME, params)

    def get_put_call_ratio(self, ccy: Any, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'period': period}
        return self.request(GET, PUT_CALL_RATIO, params)

    def get_interest_volume_expiry(self, ccy: Any, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'period': period}
        return self.request(GET, OPEN_INTEREST_VOLUME_EXPIRY, params)

    def get_interest_volume_strike(self, ccy: Any, expTime: Any, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'expTime': expTime, 'period': period}
        return self.request(GET, INTEREST_VOLUME_STRIKE, params)

    def get_taker_block_volume(self, ccy: Any, period: Any = None) -> Dict[str, Any]:
        params = {'ccy': ccy, 'period': period}
        return self.request(GET, TAKER_FLOW, params)

    def get_open_interest_history(self, instId: Any, period: Any = None, begin: Any = None, end: Any = None, limit: Any = None) -> Dict[str, Any]:
        """
        Get contract open interest history
        Retrieve the contract open interest statistics of futures and perp.
        Rate limit: 10 requests per 2 seconds
        Rate limit rule: IP + Instrument ID
        
        :param instId: Instrument ID, e.g. BTC-USDT-SWAP. Only applicable to FUTURES, SWAP
        :param period: Bar size, the default is 5m, e.g. [5m/15m/30m/1H/2H/4H]
        :param begin: Return records newer than the requested ts
        :param end: Pagination of data to return records earlier than the requested ts
        :param limit: Number of results per request. The maximum is 100. The default is 100
        :return: API response
        """
        params = {'instId': instId, 'period': period, 'begin': begin, 'end': end, 'limit': limit}
        return self.request(GET, CONTRACTS_OPEN_INTEREST_HISTORY, params)








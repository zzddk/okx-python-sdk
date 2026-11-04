from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class ConvertAPI(OkxClient):
    def get_currencies(self) -> Dict[str, Any]:
        params = {}
        return self.request(GET, GET_CURRENCIES, params)

    def get_currency_pair(self, fromCcy: Any = None, toCcy: Any = None, convertMode: Any = None) -> Dict[str, Any]:
        params = {"fromCcy": fromCcy, 'toCcy': toCcy}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self.request(GET, GET_CURRENCY_PAIR, params)

    def estimate_quote(self, baseCcy: Any = None, quoteCcy: Any = None, side: Any = None, rfqSz: Any = None, rfqSzCcy: Any = None, clQReqId: Any = None,tag: Any = None, convertMode: Any = None) -> Dict[str, Any]:
        params = {'baseCcy': baseCcy, 'quoteCcy': quoteCcy, 'side':side, 'rfqSz':rfqSz, 'rfqSzCcy':rfqSzCcy, 'clQReqId':clQReqId,'tag':tag}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self.request(POST, ESTIMATE_QUOTE, params)

    def convert_trade(self, quoteId: Any = None, baseCcy: Any = None, quoteCcy: Any = None, side: Any = None, sz: Any = None, szCcy: Any = None, clTReqId: Any = None,tag: Any = None, convertMode: Any = None) -> Dict[str, Any]:
        params = {'quoteId': quoteId, 'baseCcy': baseCcy, 'quoteCcy':quoteCcy, 'side':side, 'sz':sz, 'szCcy':szCcy, 'clTReqId':clTReqId,'tag':tag}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self.request(POST, CONVERT_TRADE, params)

    def get_convert_history(self, after: Any = None, before: Any = None, limit: Any = None,tag: Any = None) -> Dict[str, Any]:
        params = {'after': after, 'before': before, 'limit':limit,'tag':tag}
        return self.request(GET, CONVERT_HISTORY, params)

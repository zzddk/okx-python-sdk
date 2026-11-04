from .okxclient import OkxClient
from .consts import *


class ConvertAPI(OkxClient):
    def get_currencies(self):
        params = {}
        return self._request_with_params(GET, GET_CURRENCIES, params)

    def get_currency_pair(self, fromCcy = None, toCcy = None, convertMode = None):
        params = {"fromCcy": fromCcy, 'toCcy': toCcy}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self._request_with_params(GET, GET_CURRENCY_PAIR, params)

    def estimate_quote(self, baseCcy = None, quoteCcy = None, side = None, rfqSz = None, rfqSzCcy = None, clQReqId = None,tag = None, convertMode = None):
        params = {'baseCcy': baseCcy, 'quoteCcy': quoteCcy, 'side':side, 'rfqSz':rfqSz, 'rfqSzCcy':rfqSzCcy, 'clQReqId':clQReqId,'tag':tag}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self._request_with_params(POST, ESTIMATE_QUOTE, params)

    def convert_trade(self, quoteId = None, baseCcy = None, quoteCcy = None, side = None, sz = None, szCcy = None, clTReqId = None,tag = None, convertMode = None):
        params = {'quoteId': quoteId, 'baseCcy': baseCcy, 'quoteCcy':quoteCcy, 'side':side, 'sz':sz, 'szCcy':szCcy, 'clTReqId':clTReqId,'tag':tag}
        if convertMode is not None:
            params['convertMode'] = convertMode
        return self._request_with_params(POST, CONVERT_TRADE, params)

    def get_convert_history(self, after = None, before = None, limit = None,tag = None):
        params = {'after': after, 'before': before, 'limit':limit,'tag':tag}
        return self._request_with_params(GET, CONVERT_HISTORY, params)

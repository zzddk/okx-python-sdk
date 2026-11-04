from .okxclient import OkxClient
from .consts import *


class SpreadTradingAPI(OkxClient):

    # Place Order
    def place_order(self, sprdId = None, clOrdId = None, tag = None, side = None, ordType = None, sz = None, px = None):
        params = {'sprdId': sprdId, 'clOrdId': clOrdId, 'tag': tag, 'side': side, 'ordType': ordType, 'sz': sz,
                  'px': px}
        return self._request_with_params(POST, SPREAD_PLACE_ORDER, params)

    # Cancel Order
    def cancel_order(self,ordId = None, clOrdId = None):
        params = {'ordId': ordId, 'clOrdId': clOrdId}
        return self._request_with_params(POST, SPREAD_CANCEL_ORDER, params)

    # Cancel All orders
    def cancel_all_orders(self, sprdId = None):
        params = {'sprdId': sprdId}
        return self._request_with_params(POST, SPREAD_CANCEL_ALL_ORDERS, params)

    # Get order details
    def get_order_details(self, ordId = None, clOrdId = None):
        params = {'ordId': ordId, 'clOrdId': clOrdId}
        return self._request_with_params(GET, SPREAD_GET_ORDER_DETAILS, params)

    # Get active orders
    def get_active_orders(self, sprdId = None, ordType = None, state = None, beginId = None, endId = None, limit = None):
        params = {'sprdId': sprdId, 'ordType': ordType, 'state': state, 'beginId': beginId, 'endId': endId, 'limit': limit}
        return self._request_with_params(GET, SPREAD_GET_ACTIVE_ORDERS, params)

    # Get orders (last 7 days)
    def get_orders(self, sprdId = None, ordType = None, state = None, beginId = None, endId = None, begin = None, end = None, limit = None):
        params = {'sprdId': sprdId, 'ordType': ordType, 'state': state, 'beginId': beginId, 'endId': endId,
                  'begin': begin, 'end': end, 'limit': limit}
        return self._request_with_params(GET, SPREAD_GET_ORDERS, params)

    # Get trades (last 7 days)
    def get_trades(self, sprdId = None, tradeId = None, ordId = None, beginId = None, endId = None, begin = None, end = None, limit = None):
        params = {'sprdId': sprdId, 'tradeId': tradeId, 'ordId': ordId, 'beginId': beginId, 'endId': endId,
                  'begin': begin, 'end': end, 'limit': limit}
        return self._request_with_params(GET, SPREAD_GET_TRADES, params)

    # Get Spreads (Public)
    def get_spreads(self, baseCcy = None,instId = None, sprdId = None, state = None):
        params = {'baseCcy': baseCcy, 'instId': instId, 'sprdId': sprdId, 'state': state}
        return self._request_with_params(GET, SPREAD_GET_SPREADS, params)

    # Get order book (Public)
    def get_order_book(self, sprdId = None, sz = None):
        params = {'sprdId': sprdId, 'sz': sz}
        return self._request_with_params(GET, SPREAD_GET_ORDER_BOOK, params)

    # Get ticker (Public)
    def get_ticker(self, sprdId = None):
        params = {'sprdId': sprdId}
        return self._request_with_params(GET, SPREAD_GET_TICKER, params)

    # Get public trades (Public)
    def get_public_trades(self, sprdId = None):
        params = {'sprdId': sprdId}
        return self._request_with_params(GET, SPREAD_GET_PUBLIC_TRADES, params)


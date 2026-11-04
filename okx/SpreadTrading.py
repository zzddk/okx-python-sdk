from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class SpreadTradingAPI(OkxClient):

    # Place Order
    def place_order(self, sprdId: Any = None, clOrdId: Any = None, tag: Any = None, side: Any = None, ordType: Any = None, sz: Any = None, px: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId, 'clOrdId': clOrdId, 'tag': tag, 'side': side, 'ordType': ordType, 'sz': sz,
                  'px': px}
        return self.request(POST, SPREAD_PLACE_ORDER, params)

    # Cancel Order
    def cancel_order(self,ordId: Any = None, clOrdId: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId, 'clOrdId': clOrdId}
        return self.request(POST, SPREAD_CANCEL_ORDER, params)

    # Cancel All orders
    def cancel_all_orders(self, sprdId: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId}
        return self.request(POST, SPREAD_CANCEL_ALL_ORDERS, params)

    # Get order details
    def get_order_details(self, ordId: Any = None, clOrdId: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId, 'clOrdId': clOrdId}
        return self.request(GET, SPREAD_GET_ORDER_DETAILS, params)

    # Get active orders
    def get_active_orders(self, sprdId: Any = None, ordType: Any = None, state: Any = None, beginId: Any = None, endId: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId, 'ordType': ordType, 'state': state, 'beginId': beginId, 'endId': endId, 'limit': limit}
        return self.request(GET, SPREAD_GET_ACTIVE_ORDERS, params)

    # Get orders (last 7 days)
    def get_orders(self, sprdId: Any = None, ordType: Any = None, state: Any = None, beginId: Any = None, endId: Any = None, begin: Any = None, end: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId, 'ordType': ordType, 'state': state, 'beginId': beginId, 'endId': endId,
                  'begin': begin, 'end': end, 'limit': limit}
        return self.request(GET, SPREAD_GET_ORDERS, params)

    # Get trades (last 7 days)
    def get_trades(self, sprdId: Any = None, tradeId: Any = None, ordId: Any = None, beginId: Any = None, endId: Any = None, begin: Any = None, end: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId, 'tradeId': tradeId, 'ordId': ordId, 'beginId': beginId, 'endId': endId,
                  'begin': begin, 'end': end, 'limit': limit}
        return self.request(GET, SPREAD_GET_TRADES, params)

    # Get Spreads (Public)
    def get_spreads(self, baseCcy: Any = None,instId: Any = None, sprdId: Any = None, state: Any = None) -> Dict[str, Any]:
        params = {'baseCcy': baseCcy, 'instId': instId, 'sprdId': sprdId, 'state': state}
        return self.request(GET, SPREAD_GET_SPREADS, params)

    # Get order book (Public)
    def get_order_book(self, sprdId: Any = None, sz: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId, 'sz': sz}
        return self.request(GET, SPREAD_GET_ORDER_BOOK, params)

    # Get ticker (Public)
    def get_ticker(self, sprdId: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId}
        return self.request(GET, SPREAD_GET_TICKER, params)

    # Get public trades (Public)
    def get_public_trades(self, sprdId: Any = None) -> Dict[str, Any]:
        params = {'sprdId': sprdId}
        return self.request(GET, SPREAD_GET_PUBLIC_TRADES, params)


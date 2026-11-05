from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class MarketAPI(OkxClient):

    # Get Tickers
    def get_tickers(self, instType: Any, uly: Any = None, instFamily: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'uly': uly, 'instFamily': instFamily}
        return self.request(GET, TICKERS_INFO, params)

    # Get Ticker
    def get_ticker(self, instId: Any) -> Dict[str, Any]:
        params = {'instId': instId}
        return self.request(GET, TICKER_INFO, params)

    # Get Index Tickers
    def get_index_tickers(self, quoteCcy: Any = None, instId: Any = None) -> Dict[str, Any]:
        params = {'quoteCcy': quoteCcy, 'instId': instId}
        return self.request(GET, INDEX_TICKERS, params)

    # Get Order Book
    def get_orderbook(self, instId: Any, sz: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'sz': sz}
        return self.request(GET, ORDER_BOOKS, params)

    # Get RPI Order Book
    def get_rpi_orderbook(self, instId: Any, sz: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'sz': sz}
        return self.request(GET, MARKET_BOOKS_RPI, params)

    # Get Candlesticks
    def get_candlesticks(self, instId: Any, after: Any = None, before: Any = None, bar: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request(GET, MARKET_CANDLES, params)

    # GGet Candlesticks History（top currencies only）
    def get_history_candlesticks(self, instId: Any, after: Any = None, before: Any = None, bar: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request(GET, HISTORY_CANDLES, params)

    # Get Index Candlesticks
    def get_index_candlesticks(self, instId: Any, after: Any = None, before: Any = None, bar: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request(GET, INDEX_CANDLES, params)

    # Get Mark Price Candlesticks
    def get_mark_price_candlesticks(self, instId: Any, after: Any = None, before: Any = None, bar: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request(GET, MARKPRICE_CANDLES, params)

    # Get Index Candlesticks
    def get_trades(self, instId: Any, limit: Any = None) -> Dict[str, Any]:
        params = {'instId': instId, 'limit': limit}
        return self.request(GET, MARKET_TRADES, params)

    # Get Volume
    def get_volume(self) -> Dict[str, Any]:
        return self.request(GET, VOLUME)

    # Get Tier
    def get_tier(self, instType: Any = None, tdMode: Any = None, uly: Any = None, instId: Any = None, ccy: Any = None, tier: Any = None) -> Dict[str, Any]:
        params = {'instType': instType, 'tdMode': tdMode, 'uly': uly, 'instId': instId, 'ccy': ccy, 'tier': tier}
        return self.request(GET, TIER, params)

    #GET /api/v5/market/index-components
    def get_index_components(self,index: Any = None) -> Dict[str, Any]:
        param = {
            'index':index
        }
        return self.request(GET,INDEX_COMPONENTS,param)


    #GET /api/v5/market/exchange-rate
    def get_exchange_rate(self) -> Dict[str, Any]:
        return self.request(GET, EXCHANGE_RATE)

    #GET /api/v5/market/history-trades
    def get_history_trades(self,instId: Any = None,type: Any = None,after: Any = None,before: Any = None,limit: Any = None) -> Dict[str, Any]:
        params = {
            'instId':instId,
            'type':type,
            'after':after,
            'before':before,
            'limit':limit
        }
        return self.request(GET,HISTORY_TRADES,params)

    #GET /api/v5/market/block-ticker
    def get_block_ticker(self,instId: Any = None) -> Dict[str, Any]:
        params = {
            'instId':instId
        }
        return self.request(GET,BLOCK_TICKER,params)

    #GET /api/v5/market/block-tickers
    def get_block_tickers(self,instType: Any = None,uly: Any = None, instFamily: Any = None) -> Dict[str, Any]:
        params = {
            'instType':instType,
            'uly':uly,
            'instFamily':instFamily
        }
        return self.request(GET, BLOCK_TICKERS, params)

    #GET /api/v5/market/block-trades
    def get_block_trades(self,instId: Any = None) -> Dict[str, Any]:
        params = {
            'instId':instId
        }
        return self.request(GET, BLOCK_TRADES, params)

    #- Get order lite book
    def get_order_lite_book(self,instId: Any = None) -> Dict[str, Any]:
        params = {
            'instId':instId
        }
        return self.request(GET, GET_ORDER_LITE_BOOK, params)

    #- Get option trades
    def get_option_trades(self,instFamily: Any = None) -> Dict[str, Any]:
        params = {
            'instFamily':instFamily
        }
        return self.request(GET, MARKET_OPTION_TRADES, params)







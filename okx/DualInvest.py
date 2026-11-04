from typing import Any, Dict

from .okxclient import OkxClient
from .consts import (
    GET,
    POST,
    DUAL_INVEST_CURRENCY_PAIRS,
    DUAL_INVEST_PRODUCT_INFO,
    DUAL_INVEST_REQUEST_QUOTE,
    DUAL_INVEST_TRADE,
    DUAL_INVEST_REQUEST_REDEEM_QUOTE,
    DUAL_INVEST_REDEEM,
    DUAL_INVEST_ORDER_STATE,
    DUAL_INVEST_ORDER_HISTORY,
)


class DualInvestAPI(OkxClient):
    # GET /api/v5/finance/sfp/dcd/currency-pair
    def get_currency_pairs(self) -> Dict[str, Any]:
        return self.request(GET, DUAL_INVEST_CURRENCY_PAIRS)

    # GET /api/v5/finance/sfp/dcd/products
    def get_product_info(self, baseCcy: Any = None, quoteCcy: Any = None, optType: Any = None) -> Dict[str, Any]:
        params = {'baseCcy': baseCcy, 'quoteCcy': quoteCcy, 'optType': optType}
        return self.request(GET, DUAL_INVEST_PRODUCT_INFO, params)

    # POST /api/v5/finance/sfp/dcd/quote
    def request_quote(self, productId: Any = None, notionalSz: Any = None, notionalCcy: Any = None) -> Dict[str, Any]:
        params = {'productId': productId, 'notionalSz': notionalSz, 'notionalCcy': notionalCcy}
        return self.request(POST, DUAL_INVEST_REQUEST_QUOTE, params)

    # POST /api/v5/finance/sfp/dcd/trade
    def trade(self, quoteId: Any = None) -> Dict[str, Any]:
        params = {'quoteId': quoteId}
        return self.request(POST, DUAL_INVEST_TRADE, params)

    # POST /api/v5/finance/sfp/dcd/redeem-quote
    def request_redeem_quote(self, ordId: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId}
        return self.request(POST, DUAL_INVEST_REQUEST_REDEEM_QUOTE, params)

    # POST /api/v5/finance/sfp/dcd/redeem
    def redeem(self, ordId: Any = None, quoteId: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId, 'quoteId': quoteId}
        return self.request(POST, DUAL_INVEST_REDEEM, params)

    # GET /api/v5/finance/sfp/dcd/order-status
    def get_order_state(self, ordId: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId}
        return self.request(GET, DUAL_INVEST_ORDER_STATE, params)

    # GET /api/v5/finance/sfp/dcd/order-history
    def get_order_history(self, ordId: Any = None, productId: Any = None, uly: Any = None, state: Any = None,
                          beginId: Any = None, endId: Any = None, begin: Any = None, end: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'ordId': ordId, 'productId': productId, 'uly': uly, 'state': state,
                  'beginId': beginId, 'endId': endId, 'begin': begin, 'end': end, 'limit': limit}
        return self.request(GET, DUAL_INVEST_ORDER_HISTORY, params)

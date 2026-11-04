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
    def get_currency_pairs(self):
        return self._request_without_params(GET, DUAL_INVEST_CURRENCY_PAIRS)

    # GET /api/v5/finance/sfp/dcd/products
    def get_product_info(self, baseCcy = None, quoteCcy = None, optType = None):
        params = {'baseCcy': baseCcy, 'quoteCcy': quoteCcy, 'optType': optType}
        return self._request_with_params(GET, DUAL_INVEST_PRODUCT_INFO, params)

    # POST /api/v5/finance/sfp/dcd/quote
    def request_quote(self, productId = None, notionalSz = None, notionalCcy = None):
        params = {'productId': productId, 'notionalSz': notionalSz, 'notionalCcy': notionalCcy}
        return self._request_with_params(POST, DUAL_INVEST_REQUEST_QUOTE, params)

    # POST /api/v5/finance/sfp/dcd/trade
    def trade(self, quoteId = None):
        params = {'quoteId': quoteId}
        return self._request_with_params(POST, DUAL_INVEST_TRADE, params)

    # POST /api/v5/finance/sfp/dcd/redeem-quote
    def request_redeem_quote(self, ordId = None):
        params = {'ordId': ordId}
        return self._request_with_params(POST, DUAL_INVEST_REQUEST_REDEEM_QUOTE, params)

    # POST /api/v5/finance/sfp/dcd/redeem
    def redeem(self, ordId = None, quoteId = None):
        params = {'ordId': ordId, 'quoteId': quoteId}
        return self._request_with_params(POST, DUAL_INVEST_REDEEM, params)

    # GET /api/v5/finance/sfp/dcd/order-status
    def get_order_state(self, ordId = None):
        params = {'ordId': ordId}
        return self._request_with_params(GET, DUAL_INVEST_ORDER_STATE, params)

    # GET /api/v5/finance/sfp/dcd/order-history
    def get_order_history(self, ordId = None, productId = None, uly = None, state = None,
                          beginId = None, endId = None, begin = None, end = None, limit = None):
        params = {'ordId': ordId, 'productId': productId, 'uly': uly, 'state': state,
                  'beginId': beginId, 'endId': endId, 'begin': begin, 'end': end, 'limit': limit}
        return self._request_with_params(GET, DUAL_INVEST_ORDER_HISTORY, params)

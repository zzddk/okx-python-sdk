from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class BlockTradingAPI(OkxClient):
    def counterparties(self) -> Dict[str, Any]:
        params = {}
        return self._request_with_params(GET, COUNTERPARTIES, params)

    def create_rfq(self, counterparties: Any = None, anonymous: Any='false', clRfqId: Any = None, tag: Any = None, allowPartialExecution: Any='false',
                   legs: Any = None) -> Dict[str, Any]:
        if counterparties is None:
            counterparties = []
        if legs is None:
            legs = []
        params = {'counterparties': counterparties, 'anonymous': anonymous, 'clRfqId': clRfqId, 'tag': tag,
                  'allowPartialExecution': allowPartialExecution, 'legs': legs}
        return self._request_with_params(POST, CREATE_RFQ, params)

    def cancel_rfq(self, rfqId: Any = None, clRfqId: Any = None) -> Dict[str, Any]:
        params = {'rfqId': rfqId, 'clRfqId': clRfqId}
        return self._request_with_params(POST, CANCEL_RFQ, params)

    def cancel_batch_rfqs(self, rfqIds: Any = None, clRfqIds: Any = None) -> Dict[str, Any]:
        if rfqIds is None:
            rfqIds = []
        if clRfqIds is None:
            clRfqIds = []
        params = {'rfqIds': rfqIds, 'clRfqIds': clRfqIds}
        return self._request_with_params(POST, CANCEL_BATCH_RFQS, params)

    def cancel_all_rfqs(self) -> Dict[str, Any]:
        params = {}
        return self._request_with_params(POST, CANCEL_ALL_RFQS, params)

    def execute_quote(self, rfqId: Any = None, quoteId: Any = None, legs: Any = None) -> Dict[str, Any]:
        if legs is None:
            legs = []
        params = {'rfqId': rfqId, 'quoteId': quoteId, 'legs': legs}
        return self._request_with_params(POST, EXECUTE_QUOTE, params)

    def create_quote(self, rfqId: Any = None, clQuoteId: Any = None, tag: Any = None, quoteSide: Any = None, legs: Any = None, anonymous: Any=False, expiresIn: Any = None) -> Dict[str, Any]:
        if legs is None:
            legs = []
        params = {'rfqId': rfqId, 'clQuoteId': clQuoteId, 'tag': tag, 'quoteSide': quoteSide, 'legs': legs,
                  'anonymous': anonymous, 'expiresIn': expiresIn}
        return self._request_with_params(POST, CREATE_QUOTE, params)

    def cancel_quote(self, quoteId: Any = None, clQuoteId: Any = None) -> Dict[str, Any]:
        params = {'quoteId': quoteId, 'clQuoteId': clQuoteId}
        return self._request_with_params(POST, CANCEL_QUOTE, params)

    def cancel_batch_quotes(self, quoteIds: Any = None, clQuoteIds: Any = None) -> Dict[str, Any]:
        params = {'quoteIds': quoteIds, 'clQuoteIds': clQuoteIds}
        return self._request_with_params(POST, CANCEL_BATCH_QUOTES, params)

    def cancel_all_quotes(self) -> Dict[str, Any]:
        params = {}
        return self._request_with_params(POST, CANCEL_ALL_QUOTES, params)

    def get_rfqs(self, rfqId: Any = None, clRfqId: Any = None,  state: Any = None, beginId: Any = None, endId: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'rfqId': rfqId, 'clRfqId': clRfqId, 'state': state, 'beginId': beginId, 'endId': endId, 'limit':limit}
        return self._request_with_params(GET, GET_RFQS, params)

    def get_quotes(self, rfqId: Any = None, clRfqId: Any = None, quoteId: Any = None, clQuoteId: Any = None, state: Any = None, beginId: Any = None, endId: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'rfqId': rfqId, 'clRfqId': clRfqId, 'quoteId':quoteId,'clQuoteId':clQuoteId, 'state': state, 'beginId': beginId, 'endId': endId, 'limit':limit}
        return self._request_with_params(GET, GET_QUOTES, params)

    def get_trades(self, rfqId: Any = None, clRfqId: Any = None, quoteId: Any = None, clQuoteId: Any = None, state: Any = None, beginId: Any = None, endId: Any = None, beginTs: Any = None,
                   endTs: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'rfqId': rfqId, 'clRfqId': clRfqId, 'quoteId': quoteId, 'clQuoteId': clQuoteId, 'state': state,
                  'beginId': beginId, 'endId': endId, 'beginTs': beginTs, 'endTs': endTs, 'limit': limit}
        return self._request_with_params(GET, GET_RFQ_TRADES, params)

    def get_public_trades(self, beginId: Any = None, endId: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'beginId': beginId, 'endId': endId, 'limit': limit}
        return self._request_with_params(GET, GET_PUBLIC_TRADES, params)

    def reset_mmp(self) -> Dict[str, Any]:
        return self._request_without_params(POST, MMP_RESET)

    def set_marker_instrument(self,params: Any = []) -> Dict[str, Any]:

        return self._request_with_params(POST, MAKER_INSTRUMENT_SETTING, params)

    #Get Quote products
    def get_quote_products(self) -> Dict[str, Any]:
        return self._request_without_params(GET, MAKER_INSTRUMENT_SETTING)

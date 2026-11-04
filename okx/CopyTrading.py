from .okxclient import OkxClient
from .consts import *


class CopyTradingAPI(OkxClient):
    # Get existing leading positions
    def get_existing_leading_positions(self, instId = None):
        params = {
            'instId': instId
        }
        return self._request_with_params(GET, GET_EXISTING_LEADING_POSITIONS, params)

    # Get leading position history
    def get_leading_position_history(self, instId = None, after = None, before = None, limit = None):
        params = {
            'instId': instId,
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, GET_LEADING_POSITIONS_HISTORY, params)

    # Place leading stop order
    def place_leading_stop_order(self, subPosId = None, tpTriggerPx = None, slTriggerPx = None, tpTriggerPxType = None,
                                 slTriggerPxType = None):
        params = {
            'subPosId': subPosId,
            'tpTriggerPx': tpTriggerPx,
            'slTriggerPx': slTriggerPx,
            'tpTriggerPxType': tpTriggerPxType,
            'slTriggerPxType': slTriggerPxType
        }
        return self._request_with_params(POST, PLACE_LEADING_STOP_ORDER, params)

    # Close leading position
    def close_leading_position(self, subPosId = None):
        params = {
            'subPosId': subPosId
        }
        return self._request_with_params(POST, CLOSE_LEADING_POSITIONS, params)

    # Get leading instruments
    def get_leading_instruments(self):
        return self._request_without_params(GET, GET_LEADING_POSITIONS)

    # Amend leading instruments
    def amend_leading_instruments(self, instId = None):
        params = {
            'instId': instId
        }
        return self._request_with_params(POST, AMEND_EXISTING_LEADING_POSITIONS, params)

    # Get profit sharing details
    def get_profit_sharing_details(self, after = None, before = None, limit = None):
        params = {
            'after': after,
            'before': before,
            'limit': limit
        }
        return self._request_with_params(GET, GET_PROFIT_SHARING_DETAILS, params)

    # Get total profit sharing
    def get_total_profit_sharing(self):
        return self._request_without_params(GET, GET_TOTAL_PROFIT_SHARING)

    # Get unrealized profit sharing details
    def get_unrealized_profit_sharing_details(self):
        return self._request_without_params(GET, GET_UNREALIZED_PROFIT_SHARING_DETAILS)

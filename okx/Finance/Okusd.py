from okx.okxclient import OkxClient
from okx.consts import (
    GET,
    _NO_CREDENTIAL,
    OKUSD_ACCOUNT,
    OKUSD_RATE_HISTORY,
    OKUSD_SUBSCRIBE_HISTORY,
    OKUSD_REDEEM_HISTORY,
    OKUSD_REWARDS_HISTORY,
)


class OkusdAPI(OkxClient):
    def get_account(self):
        return self._request_without_params(GET, OKUSD_ACCOUNT)

    def get_rate_history(self, limit = None, begin = None, end = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self._request_with_params(GET, OKUSD_RATE_HISTORY, params)

    def get_subscribe_history(self, limit = None, begin = None, end = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self._request_with_params(GET, OKUSD_SUBSCRIBE_HISTORY, params)

    def get_redeem_history(self, limit = None, begin = None, end = None, type = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if type is not None:
            params['type'] = type
        return self._request_with_params(GET, OKUSD_REDEEM_HISTORY, params)

    def get_rewards_history(self, limit = None, begin = None, end = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self._request_with_params(GET, OKUSD_REWARDS_HISTORY, params)

from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import (
    GET,
    OKUSD_ACCOUNT,
    OKUSD_RATE_HISTORY,
    OKUSD_SUBSCRIBE_HISTORY,
    OKUSD_REDEEM_HISTORY,
    OKUSD_REWARDS_HISTORY,
)


class OkusdAPI(OkxClient):
    def get_account(self) -> Dict[str, Any]:
        return self.request(GET, OKUSD_ACCOUNT)

    def get_rate_history(self, limit: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self.request(GET, OKUSD_RATE_HISTORY, params)

    def get_subscribe_history(self, limit: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self.request(GET, OKUSD_SUBSCRIBE_HISTORY, params)

    def get_redeem_history(self, limit: Any = None, begin: Any = None, end: Any = None, type: Any = None) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if type is not None:
            params['type'] = type
        return self.request(GET, OKUSD_REDEEM_HISTORY, params)

    def get_rewards_history(self, limit: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self.request(GET, OKUSD_REWARDS_HISTORY, params)

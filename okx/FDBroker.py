from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class FDBrokerAPI(OkxClient):
    def generate_rebate_details_download_link(self, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'begin': begin, 'end': end}
        return self.request(POST, FD_REBATE_PER_ORDERS, params)

    def get_rebate_details_download_link(self, type: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'type': type, 'begin': begin, 'end': end}
        return self.request(GET, FD_GET_REBATE_PER_ORDERS, params)

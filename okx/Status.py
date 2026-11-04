from typing import Any, Dict

from .okxclient import OkxClient
from .consts import *


class StatusAPI(OkxClient):
    def status(self, state: Any = None) -> Dict[str, Any]:
        params = {'state': state}
        return self._request_with_params(GET, STATUS, params)

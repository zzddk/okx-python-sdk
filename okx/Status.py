from .okxclient import OkxClient
from .consts import *


class StatusAPI(OkxClient):
    def status(self, state = None):
        params = {'state': state}
        return self._request_with_params(GET, STATUS, params)

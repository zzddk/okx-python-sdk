from .okxclient import OkxClient
from .consts import *


class FDBrokerAPI(OkxClient):
    def generate_rebate_details_download_link(self, begin ='', end = ''):
        params = {'begin': begin, 'end': end}
        return self._request_with_params(POST, FD_REBATE_PER_ORDERS, params)

    def get_rebate_details_download_link(self, type = '', begin = '', end = ''):
        params = {'type': type, 'begin': begin, 'end': end}
        return self._request_with_params(GET, FD_GET_REBATE_PER_ORDERS, params)

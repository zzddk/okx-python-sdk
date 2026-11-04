import json
import warnings

from httpx import Client
from loguru import logger

from . import consts as c
from . import utils


class OkxClient(Client):

    def __init__(self, api_key=c._NO_CREDENTIAL, api_secret_key=c._NO_CREDENTIAL,
                 passphrase=c._NO_CREDENTIAL, use_server_time=None, flag='1',
                 base_api=c.API_URL, debug=False, proxy=None, client=None):
        # Compatible with different versions of httpx
        # New versions (0.24.0+) use proxy, older versions use proxies
        try:
            super().__init__(base_url=base_api, http2=True, proxy=proxy)
        except TypeError:
            # Older versions of httpx use proxies parameter
            if proxy:
                super().__init__(base_url=base_api, http2=True, proxies={'http://': proxy, 'https://': proxy})
            else:
                super().__init__(base_url=base_api, http2=True)
        # Sharing an existing client routes every request through that client's
        # connection pool, so callers can fan one pool out across API classes.
        self._client = client
        if client is not None:
            self.API_KEY = client.API_KEY
            self.API_SECRET_KEY = client.API_SECRET_KEY
            self.PASSPHRASE = client.PASSPHRASE
            self.flag = client.flag
            self.debug = client.debug
            self.domain = client.domain
        else:
            self.API_KEY = api_key
            self.API_SECRET_KEY = api_secret_key
            self.PASSPHRASE = passphrase
            self.flag = flag
            self.debug = debug
            self.domain = base_api
        if use_server_time:
            warnings.warn(
                "use_server_time has no effect and will be removed in 0.5.0.",
                UserWarning,
                stacklevel=2,
            )

    def _request(self, method, request_path, params):
        if self._client is not None:
            return self._client._request(method, request_path, params)
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)
        timestamp = utils.get_timestamp()
        body = json.dumps(params) if method == c.POST else ""
        if self.API_KEY != '-1':
            sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body), self.debug), self.API_SECRET_KEY)
            header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag, self.debug)
        else:
            header = utils.get_header_no_sign(self.flag, self.debug)
        response = None
        if self.debug == True:
            logger.debug(f'domain: {self.domain}')
            logger.debug(f'url: {request_path}')
            logger.debug(f'body:{body}')
        if method == c.GET:
            response = self.get(request_path, headers=header)
        elif method == c.POST:
            response = self.post(request_path, data=body, headers=header)
        return response.json()

    def _request_without_params(self, method, request_path):
        return self._request(method, request_path, {})

    def _request_with_params(self, method, request_path, params):
        return self._request(method, request_path, params)

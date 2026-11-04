import json
import logging
import time
from typing import Any, Dict, Optional

import httpx
from httpx import Client

from . import consts as c
from . import exceptions, utils
from .consts.rate_limits import RATE_LIMITS
from .rate_limit import RateLimiter

logger = logging.getLogger(__name__)

# Business codes worth retrying: the request was rejected before it could be
# matched, so replaying it cannot double-execute. Everything else (parameter
# errors, insufficient balance, …) is a definitive answer, not a transient one.
_RETRYABLE_CODES = frozenset({'50001', '50004', '50011', '50013'})

# A POST body is only replayable if the caller supplied an idempotency key;
# otherwise a retry is a second order.
_IDEMPOTENCY_KEYS = ('clOrdId', 'algoClOrdId', 'reqId')


class OkxClient(Client):

    def __init__(self, api_key: str = c._NO_CREDENTIAL, api_secret_key: str = c._NO_CREDENTIAL,
                 passphrase: str = c._NO_CREDENTIAL, flag: str = '1',
                 base_api: str = c.API_URL, debug: bool = False,
                 proxy: Optional[str] = None, client: Optional["OkxClient"] = None,
                 raise_on_error: bool = True, max_retries: int = 0,
                 retry_backoff: float = 1.0, rate_limit: bool = False) -> None:
        # Compatible with different versions of httpx
        # New versions (0.24.0+) use proxy, older versions use proxies
        try:
            super().__init__(base_url=base_api, http2=True, proxy=proxy)
        except TypeError:
            # Older versions of httpx use proxies parameter
            if proxy:
                super().__init__(base_url=base_api, http2=True, proxies={'http://': proxy, 'https://': proxy})  # type: ignore[call-arg]
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
            self.raise_on_error = client.raise_on_error
            self.max_retries = client.max_retries
            self.retry_backoff = client.retry_backoff
            self._limiter = client._limiter
        else:
            self.API_KEY = api_key
            self.API_SECRET_KEY = api_secret_key
            self.PASSPHRASE = passphrase
            self.flag = flag
            self.debug = debug
            self.domain = base_api
            self.raise_on_error = raise_on_error
            self.max_retries = max_retries
            self.retry_backoff = retry_backoff
            self._limiter = RateLimiter(RATE_LIMITS) if rate_limit else None

    def _request(self, method: Any, request_path: Any, params: Any) -> Dict[str, Any]:
        if self._client is not None:
            return self._client._request(method, request_path, params)
        if method == c.GET:
            full_path = request_path + utils.parse_params_to_str(params)
        else:
            full_path = request_path
        body = json.dumps(utils.drop_none_params(params)) if method == c.POST else ""
        attempt = 0
        while True:
            if self._limiter is not None:
                self._limiter.acquire(request_path)
            try:
                payload, response = self._send(method, full_path, body)
            except httpx.TransportError:
                if not self._retry_allowed(attempt, method, params):
                    raise
                attempt += 1
                self._backoff(attempt)
                continue
            if self.raise_on_error:
                try:
                    self._raise_for_error(response, payload)
                except exceptions.OkxAPIException as exc:
                    if not self._retry_allowed(attempt, method, params) or not self._is_transient(exc):
                        raise
                    attempt += 1
                    self._backoff(attempt)
                    continue
            return payload

    def _send(self, method: Any, full_path: str, body: str) -> Any:
        """Perform one attempt.

        The timestamp is rebuilt on every call, so a retry never replays a
        signature that has already expired.
        """
        timestamp = utils.get_timestamp()
        if self.API_KEY != c._NO_CREDENTIAL:
            sign = utils.sign(utils.pre_hash(timestamp, method, full_path, str(body), self.debug), self.API_SECRET_KEY)
            header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag, self.debug)
        else:
            header = utils.get_header_no_sign(self.flag, self.debug)
        if self.debug == True:
            logger.debug(f'domain: {self.domain}')
            logger.debug(f'url: {full_path}')
            logger.debug(f'body:{body}')
        if method == c.GET:
            response = self.get(full_path, headers=header)
        elif method == c.POST:
            response = self.post(full_path, data=body, headers=header)
        else:
            raise ValueError(f"unsupported HTTP method: {method!r}")
        try:
            payload = response.json()
        except ValueError:
            if self.raise_on_error and response.status_code >= 400:
                raise exceptions.OkxAPIException(response)
            raise
        return payload, response

    def _retry_allowed(self, attempt: int, method: Any, params: Any) -> bool:
        """Whether the request may be replayed at all, regardless of the error."""
        if attempt >= self.max_retries:
            return False
        if method == c.GET:
            return True
        return isinstance(params, dict) and any(params.get(key) for key in _IDEMPOTENCY_KEYS)

    @staticmethod
    def _is_transient(exc: exceptions.OkxAPIException) -> bool:
        status = getattr(exc, 'status_code', None) or 0
        if status == 429 or status >= 500:
            return True
        return str(getattr(exc, 'code', '')) in _RETRYABLE_CODES

    def _backoff(self, attempt: int) -> None:
        delay = self.retry_backoff * (2 ** (attempt - 1))
        if delay > 0:
            time.sleep(delay)

    @staticmethod
    def _raise_for_error(response: Any, payload: Any) -> None:
        if response.status_code >= 400:
            raise exceptions.OkxAPIException(response, payload)
        if isinstance(payload, dict) and str(payload.get('code', '0')) != '0':
            raise exceptions.OkxAPIException(response, payload)

    def _request_without_params(self, method: Any, request_path: Any) -> Dict[str, Any]:
        return self._request(method, request_path, {})

    def _request_with_params(self, method: Any, request_path: Any, params: Any) -> Dict[str, Any]:
        return self._request(method, request_path, params)

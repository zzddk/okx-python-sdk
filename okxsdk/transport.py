"""The one place that talks HTTP.

Every REST call in the SDK ends up in `Transport.request`. Signing, parameter
serialization, retries, rate limiting and error mapping live here, so endpoint
modules stay declarative and `OkxClient` stays a thin facade over one transport.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

import httpx

from . import consts as c
from . import exceptions, utils
from .consts.rate_limits import RATE_LIMITS
from .rate_limit import RateLimiter

logger = logging.getLogger(__name__)

# Business codes OKX tells you to retry: the service is unavailable, the rate
# limit was hit, or the system is busy - "please try again later". Replaying one
# of these is what the vendor asks for.
_RETRYABLE_CODES = frozenset({'50001', '50011', '50013'})

# Business codes whose outcome is unknown. OKX says a timeout "does not mean
# that the request was successful or failed, please check the request result",
# so replaying it could execute the order twice. Checked before the HTTP-status
# shortcut, so a 500 carrying one of these is not retried either.
_OUTCOME_UNKNOWN_CODES = frozenset({'50004', '51149'})

# A POST body is only replayable if the caller supplied an idempotency key;
# otherwise a retry is a second order.
_IDEMPOTENCY_KEYS = ('clOrdId', 'algoClOrdId', 'reqId')


class Transport:
    """Owns one `httpx.Client` and the policy shared by every request.

    `OkxClient` holds one instance; API classes reach it through `request`.
    Passing the same instance to several API classes shares one connection
    pool. Passing `http=` bypasses environment proxy detection: whoever injects
    a transport is responsible for its proxy configuration.
    """

    def __init__(self, api_key: str = c._NO_CREDENTIAL, api_secret_key: str = c._NO_CREDENTIAL,
                 passphrase: str = c._NO_CREDENTIAL, flag: str = '1',
                 base_api: str = c.API_URL, debug: bool = False,
                 proxy: Optional[str] = None, raise_on_error: bool = True,
                 max_retries: int = 0, retry_backoff: float = 1.0,
                 rate_limit: bool = False,
                 http: Optional[httpx.BaseTransport] = None) -> None:
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.PASSPHRASE = passphrase
        self.flag = flag
        self.debug = debug
        self.domain = base_api
        self.proxy = proxy
        self.raise_on_error = raise_on_error
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._limiter = RateLimiter(RATE_LIMITS) if rate_limit else None
        self._http = self._make_http(base_api, proxy, http)

    @staticmethod
    def _make_http(base_api: str, proxy: Optional[str],
                   http: Optional[httpx.BaseTransport]) -> httpx.Client:
        if http is not None:
            return httpx.Client(base_url=base_api, transport=http)
        # Compatible with different versions of httpx
        # New versions (0.24.0+) use proxy, older versions use proxies
        try:
            return httpx.Client(base_url=base_api, http2=True, proxy=proxy)
        except TypeError:
            # Older versions of httpx use proxies parameter
            if proxy:
                return httpx.Client(base_url=base_api, http2=True,
                                    proxies={'http://': proxy, 'https://': proxy})  # type: ignore[call-arg]
            return httpx.Client(base_url=base_api, http2=True)

    def request(self, method: Any, path: Any, params: Any, *,
                replayable: Optional[bool] = None) -> Dict[str, Any]:
        """Send one API call and return the decoded JSON payload.

        `params` holds the request arguments; `None` means there are none. A
        `None` *value* means "do not send this argument": it is dropped from
        the GET query string and from the JSON body of a POST. An empty string
        is a value and is sent as one.

        GET arguments become the query string, POST arguments become a JSON
        body. `True`/`False` serialize to `'true'`/`'false'`; a list or dict
        argument is inlined as compact JSON.

        `replayable` says whether the same call may be sent more than once.
        The default (`None`) derives it: GET is always replayable, POST only
        when the body carries an idempotency key (`clOrdId`, `algoClOrdId` or
        `reqId`). Transient failures — `httpx.TransportError`, HTTP 429/5xx and
        business codes 50001/50011/50013 — are retried up to `max_retries`
        times with exponential backoff. A failure whose outcome is unknown
        (`50004` request timeout, `51149` order timeout) is never retried: OKX
        says the request may or may not have been processed, so replaying it
        could execute twice. Every attempt rebuilds the timestamp and
        signature, so a retry never replays an expired one.

        A 429/5xx response whose body is not JSON raises `OkxAPIException`
        carrying that status code, and is retried like any other transient
        failure when the request is replayable.

        With `raise_on_error=False` an HTTP error with a JSON body is returned
        as a payload instead of raising, so that error is not retried; network
        failures still follow the retry policy. A body that is not JSON always
        raises `ValueError` — an error status included, since there is no
        payload to return. That has been the behaviour since 0.4.
        """
        if params is None:
            params = {}
        if replayable is None:
            replayable = self._is_replayable(method, params)
        attempt = 0
        while True:
            if self._limiter is not None:
                self._limiter.acquire(path)
            try:
                return self._send(method, path, params)
            except httpx.TransportError:
                if not self._retry_allowed(attempt, replayable):
                    raise
            except exceptions.OkxAPIException as exc:
                if not self._retry_allowed(attempt, replayable) or not self._is_transient(exc):
                    raise
            attempt += 1
            self._backoff(attempt)

    def _send(self, method: Any, path: str, params: Any) -> Dict[str, Any]:
        """Perform one attempt.

        The timestamp is rebuilt on every call, so a retry never replays a
        signature that has already expired.
        """
        if method == c.GET:
            full_path = path + utils.parse_params_to_str(params)
            body = ""
        else:
            full_path = path
            body = json.dumps(utils.drop_none_params(params))
        timestamp = utils.get_timestamp()
        if self.API_KEY != c._NO_CREDENTIAL:
            sign = utils.sign(utils.pre_hash(timestamp, method, full_path, str(body), self.debug), self.API_SECRET_KEY)
            header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag, self.debug)
        else:
            header = utils.get_header_no_sign(self.flag, self.debug)
        if self.debug:
            logger.debug(f'domain: {self.domain}')
            logger.debug(f'url: {full_path}')
            logger.debug(f'body:{body}')
        if method == c.GET:
            response = self._http.get(full_path, headers=header)
        elif method == c.POST:
            response = self._http.post(full_path, content=body, headers=header)
        else:
            raise ValueError(f"unsupported HTTP method: {method!r}")
        try:
            payload = response.json()
        except ValueError:
            if self.raise_on_error and response.status_code >= 400:
                raise exceptions.OkxAPIException(response)
            raise
        if self.raise_on_error:
            self._raise_for_error(response, payload)
        return payload

    def _is_replayable(self, method: Any, params: Any) -> bool:
        """Whether the request may be replayed at all, regardless of the error."""
        if method == c.GET:
            return True
        return isinstance(params, dict) and any(params.get(key) for key in _IDEMPOTENCY_KEYS)

    def _retry_allowed(self, attempt: int, replayable: bool) -> bool:
        return replayable and attempt < self.max_retries

    @staticmethod
    def _is_transient(exc: exceptions.OkxAPIException) -> bool:
        code = str(getattr(exc, 'code', ''))
        if code in _OUTCOME_UNKNOWN_CODES:
            return False
        status = getattr(exc, 'status_code', None) or 0
        if status == 429 or status >= 500:
            return True
        return code in _RETRYABLE_CODES

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

    def close(self) -> None:
        self._http.close()

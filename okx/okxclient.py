from typing import Any, Dict, Iterator, Optional

from . import pagination
from .transport import Transport


class OkxClient:
    """Base class for the REST API surface: one `Transport`, one `request` seam.

    Every API class is constructed with a `Transport` that holds the credentials
    and the policy (retries, rate limits, proxy). Passing the same `Transport` to
    several API classes shares one connection pool and one configuration.
    """

    def __init__(self, transport: Transport) -> None:
        if not isinstance(transport, Transport):
            raise TypeError(f"transport must be a Transport, not {type(transport).__name__}")
        self._t = transport

    @property
    def transport(self) -> Transport:
        """The one configuration surface: credentials, environment and policy.

        API classes no longer copy individual fields; read them here, e.g.
        `api.transport.debug` or `api.transport.max_retries`.
        """
        return self._t

    def request(self, method: Any, path: Any,
                params: Optional[Dict[str, Any]] = None, *,
                replayable: Optional[bool] = None) -> Dict[str, Any]:
        """Send one API call; see `okx.transport.Transport.request` for the policy.

        Every endpoint method funnels through here, so retries, rate limits and
        error mapping apply uniformly. `params` defaults to no arguments, and
        `replayable` overrides the derived retry safety for one call.
        """
        return self._t.request(method, path, params, replayable=replayable)

    def paginate(self, method: Any, cursor: Optional[str] = None,
                 params: Optional[Dict[str, Any]] = None,
                 page_size: Optional[int] = pagination.DEFAULT_PAGE_SIZE,
                 max_pages: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """Walk a list endpoint backwards, one record at a time.

        Validation and the walk live in `okx.pagination.paginate`; this method
        only forwards, so `api.paginate(...)` and `okx.pagination.paginate(...)`
        behave identically (including failing at the call site when `cursor`
        is missing).
        """
        return pagination.paginate(method, cursor=cursor, params=params,
                                   page_size=page_size, max_pages=max_pages)

    def close(self) -> None:
        """Close the underlying connection pool (shared with every user of this transport)."""
        self._t.close()

    def __enter__(self) -> "OkxClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

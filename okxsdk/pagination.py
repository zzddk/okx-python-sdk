"""Backward pagination over OKX list endpoints.

OKX list endpoints page with `after`: pass the cursor of the last record you
already have, and the response returns older ones. `before` walks the other
direction (polling for new records) and is deliberately not supported here —
mixing the two makes "which page am I on" meaningless.

This module owns both halves of that contract: what makes a call meaningful
and how the walk moves. `paginate()` projects the caller's request once, before
any page is fetched, and `_walk()` only carries out the result:

* `cursor` is required — `after` refers to a different response field per
  endpoint, and a few endpoints page by number instead.
* `before` is rejected: `after` is the only direction this module walks.
* `limit` comes from `page_size` alone; a `limit` in `params` is rejected so
  the walk has one knob. `page_size=None` sends no `limit` at all, while
  `page_size <= 0` and a negative `max_pages` are rejected at the call site.
* `params['after']` seeds the walk; every other key (`begin`, `end`,
  `instType`, …) is sent unchanged on every page.

`OkxClient.paginate` only forwards.
"""

import inspect
from typing import Any, Callable, Dict, Iterator, Optional

DEFAULT_PAGE_SIZE = 100


def paginate(fetch: Callable[..., Dict[str, Any]], cursor: Optional[str] = None,
             params: Optional[Dict[str, Any]] = None,
             page_size: Optional[int] = DEFAULT_PAGE_SIZE,
             max_pages: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    """Yield every record reachable by walking `after` backwards.

    ```python
    for bill in account.paginate(account.get_account_bills, cursor='billId',
                                 params={'instType': 'SPOT'}, page_size=100):
        ...
    ```

    `cursor` names the response field that `after` refers to. It is required
    because the field differs per endpoint (`ordId`, `billId`, `ts`, …) and a
    wrong guess silently skips or repeats records. A missing or empty cursor
    raises here, before the first page is requested, so a wrong call fails at
    the call site rather than in the middle of the loop.

    `params` is the filter set sent with every page. `after` in it resumes the
    walk from that cursor; `before` and `limit` are rejected here, before the
    first page is requested, because the walk owns direction and page size. The
    caller's dict is copied, never modified.

    The walk stops at an empty page or when the cursor stops advancing. It does
    **not** stop on a short page: endpoints cap `limit` at their own maximum, so
    a short page means the cap was hit, not that the data ran out. The cost is
    one extra request that returns an empty page.
    """
    if not cursor:
        raise ValueError(_missing_cursor_message(fetch))
    if page_size is not None and page_size <= 0:
        raise ValueError(
            f"page_size must be positive for paginate({_callable_name(fetch)}), "
            f"got {page_size!r}")
    if max_pages is not None and max_pages < 0:
        raise ValueError(
            f"max_pages must not be negative for paginate({_callable_name(fetch)}), "
            f"got {max_pages!r}")
    filters, after = _project(fetch, params, page_size)
    return _walk(fetch, cursor, filters, after, max_pages)


def _project(fetch: Callable[..., Any], params: Optional[Dict[str, Any]],
             page_size: Optional[int]):
    """Turn the caller's params into the filters and cursor `_walk` may use."""
    filters = dict(params or {})
    if 'before' in filters:
        raise ValueError(
            f"before is not supported by paginate({_callable_name(fetch)}); "
            "walk forward with after")
    if 'limit' in filters:
        raise ValueError(
            f"limit is not accepted by paginate({_callable_name(fetch)}); "
            "set page_size instead")
    after = filters.pop('after', None)
    if page_size is not None:
        filters['limit'] = page_size
    return filters, after


def _callable_name(fetch: Callable[..., Any]) -> str:
    name = getattr(fetch, '__name__', None)
    return name if isinstance(name, str) else str(fetch)


def _missing_cursor_message(fetch: Callable[..., Any]) -> str:
    """Explain why this call needs a cursor, naming the callable."""
    name = getattr(fetch, '__name__', str(fetch))
    try:
        parameters = inspect.signature(fetch).parameters
    except (TypeError, ValueError):
        parameters = {}
    if 'page' in parameters:
        return f"{name} pages by page number, not by cursor; call it directly with page="
    return (f"cursor is required for {name}: name the response field 'after' refers to, "
            "for example cursor='billId'")


def _walk(fetch: Callable[..., Dict[str, Any]], cursor: str,
          filters: Dict[str, Any], after: Any,
          max_pages: Optional[int]) -> Iterator[Dict[str, Any]]:
    seen = set()
    pages = 0
    while True:
        if max_pages is not None and pages >= max_pages:
            return
        if after is None:
            payload = fetch(**filters)
        else:
            payload = fetch(after=after, **filters)
        pages += 1
        data = (payload or {}).get('data') or []
        if not data:
            return
        for item in data:
            yield item
        last = data[-1].get(cursor)
        if last is None or last == after or last in seen:
            return
        seen.add(last)
        after = last

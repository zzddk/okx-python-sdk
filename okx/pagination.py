"""Backward pagination over OKX list endpoints.

OKX list endpoints page with `after`: pass the cursor of the last record you
already have, and the response returns older ones. `before` walks the other
direction (polling for new records) and is deliberately not supported here —
mixing the two makes "which page am I on" meaningless.
"""

from typing import Any, Callable, Dict, Iterator, Optional

DEFAULT_PAGE_SIZE = 100


def paginate(fetch: Callable[..., Dict[str, Any]], cursor: str,
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
    wrong guess silently skips or repeats records.

    The walk stops at an empty page or when the cursor stops advancing. It does
    **not** stop on a short page: endpoints cap `limit` at their own maximum, so
    a short page means the cap was hit, not that the data ran out. The cost is
    one extra request that returns an empty page.
    """
    if not cursor:
        raise ValueError(
            "cursor is required: name the response field 'after' refers to, "
            "for example cursor='billId'"
        )
    base = dict(params or {})
    after = base.pop('after', None)
    if page_size is not None:
        base['limit'] = page_size
    seen = set()
    pages = 0
    while True:
        if max_pages is not None and pages >= max_pages:
            return
        if after is None:
            payload = fetch(**base)
        else:
            payload = fetch(after=after, **base)
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

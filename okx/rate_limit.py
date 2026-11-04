"""Sliding-window rate limiting for REST calls.

Kept out of `OkxClient` so it can be unit-tested without httpx and so the
retry loop stays readable. Unknown paths are never throttled.
"""

import threading
import time
from typing import Callable, Dict, Hashable, Tuple


class RateLimiter:
    """At most `count` calls per `window` seconds for each request path."""

    def __init__(self, limits: Dict[Hashable, Tuple[int, float]],
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self._limits = dict(limits)
        self._calls: Dict[Hashable, list] = {}
        self._lock = threading.Lock()
        # Injectable so tests can assert the wait without spending it.
        self._sleep = sleep

    def acquire(self, path: Hashable) -> None:
        """Block until a slot for `path` is free, then record the call."""
        limit = self._limits.get(path)
        if limit is None:
            return
        count, window = limit
        while True:
            with self._lock:
                now = time.monotonic()
                recent = [stamp for stamp in self._calls.get(path, ()) if now - stamp < window]
                if len(recent) < count:
                    recent.append(now)
                    self._calls[path] = recent
                    return
                wait = window - (now - recent[0])
            # Sleep outside the lock so other paths are not blocked by this one.
            self._sleep(max(wait, 0.001))

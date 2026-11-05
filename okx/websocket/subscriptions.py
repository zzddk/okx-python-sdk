"""Subscription registry: which callback receives which server message.

A WebSocket session needs one relation that the socket itself does not carry:
a subscription and the callback that wants its messages. This module holds
that relation as plain data -- no event loop, no socket, no log sink -- so the
routing rules can be tested without a connection.

Routing order
-------------
`take(payload)` looks at `payload["arg"]` first. The whole arg dict is the
key, spelled `json.dumps(arg, sort_keys=True)`, which is byte-for-byte the key
0.11 used for replay; subscriptions recorded before an upgrade therefore
reconnect into the same table. When `arg` is absent or not registered, the
`id` of the payload is tried -- an order acknowledgement carries no `arg`, so
its `id` is the only identity available. A miss returns `None` and the caller
decides what the fallback is.

A subscription may have no callback. Such an entry exists only so a reconnect
can replay it, and `take` returns `None` for it like any other miss. Entries
added with the same `arg` replace the previous callback; there is no second
consumer, so no broadcasting. Request entries are one-shot: `take` removes the
entry it matched.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

Callback = Callable[[Any], Any]


class Subscription:
    """One arg and the callback that receives messages for it.

    `params` is a tuple because a subscribe frame carries a list; the table
    keys entries one arg at a time, so an entry's tuple holds exactly that arg.
    Replacing a subscription builds a new entry instead of mutating this one.
    """

    __slots__ = ("params", "callback")

    def __init__(
        self,
        params: Tuple[Dict[str, Any], ...],
        callback: Optional[Callback],
    ) -> None:
        self.params = params
        self.callback = callback


def key(arg: Dict[str, Any]) -> str:
    """The routing key for one arg: the whole dict, order-independent.

    This is the single implementation of the key contract; callers that need
    to key their own view of the table (such as the deprecated
    `WsBaseAsync.subscriptions` property) must use it rather than repeat the
    serialisation.
    """
    return json.dumps(arg, sort_keys=True)


class Subscriptions:
    """The subscription table and the callback under which each was added."""

    def __init__(self) -> None:
        self._entries: Dict[str, Subscription] = {}
        self._requests: Dict[str, Callback] = {}

    def add(
        self,
        params: Sequence[Dict[str, Any]],
        callback: Optional[Callback] = None,
    ) -> Tuple[Subscription, ...]:
        """Register every arg in `params`, replacing any callback already there.

        Entries keep the order they were first added in; adding the same arg
        again replaces the entry in place. Returns the entries added, one per
        arg, so a caller can report what it accepted.
        """
        added: List[Subscription] = []
        for arg in params:
            if not isinstance(arg, dict):
                continue
            entry = Subscription((dict(arg),), callback)
            self._entries[key(arg)] = entry
            added.append(entry)
        return tuple(added)

    def remove(self, params: Sequence[Dict[str, Any]]) -> Tuple[Subscription, ...]:
        """Drop every arg in `params`; unknown args are ignored."""
        removed: List[Subscription] = []
        for arg in params:
            if not isinstance(arg, dict):
                continue
            entry = self._entries.pop(key(arg), None)
            if entry is not None:
                removed.append(entry)
        return tuple(removed)

    def add_request(self, request_id: str, callback: Callback) -> None:
        """Associate a one-shot response, matched by `id`, with `callback`."""
        self._requests[request_id] = callback

    def drop_requests(self) -> None:
        """Forget every pending request; used on reconnect and on stop()."""
        self._requests.clear()

    def take(self, payload: Any) -> Optional[Callback]:
        """Return the callback that owns `payload`, or `None` on a miss.

        Matching is by `arg` first, then by `id`. A subscription hit leaves
        the entry in place, so the next message for the same channel routes
        the same way. A request hit removes the entry. Server data is not
        trusted: a non-dict payload, a non-dict `arg` or a non-string `id`
        yields `None` instead of raising.
        """
        if not isinstance(payload, dict):
            return None
        arg = payload.get("arg")
        if isinstance(arg, dict):
            try:
                entry = self._entries.get(key(arg))
            except (TypeError, ValueError):
                entry = None
            if entry is not None:
                return entry.callback
        request_id = payload.get("id")
        if isinstance(request_id, str):
            return self._requests.pop(request_id, None)
        return None

    def replay(self) -> List[Dict[str, Any]]:
        """Return copies of the subscribed args, in the order they were added.

        Removed entries and pending requests do not appear. The copies are
        detached from the table, so a caller may modify them freely.
        """
        return [dict(entry.params[0]) for entry in self._entries.values()]

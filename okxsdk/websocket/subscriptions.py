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

Only a routable arg can enter the table: a dict whose `channel` is a non-blank
string. `add` and `remove` check the whole batch first, so a rejected batch
leaves the table untouched.

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


def key(arg: Dict[str, Any]) -> str:
    """The routing key for one arg: the whole dict, order-independent.

    This is the single implementation of the key contract; callers that need
    to key their own view of the table (such as the deprecated
    `WsBaseAsync.subscriptions` property) must use it rather than repeat the
    serialisation.
    """
    return json.dumps(arg, sort_keys=True)


def _require_routable(arg: Any) -> None:
    """Reject an arg the server cannot route: not a dict, or a blank channel.

    Both entry points share this rule, so `add` and `remove` accept exactly
    the same args and a batch is checked before it changes anything.
    """
    if not isinstance(arg, dict):
        raise ValueError(f"subscription arg must be a dict, got {arg!r}")
    channel = arg.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"channel must be a non-blank string, got {channel!r}")


class Subscriptions:
    """The subscription table and the callback under which each was added."""

    def __init__(self) -> None:
        self._entries: Dict[str, Tuple[Dict[str, Any], Optional[Callback]]] = {}
        self._requests: Dict[str, Callback] = {}

    def add(
        self,
        params: Sequence[Dict[str, Any]],
        callback: Optional[Callback] = None,
    ) -> None:
        """Register every arg in `params`, replacing any callback already there.

        The whole batch is checked before the table is written: one unroutable
        arg raises `ValueError` and leaves the table exactly as it was.
        Entries keep the order they were first added in; adding the same arg
        again replaces the entry in place.
        """
        for arg in params:
            _require_routable(arg)
        for arg in params:
            self._entries[key(arg)] = (dict(arg), callback)

    def remove(self, params: Sequence[Dict[str, Any]]) -> None:
        """Drop every arg in `params`; args never added are ignored.

        Like `add`, the whole batch is checked before anything is removed, so
        an unroutable arg raises `ValueError` and the table stays as it was.
        """
        for arg in params:
            _require_routable(arg)
        for arg in params:
            self._entries.pop(key(arg), None)

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
                return entry[1]
        request_id = payload.get("id")
        if isinstance(request_id, str):
            return self._requests.pop(request_id, None)
        return None

    def replay(self) -> List[Dict[str, Any]]:
        """Return copies of the subscribed args, in the order they were added.

        Removed entries and pending requests do not appear. The copies are
        detached from the table, so a caller may modify them freely.
        """
        return [dict(arg) for arg, _ in self._entries.values()]

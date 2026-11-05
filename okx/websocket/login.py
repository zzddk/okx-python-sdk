"""The login handshake.

A private channel answers a login request with exactly one frame:
`{"event": "login", "code": "0"}` when accepted, a non-zero `code` when
rejected. Everything that decides *which* frame answers the request and *what
counts as a rejection* lives here, so the two ways a session can receive that
frame share one rule:

- the read loop feeds every parsed frame through `feed()`;
- when no reader is running (between a reconnect and the reader restart, or
  after `connect()` and before `start()`), `read()` pulls frames from the
  socket itself and hands everything else to `deliver`.

Both paths settle the same state; `wait()` is how the read-loop case blocks.

`login_payload()` builds the request those paths wait for: the message the
server expects is `str(timestamp) + 'GET' + '/users/self/verify'`, signed with
the API secret and wrapped in the JSON envelope. The signature primitive itself
lives in `okx.utils.sign` and is shared with the REST layer.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Awaitable, Callable

from okx import utils

DEFAULT_LOGIN_TIMEOUT = 10.0

Deliver = Callable[[str], Awaitable[None]]


def login_payload(
    api_key: str,
    passphrase: str,
    secret_key: str,
    timestamp: int | None = None,
) -> str:
    """Build the login request for a private channel.

    `timestamp` defaults to the local clock in whole seconds. Tests pass a
    fixed value so the whole string can be compared byte for byte.
    """
    if timestamp is None:
        timestamp = int(time.time())
    message = str(timestamp) + 'GET' + '/users/self/verify'
    signature = utils.sign(message, secret_key).decode('utf-8')
    payload = {
        "op": "login",
        "args": [
            {
                "apiKey": api_key,
                "passphrase": passphrase,
                "timestamp": timestamp,
                "sign": signature,
            }
        ],
    }
    return json.dumps(payload)


class LoginHandshake:
    """Wait for the answer to one login request.

    One instance serves one login attempt: after the answering frame arrives,
    later frames are ignored by that instance. A fresh connection gets a fresh
    instance, which is why a reconnect cannot inherit a stale result.
    """

    def __init__(self, timeout: float = DEFAULT_LOGIN_TIMEOUT) -> None:
        self.timeout = timeout
        self._answer = asyncio.Event()
        self._rejection: ConnectionError | None = None

    @staticmethod
    def is_ack(payload: Any) -> bool:
        """Whether a parsed frame is a login answer (accepted or rejected)."""
        return isinstance(payload, dict) and payload.get("event") == "login"

    @staticmethod
    def rejection(payload: dict[str, Any]) -> ConnectionError | None:
        """The error a login answer carries, or None when it was accepted."""
        if str(payload.get("code", "0")) != "0":
            return ConnectionError(
                f"login rejected: code={payload.get('code')} msg={payload.get('msg')}"
            )
        return None

    def feed(self, payload: Any) -> bool:
        """Take one parsed frame.

        Returns True when the frame answered this login — the caller should not
        deliver it anywhere else. Returns False for every other frame, which
        stays the caller's to route.
        """
        if not self.is_ack(payload):
            return False
        if not self._answer.is_set():
            self._rejection = self.rejection(payload)
            self._answer.set()
        return True

    async def wait(self) -> None:
        """Block until `feed()` takes the answer, then raise or return."""
        try:
            await asyncio.wait_for(self._answer.wait(), self.timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(self._timeout_message()) from None
        if self._rejection is not None:
            raise self._rejection

    async def read(self, websocket: Any, parse: Callable[[Any], Any],
                   deliver: Deliver) -> None:
        """Read the socket until the answer arrives.

        Frames that are not the answer are handed to `deliver` — during a
        reconnect they are pushed data the caller still expects to see.
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.timeout
        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TimeoutError(self._timeout_message())
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                raise TimeoutError(self._timeout_message()) from None
            if self.feed(parse(message)):
                if self._rejection is not None:
                    raise self._rejection
                return
            await deliver(message)

    def _timeout_message(self) -> str:
        return f"no login acknowledgement within {self.timeout}s"

"""The login handshake.

A private channel answers a login request with exactly one frame:
`{"event": "login", "code": "0"}` when accepted, a non-zero `code` when
rejected. Everything that decides *which* frame answers the request and *what
counts as a rejection* lives here, so every frame the session reads goes
through one rule.

The read loop feeds every parsed frame through `feed()`; `wait()` is how the
request blocks until its answer arrives. The reader always runs once the
connection supervisor has opened the socket, so there is no second path that
reads the socket itself.

`login_payload()` builds the request those paths wait for: the message the
server expects is `str(timestamp) + 'GET' + '/users/self/verify'`, signed with
the API secret and wrapped in the JSON envelope. The signature primitive itself
lives in `okx.utils.sign` and is shared with the REST layer.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from okx import utils
from okx.exceptions import PermanentConnectionError

DEFAULT_LOGIN_TIMEOUT = 10.0


class LoginRejected(PermanentConnectionError):
    """The server refused these credentials; replaying them cannot help.

    Still a `ConnectionError` through its base, so callers that caught the
    previous exception keep working.
    """


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
        self._rejection: BaseException | None = None

    @staticmethod
    def is_ack(payload: Any) -> bool:
        """Whether a parsed frame is a login answer (accepted or rejected)."""
        return isinstance(payload, dict) and payload.get("event") == "login"

    @staticmethod
    def rejection(payload: dict[str, Any]) -> LoginRejected | None:
        """The error a login answer carries, or None when it was accepted.

        A rejection is permanent: the same credentials get the same answer, so
        the reconnect loop must not retry it.
        """
        if str(payload.get("code", "0")) != "0":
            return LoginRejected(
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

    def abort(self, error: BaseException) -> None:
        """End the wait early because the connection is gone.

        A socket that dies while the login request is in flight never answers.
        Without this the caller would wait out the full timeout; the read loop
        reports the loss, and whoever owns the handshake turns it into this.
        """
        if not self._answer.is_set():
            self._rejection = error
            self._answer.set()

    async def wait(self) -> None:
        """Block until `feed()` takes the answer, then raise or return."""
        try:
            await asyncio.wait_for(self._answer.wait(), self.timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(self._timeout_message()) from None
        if self._rejection is not None:
            raise self._rejection

    def _timeout_message(self) -> str:
        return f"no login acknowledgement within {self.timeout}s"

"""Test doubles for the transport seam.

Unit tests never build a real `httpx.Client`: with a SOCKS proxy in the
environment that fails while parsing the proxy, which has nothing to do with
the code under test. Construct clients with `FakeTransport()` when requests are
mocked further up, or with `mock_transport(handler)` when the wire format and
retry behaviour matter.
"""

from typing import Any, Dict, Optional

import httpx

from okxsdk.transport import Transport


class FakeTransport(Transport):
    """Implements the Transport interface; records calls, never sends.

    Skips `Transport.__init__` on purpose: that is the part that builds an
    `httpx.Client`, which is what these tests must avoid.
    """

    def __init__(self, payload: Optional[Dict[str, Any]] = None) -> None:
        self.calls = []
        self.payload = {'code': '0'} if payload is None else payload
        self.closed = False

    def request(self, method: Any, path: Any, params: Any, *,
                replayable: Optional[bool] = None) -> Dict[str, Any]:
        self.calls.append((method, path, params))
        return self.payload

    def close(self) -> None:
        self.closed = True


def sent_params(mock, call=0):
    """The arguments a mocked `request` would actually put on the wire.

    `Transport` drops `None` values, so `None` means "not supplied" whether
    the endpoint passed the key or left it out. Tests should assert against this
    view: it says which arguments are sent, not how the endpoint spells "unset".
    """
    args = mock.call_args_list[call].args
    params = args[2] if len(args) > 2 else {}
    if not isinstance(params, dict):
        return params
    return {key: value for key, value in params.items() if value is not None}


def assert_request(mock, method, path, params=None):
    """Assert the single call a mocked `request` received."""
    mock.assert_called_once()
    args = mock.call_args.args
    assert args[0] == method, f"expected {method!r}, sent {args[0]!r}"
    assert args[1] == path, f"expected {path!r}, sent {args[1]!r}"
    assert sent_params(mock) == ({} if params is None else params)


def mock_transport(handler=None, **config):
    """A real Transport wired to `httpx.MockTransport` instead of the network."""
    if handler is None:
        def handler(request):
            return httpx.Response(200, json={'code': '0'})
    return Transport(http=httpx.MockTransport(handler), **config)

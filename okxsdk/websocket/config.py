"""Turning one `Transport` into the options for a WebSocket session.

Both WS clients inherit their credentials, environment and proxy from the REST
client's `Transport`; only the host differs. This module owns that mapping —
field names, the demo switch, the `debug` fallback, the proxy rule — so a new
transport field is added in one place. Each client supplies its own host table.

Only `transport.proxy` is inherited. `Transport(http=...)` turning off
environment-proxy detection is a REST rule and does not extend here: with no
proxy set, the WebSocket still follows the environment.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from okxsdk.transport import Transport

# "is demo trading" -> endpoint. Keyed by the boolean, not by name, so the
# caller cannot pick a host that does not belong to its client.
Hosts = Mapping[bool, str]


def require_transport(value: Any) -> Transport:
    """Reject anything that is not a `Transport`, with the same message everywhere."""
    if not isinstance(value, Transport):
        raise TypeError(
            "transport must be an okxsdk.transport.Transport instance, "
            f"got {type(value).__name__}"
        )
    return value


def session_config(transport: Transport, hosts: Hosts,
                   url: Optional[str] = None,
                   debug: Optional[bool] = None) -> Dict[str, Any]:
    """Constructor options for a WS session built from a REST `Transport`.

    `hosts` maps "is demo trading" to an endpoint. `transport.flag == '1'`
    means demo trading, the same switch the REST side uses. `url` overrides the
    host entirely; `debug` falls back to the transport's value.
    """
    transport = require_transport(transport)
    if url is None:
        url = hosts[str(transport.flag) == '1']
    return {
        'url': url,
        'apiKey': transport.API_KEY,
        'passphrase': transport.PASSPHRASE,
        'secretKey': transport.API_SECRET_KEY,
        'debug': transport.debug if debug is None else debug,
        'proxy': transport.proxy,
    }

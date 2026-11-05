"""Public and business WebSocket client."""

from __future__ import annotations

from typing import ClassVar, Optional

from okx import consts
from okx.transport import Transport
from okx.websocket.config import require_transport, session_config
from okx.websocket.WsBaseAsync import WsBaseAsync


class WsPublicAsync(WsBaseAsync):
    # "is demo trading" -> endpoint. Also the default url for a bare client:
    # with no transport there is no channel and no demo switch, and the live
    # public endpoint is what that means.
    _HOSTS: ClassVar[dict[bool, str]] = {
        False: consts.WS_PUBLIC_URL,
        True: consts.WS_PUBLIC_DEMO_URL,
    }

    # channel -> {"is demo trading": endpoint}. A channel is only meaningful for
    # a real transport, so the transport is checked first.
    _CHANNELS: ClassVar[dict[str, dict[bool, str]]] = {
        'public': _HOSTS,
        'business': {False: consts.WS_BUSINESS_URL, True: consts.WS_BUSINESS_DEMO_URL},
    }

    @classmethod
    def from_transport(
        cls,
        transport: Transport,
        channel: str = 'public',
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPublicAsync":
        """Build from the `Transport` that configures the REST side.

        `channel` picks the public or business host table; credentials,
        environment and proxy come from the transport (see
        `okx.websocket.config.session_config`). `url` overrides the host.
        """
        require_transport(transport)
        if not isinstance(channel, str) or channel not in cls._CHANNELS:
            raise ValueError(f"channel must be 'public' or 'business', got {channel!r}")
        return cls(**session_config(transport, cls._CHANNELS[channel], url=url, debug=debug))

"""Public and business WebSocket client."""

from __future__ import annotations

from typing import Any, Optional

from okx import consts
from okx.transport import Transport
from okx.websocket.WsBaseAsync import WsBaseAsync


class WsPublicAsync(WsBaseAsync):
    @classmethod
    def from_transport(
        cls,
        transport: Transport,
        channel: str = 'public',
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPublicAsync":
        """Build from the `Transport` that configures the REST side.

        Credentials, proxy and environment are shared: `transport.flag == '1'`
        (demo trading) selects the demo host, and `channel` selects the public
        or business endpoint. `debug` falls back to the transport's value
        unless given explicitly.

        Only `transport.proxy` is inherited. `Transport(http=...)` turning off
        environment-proxy detection is a REST rule and does not extend here:
        with no proxy set, the WebSocket still follows the environment.
        """
        if not isinstance(transport, Transport):
            raise TypeError(
                "transport must be an okx.transport.Transport instance, "
                f"got {type(transport).__name__}"
            )
        if channel not in ('public', 'business'):
            raise ValueError(f"channel must be 'public' or 'business', got {channel!r}")
        demo = str(transport.flag) == '1'
        if url is None:
            if channel == 'business':
                url = consts.WS_BUSINESS_DEMO_URL if demo else consts.WS_BUSINESS_URL
            else:
                url = consts.WS_PUBLIC_DEMO_URL if demo else consts.WS_PUBLIC_URL
        return cls(
            url=url,
            apiKey=transport.API_KEY,
            passphrase=transport.PASSPHRASE,
            secretKey=transport.API_SECRET_KEY,
            debug=transport.debug if debug is None else debug,
            proxy=transport.proxy,
        )

    def __init__(
        self,
        url: str = consts.WS_PUBLIC_URL,
        apiKey: str = '',
        passphrase: str = '',
        secretKey: str = '',
        debug: bool = False,
        **options: Any,
    ) -> None:
        super().__init__(
            url=url,
            apiKey=apiKey,
            passphrase=passphrase,
            secretKey=secretKey,
            debug=debug,
            **options,
        )

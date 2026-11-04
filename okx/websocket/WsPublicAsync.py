"""Public and business WebSocket client."""

from __future__ import annotations

from typing import Any, Optional

from okx import consts
from okx.websocket.WsBaseAsync import WsBaseAsync


class WsPublicAsync(WsBaseAsync):
    @classmethod
    def from_client(
        cls,
        client: Any,
        channel: str = 'public',
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPublicAsync":
        """Build from an existing REST client, matching its credentials and environment.

        `channel` selects the public or business endpoint; `client.flag == '1'`
        (demo trading) selects the demo host.
        """
        if channel not in ('public', 'business'):
            raise ValueError(f"channel must be 'public' or 'business', got {channel!r}")
        demo = str(client.flag) == '1'
        if url is None:
            if channel == 'business':
                url = consts.WS_BUSINESS_DEMO_URL if demo else consts.WS_BUSINESS_URL
            else:
                url = consts.WS_PUBLIC_DEMO_URL if demo else consts.WS_PUBLIC_URL
        return cls(
            url=url,
            apiKey=client.API_KEY,
            passphrase=client.PASSPHRASE,
            secretKey=client.API_SECRET_KEY,
            debug=client.debug if debug is None else debug,
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

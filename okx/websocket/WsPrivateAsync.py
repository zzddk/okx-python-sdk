"""Private WebSocket client: account channels and order entry."""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional

from okx import consts
from okx.websocket.WsBaseAsync import Callback, WsBaseAsync


class WsPrivateAsync(WsBaseAsync):
    _LOGIN_REQUIRED = True

    @classmethod
    def from_client(
        cls,
        client: Any,
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPrivateAsync":
        """Build from an existing REST client, matching its credentials and environment.

        `flag='1'` on the REST client means demo trading, so the demo host is
        used automatically — the two layers cannot end up in different
        environments by accident.
        """
        if url is None:
            url = consts.WS_PRIVATE_DEMO_URL if str(client.flag) == '1' else consts.WS_PRIVATE_URL
        return cls(
            apiKey=client.API_KEY,
            passphrase=client.PASSPHRASE,
            secretKey=client.API_SECRET_KEY,
            url=url,
            debug=client.debug if debug is None else debug,
        )

    def __init__(
        self,
        apiKey: str,
        passphrase: str,
        secretKey: str,
        url: str = consts.WS_PRIVATE_URL,
        useServerTime: Optional[bool] = None,
        debug: bool = False,
        **options: Any,
    ) -> None:
        if useServerTime is not None:
            warnings.warn("useServerTime parameter is deprecated. Please remove it.", DeprecationWarning)
        super().__init__(
            url=url,
            apiKey=apiKey,
            passphrase=passphrase,
            secretKey=secretKey,
            debug=debug,
            **options,
        )
        # Kept for the deprecated argument's test surface until it is removed
        # with the rest of the 0.9.0 breaking batch.
        self.useServerTime = False

    async def place_order(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Place an order."""
        await self.send("order", args, callback, id)

    async def batch_orders(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Place up to 20 orders in one request."""
        await self.send("batch-orders", args, callback, id)

    async def cancel_order(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Cancel an order."""
        await self.send("cancel-order", args, callback, id)

    async def batch_cancel_orders(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Cancel up to 20 orders in one request."""
        await self.send("batch-cancel-orders", args, callback, id)

    async def amend_order(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Amend an order."""
        await self.send("amend-order", args, callback, id)

    async def batch_amend_orders(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Amend up to 20 orders in one request."""
        await self.send("batch-amend-orders", args, callback, id)

    async def mass_cancel(
        self,
        args: List[Dict[str, Any]],
        callback: Optional[Callback] = None,
        id: Optional[str] = None,
    ) -> None:
        """Mass cancel orders on the business channel (1 request/second)."""
        await self.send("mass-cancel", args, callback, id)

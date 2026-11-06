"""Private WebSocket client: account channels and order entry."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional

from okxsdk import consts
from okxsdk.transport import Transport
from okxsdk.websocket.config import session_config
from okxsdk.websocket.WsBaseAsync import Callback, WsBaseAsync


class WsPrivateAsync(WsBaseAsync):
    _LOGIN_REQUIRED = True

    # "is demo trading" -> endpoint; the mapping itself lives in
    # okxsdk.websocket.config.session_config. The live entry is also the default
    # url when the client is built without a transport.
    _HOSTS: ClassVar[dict[bool, str]] = {
        False: consts.WS_PRIVATE_URL,
        True: consts.WS_PRIVATE_DEMO_URL,
    }

    @classmethod
    def from_transport(
        cls,
        transport: Transport,
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPrivateAsync":
        """Build from the `Transport` that configures the REST side.

        Credentials, environment and proxy come from it; the field mapping and
        the demo switch live in `okxsdk.websocket.config.session_config`. `url`
        overrides the host.
        """
        return cls(**session_config(transport, cls._HOSTS, url=url, debug=debug))

    def __init__(
        self,
        apiKey: str,
        passphrase: str,
        secretKey: str,
        url: Optional[str] = None,
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

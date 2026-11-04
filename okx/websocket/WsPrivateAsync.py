"""Private WebSocket client: account channels and order entry."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from okx import consts
from okx.transport import Transport
from okx.websocket.WsBaseAsync import Callback, WsBaseAsync


class WsPrivateAsync(WsBaseAsync):
    _LOGIN_REQUIRED = True

    @classmethod
    def from_transport(
        cls,
        transport: Transport,
        url: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "WsPrivateAsync":
        """Build from the `Transport` that configures the REST side.

        Credentials, environment and proxy are shared: `flag='1'` on the
        transport means demo trading, so the demo host and `transport.proxy`
        are picked up automatically. `debug` falls back to the transport's
        value unless given explicitly.

        Only `transport.proxy` is inherited. `Transport(http=...)` turning off
        environment-proxy detection is a REST rule and does not extend here:
        with no proxy set, the WebSocket still follows the environment.
        """
        if not isinstance(transport, Transport):
            raise TypeError(
                "transport must be an okx.transport.Transport instance, "
                f"got {type(transport).__name__}"
            )
        if url is None:
            url = consts.WS_PRIVATE_DEMO_URL if str(transport.flag) == '1' else consts.WS_PRIVATE_URL
        return cls(
            apiKey=transport.API_KEY,
            passphrase=transport.PASSPHRASE,
            secretKey=transport.API_SECRET_KEY,
            url=url,
            debug=transport.debug if debug is None else debug,
            proxy=transport.proxy,
        )

    def __init__(
        self,
        apiKey: str,
        passphrase: str,
        secretKey: str,
        url: str = consts.WS_PRIVATE_URL,
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

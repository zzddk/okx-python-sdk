"""WebSocket endpoints.

Live and demo hosts differ; the demo host also needs `brokerId=9999`. Pass your
own `url` if OKX moves the host before this file is updated. OKX retired the
explicit `:8443` port on 2026-10-31 (Colo 2026-11-16); `wss://` defaults to 443,
so these carry no port. See ADR-0025.
"""

# Live trading
WS_PUBLIC_URL = 'wss://ws.okx.com/ws/v5/public'
WS_PRIVATE_URL = 'wss://ws.okx.com/ws/v5/private'
WS_BUSINESS_URL = 'wss://ws.okx.com/ws/v5/business'

# Demo trading (what `flag='1'` means on the REST side)
WS_PUBLIC_DEMO_URL = 'wss://wspap.okx.com/ws/v5/public?brokerId=9999'
WS_PRIVATE_DEMO_URL = 'wss://wspap.okx.com/ws/v5/private?brokerId=9999'
WS_BUSINESS_DEMO_URL = 'wss://wspap.okx.com/ws/v5/business?brokerId=9999'

"""WebSocket endpoints.

Live and demo hosts differ; the demo host also needs `brokerId=9999`. Pass your
own `url` if OKX moves the host before this file is updated.
"""

# Live trading
WS_PUBLIC_URL = 'wss://ws.okxsdk.com:8443/ws/v5/public'
WS_PRIVATE_URL = 'wss://ws.okxsdk.com:8443/ws/v5/private'
WS_BUSINESS_URL = 'wss://ws.okxsdk.com:8443/ws/v5/business'

# Demo trading (what `flag='1'` means on the REST side)
WS_PUBLIC_DEMO_URL = 'wss://wspap.okxsdk.com:8443/ws/v5/public?brokerId=9999'
WS_PRIVATE_DEMO_URL = 'wss://wspap.okxsdk.com:8443/ws/v5/private?brokerId=9999'
WS_BUSINESS_DEMO_URL = 'wss://wspap.okxsdk.com:8443/ws/v5/business?brokerId=9999'

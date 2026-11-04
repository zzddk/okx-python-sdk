"""Per-endpoint rate limits, keyed by the request path.

Values are `(requests, window_seconds)`, matching how OKX documents its
limits. The table covers the endpoints whose published limits are stable;
**paths missing from it are not throttled**. Add entries as they are confirmed
against the OKX documentation for the account tier you target — higher VIP
levels get larger limits, so treat these numbers as a floor.

The client only consults this table when constructed with `rate_limit=True`.
"""

RATE_LIMITS = {
    # Account
    '/api/v5/account/balance': (10, 2),
    '/api/v5/account/positions': (10, 2),
    # Trade
    '/api/v5/trade/order': (60, 2),
    '/api/v5/trade/cancel-order': (60, 2),
    '/api/v5/trade/amend-order': (60, 2),
    # Market data
    '/api/v5/market/ticker': (20, 2),
    '/api/v5/market/tickers': (20, 2),
    '/api/v5/market/books': (40, 2),
}

"""Per-endpoint rate limits, keyed by the request path.

Values are `(requests, window_seconds)`, matching how OKX documents its
limits. Every path declared in `okxsdk.consts` is either in this table or in
`RATE_LIMIT_EXEMPTIONS`; a path in neither is not throttled, and the test suite
fails until it is classified.

Numbers come from each endpoint's `Rate Limit:` line in the official
documentation. Snapshot: 2026-11-06 - update this date whenever an entry is
re-checked against the official Change Log.

`RATE_LIMIT_EXEMPTIONS` records why a declared path is not throttled:
`ORDERS_BASED` for the four batch endpoints whose published limit is in
**orders** per window, and `NOT_IN_OFFICIAL_LIST` for the 8 paths absent from
the official endpoint list.

The client only consults these maps when constructed with `rate_limit=True`.
"""

RATE_LIMITS = {
    # account
    '/api/v5/account/account-position-risk': (10, 2),
    '/api/v5/account/activate-option': (5, 2),
    '/api/v5/account/balance': (10, 2),
    '/api/v5/account/bills': (5, 1),
    '/api/v5/account/bills-archive': (5, 2),
    '/api/v5/account/bills-history-archive': (12, 86400),
    '/api/v5/account/config': (5, 2),
    '/api/v5/account/greeks': (10, 2),
    '/api/v5/account/instruments': (20, 2),
    '/api/v5/account/interest-accrued': (5, 2),
    '/api/v5/account/interest-limits': (5, 2),
    '/api/v5/account/interest-rate': (5, 2),
    '/api/v5/account/leverage-info': (20, 2),
    '/api/v5/account/max-avail-size': (20, 2),
    '/api/v5/account/max-loan': (20, 2),
    '/api/v5/account/max-size': (20, 2),
    '/api/v5/account/max-withdrawal': (20, 2),
    '/api/v5/account/position-builder': (2, 2),
    '/api/v5/account/position-tiers': (10, 2),
    '/api/v5/account/position/margin-balance': (20, 2),
    '/api/v5/account/positions': (10, 2),
    '/api/v5/account/positions-history': (10, 2),
    '/api/v5/account/precheck-set-delta-neutral': (1, 2),
    '/api/v5/account/risk-state': (10, 2),
    '/api/v5/account/set-account-level': (5, 2),
    '/api/v5/account/set-auto-earn': (2, 2),
    '/api/v5/account/set-auto-loan': (5, 2),
    '/api/v5/account/set-auto-repay': (5, 2),
    '/api/v5/account/set-greeks': (5, 2),
    '/api/v5/account/set-isolated-mode': (5, 2),
    '/api/v5/account/set-leverage': (20, 2),
    '/api/v5/account/set-position-mode': (5, 2),
    '/api/v5/account/set-riskOffset-amt': (10, 2),
    '/api/v5/account/set-trading-config': (1, 2),
    '/api/v5/account/spot-borrow-repay-history': (5, 2),
    '/api/v5/account/spot-manual-borrow-repay': (1, 3),
    '/api/v5/account/subaccount/balances': (6, 2),
    '/api/v5/account/subtypes': (20, 2),
    '/api/v5/account/trade-fee': (5, 2),

    # affiliate
    '/api/v5/affiliate/invitee/detail': (3, 1),
    '/api/v5/affiliate/invitee/list': (3, 1),
    '/api/v5/affiliate/link/list': (3, 1),
    '/api/v5/affiliate/performance/summary': (3, 1),

    # asset
    '/api/v5/asset/asset-valuation': (1, 1),
    '/api/v5/asset/balances': (6, 1),
    '/api/v5/asset/bills': (6, 1),
    '/api/v5/asset/cancel-withdrawal': (6, 1),
    '/api/v5/asset/convert/currencies': (6, 1),
    '/api/v5/asset/convert/currency-pair': (6, 1),
    '/api/v5/asset/convert/estimate-quote': (10, 1),
    '/api/v5/asset/convert/history': (6, 1),
    '/api/v5/asset/convert/trade': (10, 1),
    '/api/v5/asset/currencies': (6, 1),
    '/api/v5/asset/deposit-address': (6, 1),
    '/api/v5/asset/deposit-history': (6, 1),
    '/api/v5/asset/deposit-withdraw-status': (1, 2),
    '/api/v5/asset/non-tradable-assets': (6, 1),
    '/api/v5/asset/subaccount/balances': (6, 2),
    '/api/v5/asset/subaccount/bills': (6, 1),
    '/api/v5/asset/subaccount/transfer': (1, 1),
    '/api/v5/asset/transfer': (2, 1),
    '/api/v5/asset/transfer-state': (10, 1),
    '/api/v5/asset/withdrawal': (6, 1),
    '/api/v5/asset/withdrawal-history': (6, 1),

    # copytrading
    '/api/v5/copytrading/algo-order': (20, 2),
    '/api/v5/copytrading/close-subposition': (20, 2),
    '/api/v5/copytrading/current-subpositions': (20, 2),
    '/api/v5/copytrading/instruments': (5, 2),
    '/api/v5/copytrading/profit-sharing-details': (5, 2),
    '/api/v5/copytrading/set-instruments': (5, 2),
    '/api/v5/copytrading/subpositions-history': (20, 2),
    '/api/v5/copytrading/total-profit-sharing': (5, 2),
    '/api/v5/copytrading/unrealized-profit-sharing-details': (5, 2),

    # finance
    '/api/v5/finance/flexible-loan/adjust-collateral': (5, 2),
    '/api/v5/finance/flexible-loan/borrow': (2, 2),
    '/api/v5/finance/flexible-loan/borrow-currencies': (5, 2),
    '/api/v5/finance/flexible-loan/collateral-assets': (5, 2),
    '/api/v5/finance/flexible-loan/emode-info': (5, 2),
    '/api/v5/finance/flexible-loan/interest-accrued': (5, 2),
    '/api/v5/finance/flexible-loan/loan-history': (5, 2),
    '/api/v5/finance/flexible-loan/loan-info': (5, 2),
    '/api/v5/finance/flexible-loan/max-collateral-redeem-amount': (5, 2),
    '/api/v5/finance/flexible-loan/max-loan': (5, 2),
    '/api/v5/finance/flexible-loan/repay': (2, 2),
    '/api/v5/finance/okusd/account': (2, 2),
    '/api/v5/finance/okusd/rate/history': (5, 2),
    '/api/v5/finance/okusd/redeem/history': (5, 2),
    '/api/v5/finance/okusd/rewards/history': (5, 2),
    '/api/v5/finance/okusd/subscribe/history': (5, 2),
    '/api/v5/finance/savings/balance': (6, 1),
    '/api/v5/finance/savings/lending-history': (6, 1),
    '/api/v5/finance/savings/lending-rate-history': (6, 1),
    '/api/v5/finance/savings/lending-rate-summary': (6, 1),
    '/api/v5/finance/savings/purchase-redempt': (6, 1),
    '/api/v5/finance/sfp/dcd/currency-pair': (1, 1),
    '/api/v5/finance/sfp/dcd/order-history': (1, 1),
    '/api/v5/finance/sfp/dcd/order-status': (3, 1),
    '/api/v5/finance/sfp/dcd/products': (1, 1),
    '/api/v5/finance/sfp/dcd/quote': (10, 60),
    '/api/v5/finance/sfp/dcd/redeem': (2, 60),
    '/api/v5/finance/sfp/dcd/redeem-quote': (10, 60),
    '/api/v5/finance/sfp/dcd/trade': (2, 60),
    '/api/v5/finance/staking-defi/cancel': (2, 1),
    '/api/v5/finance/staking-defi/eth/apy-history': (6, 1),
    '/api/v5/finance/staking-defi/eth/balance': (6, 1),
    '/api/v5/finance/staking-defi/eth/cancel-redeem': (2, 1),
    '/api/v5/finance/staking-defi/eth/product-info': (3, 1),
    '/api/v5/finance/staking-defi/eth/purchase': (2, 1),
    '/api/v5/finance/staking-defi/eth/purchase-redeem-history': (6, 1),
    '/api/v5/finance/staking-defi/eth/redeem': (2, 1),
    '/api/v5/finance/staking-defi/offers': (3, 1),
    '/api/v5/finance/staking-defi/orders-active': (3, 1),
    '/api/v5/finance/staking-defi/orders-history': (3, 1),
    '/api/v5/finance/staking-defi/purchase': (2, 1),
    '/api/v5/finance/staking-defi/redeem': (2, 1),
    '/api/v5/finance/staking-defi/sol/apy-history': (6, 1),
    '/api/v5/finance/staking-defi/sol/balance': (6, 1),
    '/api/v5/finance/staking-defi/sol/product-info': (3, 1),
    '/api/v5/finance/staking-defi/sol/purchase': (2, 1),
    '/api/v5/finance/staking-defi/sol/purchase-redeem-history': (6, 1),
    '/api/v5/finance/staking-defi/sol/redeem': (2, 1),

    # market
    '/api/v5/market/block-ticker': (20, 2),
    '/api/v5/market/block-tickers': (20, 2),
    '/api/v5/market/books': (40, 2),
    '/api/v5/market/books-rpi': (20, 2),
    '/api/v5/market/candles': (40, 2),
    '/api/v5/market/exchange-rate': (1, 2),
    '/api/v5/market/history-candles': (20, 2),
    '/api/v5/market/history-trades': (20, 2),
    '/api/v5/market/index-candles': (20, 2),
    '/api/v5/market/index-components': (20, 2),
    '/api/v5/market/index-tickers': (20, 2),
    '/api/v5/market/mark-price-candles': (20, 2),
    '/api/v5/market/option/instrument-family-trades': (20, 2),
    '/api/v5/market/platform-24-volume': (2, 2),
    '/api/v5/market/sprd-ticker': (20, 2),
    '/api/v5/market/ticker': (20, 2),
    '/api/v5/market/tickers': (20, 2),
    '/api/v5/market/trades': (100, 2),

    # public
    '/api/v5/public/block-trades': (20, 2),
    '/api/v5/public/convert-contract-coin': (10, 2),
    '/api/v5/public/delivery-exercise-history': (40, 2),
    '/api/v5/public/discount-rate-interest-free-quota': (2, 2),
    '/api/v5/public/estimated-price': (10, 2),
    '/api/v5/public/funding-rate': (10, 2),
    '/api/v5/public/funding-rate-history': (10, 2),
    '/api/v5/public/instrument-tick-bands': (5, 2),
    '/api/v5/public/instruments': (20, 2),
    '/api/v5/public/insurance-fund': (10, 2),
    '/api/v5/public/interest-rate-loan-quota': (2, 2),
    '/api/v5/public/mark-price': (10, 2),
    '/api/v5/public/market-data-history': (5, 2),
    '/api/v5/public/open-interest': (20, 2),
    '/api/v5/public/opt-summary': (20, 2),
    '/api/v5/public/option-trades': (20, 2),
    '/api/v5/public/position-tiers': (10, 2),
    '/api/v5/public/price-limit': (20, 2),
    '/api/v5/public/time': (10, 2),
    '/api/v5/public/underlying': (20, 2),

    # rfq
    '/api/v5/rfq/cancel-all-quotes': (2, 2),
    '/api/v5/rfq/cancel-all-rfqs': (2, 2),
    '/api/v5/rfq/cancel-batch-quotes': (2, 2),
    '/api/v5/rfq/cancel-batch-rfqs': (2, 2),
    '/api/v5/rfq/cancel-quote': (50, 2),
    '/api/v5/rfq/cancel-rfq': (5, 2),
    '/api/v5/rfq/counterparties': (5, 2),
    '/api/v5/rfq/create-quote': (50, 2),
    '/api/v5/rfq/create-rfq': (5, 2),
    '/api/v5/rfq/execute-quote': (2, 3),
    '/api/v5/rfq/maker-instrument-settings': (5, 2),
    '/api/v5/rfq/mmp-reset': (5, 2),
    '/api/v5/rfq/public-trades': (5, 2),
    '/api/v5/rfq/quotes': (2, 2),
    '/api/v5/rfq/rfqs': (2, 2),
    '/api/v5/rfq/trades': (5, 2),

    # rubik
    '/api/v5/rubik/stat/contracts/long-short-account-ratio': (5, 2),
    '/api/v5/rubik/stat/contracts/open-interest-history': (10, 2),
    '/api/v5/rubik/stat/contracts/open-interest-volume': (5, 2),
    '/api/v5/rubik/stat/margin/loan-ratio': (5, 2),
    '/api/v5/rubik/stat/option/open-interest-volume': (5, 2),
    '/api/v5/rubik/stat/option/open-interest-volume-expiry': (5, 2),
    '/api/v5/rubik/stat/option/open-interest-volume-ratio': (5, 2),
    '/api/v5/rubik/stat/option/open-interest-volume-strike': (5, 2),
    '/api/v5/rubik/stat/option/taker-block-volume': (5, 2),
    '/api/v5/rubik/stat/taker-volume': (5, 2),
    '/api/v5/rubik/stat/trading-data/support-coin': (5, 2),

    # sprd
    '/api/v5/sprd/books': (20, 2),
    '/api/v5/sprd/cancel-order': (20, 2),
    '/api/v5/sprd/mass-cancel': (10, 2),
    '/api/v5/sprd/order': (20, 2),
    '/api/v5/sprd/orders-history': (20, 2),
    '/api/v5/sprd/orders-pending': (10, 2),
    '/api/v5/sprd/public-trades': (20, 2),
    '/api/v5/sprd/spreads': (20, 2),
    '/api/v5/sprd/trades': (20, 2),

    # support
    '/api/v5/support/announcements': (5, 2),

    # system
    '/api/v5/system/status': (1, 5),

    # trade
    '/api/v5/trade/amend-algos': (20, 2),
    '/api/v5/trade/amend-order': (60, 2),
    '/api/v5/trade/cancel-order': (60, 2),
    '/api/v5/trade/close-position': (20, 2),
    '/api/v5/trade/easy-convert': (1, 2),
    '/api/v5/trade/easy-convert-currency-list': (1, 2),
    '/api/v5/trade/easy-convert-history': (1, 2),
    '/api/v5/trade/fills': (60, 2),
    '/api/v5/trade/fills-history': (10, 2),
    '/api/v5/trade/one-click-repay': (1, 2),
    '/api/v5/trade/one-click-repay-currency-list': (1, 2),
    '/api/v5/trade/one-click-repay-currency-list-v2': (1, 2),
    '/api/v5/trade/one-click-repay-history': (1, 2),
    '/api/v5/trade/one-click-repay-history-v2': (1, 2),
    '/api/v5/trade/one-click-repay-v2': (1, 2),
    '/api/v5/trade/order': (60, 2),
    '/api/v5/trade/order-algo': (20, 2),
    '/api/v5/trade/orders-algo-history': (20, 2),
    '/api/v5/trade/orders-algo-pending': (20, 2),
    '/api/v5/trade/orders-history': (40, 2),
    '/api/v5/trade/orders-history-archive': (20, 2),
    '/api/v5/trade/orders-pending': (60, 2),

    # tradingBot
    '/api/v5/tradingBot/grid/ai-param': (20, 2),
    '/api/v5/tradingBot/grid/amend-order-algo': (20, 2),
    '/api/v5/tradingBot/grid/compute-margin-balance': (20, 2),
    '/api/v5/tradingBot/grid/margin-balance': (20, 2),
    '/api/v5/tradingBot/grid/order-algo': (20, 2),
    '/api/v5/tradingBot/grid/orders-algo-details': (20, 2),
    '/api/v5/tradingBot/grid/orders-algo-history': (20, 2),
    '/api/v5/tradingBot/grid/orders-algo-pending': (20, 2),
    '/api/v5/tradingBot/grid/positions': (20, 2),
    '/api/v5/tradingBot/grid/stop-order-algo': (20, 2),
    '/api/v5/tradingBot/grid/sub-orders': (20, 2),
    '/api/v5/tradingBot/grid/withdraw-income': (20, 2),
    '/api/v5/tradingBot/recurring/amend-order-algo': (20, 2),
    '/api/v5/tradingBot/recurring/order-algo': (20, 2),
    '/api/v5/tradingBot/recurring/orders-algo-details': (20, 2),
    '/api/v5/tradingBot/recurring/orders-algo-history': (20, 2),
    '/api/v5/tradingBot/recurring/orders-algo-pending': (20, 2),
    '/api/v5/tradingBot/recurring/stop-order-algo': (20, 2),
    '/api/v5/tradingBot/recurring/sub-orders': (20, 2),

    # users
    '/api/v5/users/entrust-subaccount-list': (1, 1),
    '/api/v5/users/glp/historicalperformance': (5, 2),
    '/api/v5/users/glp/todayperformance': (5, 2),
    '/api/v5/users/subaccount/list': (20, 2),
    '/api/v5/users/subaccount/modify-apikey': (1, 1),
    '/api/v5/users/subaccount/set-transfer-out': (1, 1),
}

# Why a declared path is not throttled. The test suite accepts only these
# values, so a new exemption needs a decision rather than a free-form note.
ORDERS_BASED = 'orders-based'
NOT_IN_OFFICIAL_LIST = 'not-in-official-list'
RATE_LIMIT_EXEMPTION_REASONS = frozenset({ORDERS_BASED, NOT_IN_OFFICIAL_LIST})

RATE_LIMIT_EXEMPTIONS = {
    # Published in orders per window, which a request-counting limiter cannot
    # express.
    '/api/v5/trade/amend-batch-orders': ORDERS_BASED,
    '/api/v5/trade/batch-orders': ORDERS_BASED,
    '/api/v5/trade/cancel-algos': ORDERS_BASED,
    '/api/v5/trade/cancel-batch-orders': ORDERS_BASED,

    # Absent from the official endpoint list (snapshot above), so there is no
    # published value to enforce.
    '/api/v5/account/simulated_margin': NOT_IN_OFFICIAL_LIST,
    '/api/v5/account/subaccount/interest-limits': NOT_IN_OFFICIAL_LIST,
    '/api/v5/account/subaccount/set-loan-allocation': NOT_IN_OFFICIAL_LIST,
    '/api/v5/affiliate/tvb/tier-breakdown': NOT_IN_OFFICIAL_LIST,
    '/api/v5/asset/deposit-lightning': NOT_IN_OFFICIAL_LIST,
    '/api/v5/asset/withdrawal-lightning': NOT_IN_OFFICIAL_LIST,
    '/api/v5/broker/fd/rebate-per-orders': NOT_IN_OFFICIAL_LIST,
    '/api/v5/finance/savings/set-lending-rate': NOT_IN_OFFICIAL_LIST,
}

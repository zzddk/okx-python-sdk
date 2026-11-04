# Changelog

All notable changes to `python-okx` are documented in this file.

## [0.5.0]

Breaking release. This is the only window in the 0.4/0.5 line for public-API changes, so nothing renamed here keeps a compatibility alias (see ADR-0001). The "Renamed" table below is the complete migration list.

### Changed
- Failed requests raise `OkxAPIException` by default when the HTTP status is `>= 400` or the response `code` is not `'0'`. The exception exposes `code`, `message`, `status_code` and the original `response`; network failures still surface as the underlying `httpx` exception. Pass `raise_on_error=False` to return the payload dict exactly as 0.4.x did.
- All 22 `*API` classes now inherit `OkxClient.__init__`; the duplicated subclass constructors are gone. Adding a client-wide option no longer means editing 22 files.
- The base constructor's `domain` parameter is now `base_api`, matching `OkxClient`. `domain=` keyword calls must switch to `base_api=`.
- `use_server_time` is removed from every constructor; the fourth positional argument is now `flag`. The parameter had been a silent no-op since 0.4.x, so sync the system clock (for example with NTP) if timestamp drift matters.
- The REST layer logs through the standard `logging` module (`okx.okxclient`, `okx.utils`), matching the WebSocket layer. Application handlers receive SDK records; a `NullHandler` on the `okx` logger keeps unconfigured apps quiet.
- `okx.websocket.WsUtils.getServerTime` uses the already-required `httpx` instead of `requests`.
- Empty-value semantics are unified: `None` is the only "not supplied" marker, and an explicit `''` is sent as a real parameter. Every optional REST argument now defaults to `None` instead of `''`. GET query values that are lists or dicts are JSON-encoded; POST bodies drop top-level `None` values. `TradeAPI.place_algo_order(attachAlgoOrds=...)` no longer defaults to a shared mutable empty list.
- `okx.consts` is now a package (`okx/consts/http.py` plus one module per product under `okx/consts/endpoints/`). `from okx import consts`, `consts.ACCOUNT_INFO` and `from okx.consts import *` are unchanged. A constant name declared in two modules now raises `ImportError` at import time instead of silently shadowing.

### Renamed

No aliases are kept; update call sites using this table.

| Old | New |
| --- | --- |
| `AccountAPI.get_instruments(ugly=...)` | `AccountAPI.get_instruments(uly=...)` (the OKX parameter is `uly`) |
| `AccountAPI.set_risk_offset_typel` | `AccountAPI.set_risk_offset_type` |
| `AccountAPI.get_VIP_interest_accrued_data` | `AccountAPI.get_vip_interest_accrued_data` |
| `AccountAPI.get_VIP_interest_deducted_data` | `AccountAPI.get_vip_interest_deducted_data` |
| `AccountAPI.get_VIP_loan_order_list` | `AccountAPI.get_vip_loan_order_list` |
| `AccountAPI.get_VIP_loan_order_detail` | `AccountAPI.get_vip_loan_order_detail` |
| `PublicDataAPI.get_option_tickBands` | `PublicDataAPI.get_option_tickbands` |
| `SubAccountAPI.subAccount_transfer` | `SubAccountAPI.subaccount_transfer` |
| `SubAccountAPI.set_sub_accounts_VIP_loan` | `SubAccountAPI.set_sub_accounts_vip_loan` |
| `consts.ACEEPT` | `consts.ACCEPT` |
| `consts.ACTIVSTE_OPTION` | `consts.ACTIVATE_OPTION` |
| `consts.INDEX_CANSLES` | `consts.INDEX_CANDLES` |
| `consts.VOLUMNE` | `consts.VOLUME` |
| `consts.PLACR_ORDER` | `consts.PLACE_ORDER` |
| `consts.BILLs` | `consts.SUBACCOUNT_BILLS` |
| `consts.SET_TRSNSFER_OUT` | `consts.SET_TRANSFER_OUT` |
| `consts.DICCOUNT_INTETEST_INFO` | `consts.DISCOUNT_INTEREST_INFO` |
| `consts.GET_DEPOSIT_WITHDrAW_STATUS` | `consts.GET_DEPOSIT_WITHDRAW_STATUS` |
| `consts.GRID_COMPUTE_MARIGIN_BALANCE` | `consts.GRID_COMPUTE_MARGIN_BALANCE` |
| `consts.CANCEL_ALL_RSQS` | `consts.CANCEL_ALL_RFQS` |
| `consts.MARKER_INSTRUMENT_SETTING` | `consts.MAKER_INSTRUMENT_SETTING` |

### Added
- Type annotations on every public REST method (parameters and `-> Dict[str, Any]`), plus `okx/py.typed` shipped with the package. Type checkers and IDEs now treat the SDK as typed.
- `client=` on every REST API class. Pass an existing `OkxClient` to route requests through its connection pool and reuse its credentials.

### Removed
- `loguru` and `requests` are no longer runtime dependencies; `requirements.txt` lists only `httpx[http2]`, `websockets` and `certifi`.
- `consts.SERVER_TIMESTAMP_URL` (duplicate of `consts.SYSTEM_TIME`, only used by the removed server-time path).

## [0.4.5]

Defect-fix release. No endpoint, constructor signature or happy-path return value changes. Breaking changes from the same review are deferred to 0.5.0.

### Fixed
- `okx/consts.py`: `GET_OPTION_TRADES` was defined twice, so the market definition (`/api/v5/market/option/instrument-family-trades`) was silently shadowed by the public one. The market constant is now `MARKET_OPTION_TRADES`; both `MarketData.get_option_trades` and `PublicData.get_option_trades` reach their intended endpoint.
- `use_server_time=True` now emits a visible `UserWarning` stating that it has no effect. Previously it raised a `DeprecationWarning`, which Python hides by default, so `True` was effectively a silent no-op.
- Replaced 12 mutable default arguments (`x=[]`) with `None` and a per-call list.
- GET query strings are now built with `urllib.parse.urlencode`: booleans serialize as `true`/`false`, and values containing spaces or `&` no longer truncate the query string.

### Added
- Contract test layer (`test/unit/okx/test_contract.py`): every `*API` method's `(HTTP method, path)` must resolve to a declared constant, constant names must be unique, and every declared endpoint must be reachable.
- Unit tests for query-string encoding.

### Deprecated
- `use_server_time` will be removed from `OkxClient` and every `*API` subclass in 0.5.0.

### Deferred to 0.5.0
- Raising `OkxAPIException` by default when the HTTP status is `>= 400` or the response body has a non-`'0'` `code`, with `raise_on_error=False` as the opt-out.
- Removal of the `use_server_time` constructor argument.

## [0.4.4]

REST parity catch-up with the OKX v5 docs added between 2026-07-06 and 2026-08-26: 16 new endpoint bindings across market data, GLP performance, Flexible Loan, OKUSD, and Affiliate TVB. All changes are additive / opt-in and backward compatible — existing public signatures and happy-path behaviour are unchanged. New endpoints/modules are net-new symbols; new optional kwargs default to "unset" (omitted from the request).

### Added
- `okx/MarketData.py` `get_rpi_orderbook(instId, sz='')`: new method for `GET /api/v5/market/books-rpi` (RPI-consolidated order book). Mirrors `get_orderbook`.
- `okx/Account.py` `get_glp_historical_performance(program, begin='', end='', limit='')` and `get_glp_today_performance()`: new methods for `GET /api/v5/users/glp/historicalperformance` and `GET /api/v5/users/glp/todayperformance` (GLP market-maker performance reporting).
- `okx/Finance/FlexibleLoan.py` `borrow(loanData, clOrdId, ordId='', collateralData=None, eMode='')`, `repay(ordId, ccy, amt, clOrdId)`, and `emode_info()`: new methods for `POST /api/v5/finance/flexible-loan/borrow`, `POST /api/v5/finance/flexible-loan/repay`, and `GET /api/v5/finance/flexible-loan/emode-info`.
- `okx/Finance/Okusd.py` (new module) `OkusdAPI`: 5 methods for the OKUSD stablecoin product — `get_account`, `get_rate_history`, `get_subscribe_history`, `get_redeem_history`, `get_rewards_history` (`GET /api/v5/finance/okusd/{account,rate/history,subscribe/history,redeem/history,rewards/history}`). Registered in `okx/Finance/__init__.py`.
- `okx/Affiliate.py` (new module) `AffiliateAPI`: 5 methods for the Affiliate Trading Volume Bonus (TVB) program — `get_tvb_invitee_detail`, `get_tvb_invitee_list`, `get_tvb_link_list`, `get_tvb_performance_summary`, `get_tvb_tier_breakdown` (`GET /api/v5/affiliate/tvb/{invitee/detail,invitee/list,link/list,performance/summary,tier-breakdown}`). Methods carry the `tvb_` prefix to avoid collisions with the non-TVB affiliate endpoints planned for a later release.
- `okx/consts.py`: 16 new path constants for all endpoints above.

## [0.4.3]

Packaging hygiene plus one additive ETH Staking endpoint. All changes are backward compatible — existing public signatures and happy-path behaviour are unchanged.

### Fixed
- Packaging split: dev/release-only tooling no longer leaks into end-user installs. `requirements.txt` now lists only the 5 runtime dependencies (`httpx[http2]`, `requests`, `websockets`, `certifi`, `loguru`), so `setup.py`'s `parse_requirements()` yields a runtime-only `install_requires`. The dev/test/release packages (`python-dotenv`, `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `build`, `twine`) moved to a new `dev_requirements.txt` (starts with `-r requirements.txt`). `setup.py` is unchanged. Contributors should now run `pip install -r dev_requirements.txt`. Consumers who relied on `python-okx` transitively installing `pytest`/`python-dotenv` etc. must install those themselves.

### Added
- `okx/Finance/EthStaking.py` `eth_cancel_redeem(ordId='')`: new method for `POST /api/v5/finance/staking-defi/eth/cancel-redeem`, bringing the ETH Staking module to full 7/7 endpoint coverage. Mirrors `eth_purchase` / `eth_redeem`.
- `okx/consts.py`: new `STACK_ETH_CANCEL_REDEEM` path constant.

## [0.4.2]

Community issue batch (GH#141 / GH#116 / GH#115) plus the v5 API sync batch. All changes are additive / opt-in and backward compatible — existing public signatures and happy-path behaviour are unchanged. New optional kwargs default to "unset" (omitted from the request); new endpoints/modules are net-new symbols.

### Added
- `okx/Account.py` `get_account_bills`: added optional `begin=''` / `end=''` time-window parameters, mirroring `get_account_bills_archive`. Empty defaults produce the exact same request as before (GH#141).
- `okx/websocket/WsPublicAsync.py` and `okx/websocket/WsPrivateAsync.py` `start()`: now return the created `consume()` task so callers can retain/await it (GH#116).
- `okx/Account.py` `set_trading_config`: new method for `POST /api/v5/account/set-trading-config` (params `type` (required), `stgyType` (optional; 0=general, 1=delta neutral, applies when type=stgyType)); `precheck_set_delta_neutral`: new method for `GET /api/v5/account/precheck-set-delta-neutral` (param `stgyType`) (delta-neutral trading config).
- `okx/Account.py` `get_bill_type` / `apply_bills`: new methods for `GET /api/v5/account/subtypes` (optional `type`) and `POST /api/v5/account/bills-history-archive` (params `year`, `quarter`, optional `type`) (bill subtypes + async bill history archive).
- `okx/DualInvest.py` (new module) `DualInvestAPI`: 8 methods for the `/api/v5/finance/sfp/dcd/*` dual-currency (DCD) product surface — `get_currency_pairs`, `get_product_info`, `request_quote`, `trade`, `request_redeem_quote`, `redeem`, `get_order_state`, `get_order_history`.
- `okx/PublicData.py` `get_announcements`: new method for `GET /api/v5/announcement/announcements`.
- `okx/consts.py`: new path constants for all endpoints above, plus 8 `DUAL_INVEST_*` constants.

### Fixed
- `okx/websocket/WsPublicAsync.py` and `okx/websocket/WsPrivateAsync.py` `consume()`: wrap the receive loop in `try/except ConnectionClosedError` — on disconnect it now logs the error, pushes an `{"event": "error", "code": "ConnClosed", ...}` message to the existing callback, and re-raises so the awaited task surfaces the failure instead of dying silently. No auto-reconnect (retry is left to the caller) (GH#116).

### Changed
- `okx/Trade.py` `cancel_algo_order`: renamed the positional argument `params` → `orders_data` and added a docstring documenting the expected `list[{'instId', 'algoId'}]`. The legacy `params=` keyword is kept as a deprecated alias, so all existing call shapes (positional and `params=`) continue to work (GH#115).
- `okx/Trade.py` `place_algo_order`: added optional `advanceOrdType=None` (trigger-order advance type) and `tpTriggerRatio=None` / `slTriggerRatio=None`. Unset params are omitted from the request.
- `okx/Account.py` `get_fee_rates`: added optional `groupId=None` (query fees by instrument group). Unset param is omitted.
- `okx/Trade.py` `place_order`: added optional `isElpTakerAccess=None` (ELP taker access on IOC) and `instIdCode=None`. Unset params are omitted.
- `okx/Convert.py` `get_currency_pair` / `estimate_quote` / `convert_trade`: added optional `convertMode=None` (0=standard, 1=large-order VIP). Unset param is omitted.
- `okx/Trade.py` `amend_order`: added optional `newTpTriggerRatio=None` / `newSlTriggerRatio=None`. Unset params are omitted.

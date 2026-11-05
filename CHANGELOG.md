# Changelog

All notable changes to `python-okx` are documented in this file.

## [Unreleased]

### Changed
- Endpoint methods with required collection parameters (`simPos`,
  `counterparties`, `legs`, `rfqIds`, `clRfqIds`, `fromCcy`, `debtCcy`,
  `repayCcyList`, `recurringList`, `alloc`, `supCollateral`, `investData`)
  now default to `[]` in the signature, so a call without them still sends an
  empty array. Passing `None` explicitly now means "not sent" (ADR-0010):
  `create_rfq(legs=None)` no longer sends `legs`.
- `Subscriptions.add()` and `remove()` return `None` instead of a tuple of
  entries. Both check the whole batch first: a non-dict arg, or one whose
  `channel` is missing or blank, now raises `ValueError` and leaves the table
  as it was (it used to be skipped silently).
- `WsBaseAsync.unsubscribe()` applies the same arg rule as `subscribe()`,
  which it previously skipped.

### Removed
- `okx.websocket.WsUtils` is gone. `initLoginParams` and `getLocalTime` had
  one caller (`WsBaseAsync.login`) and one purpose; the login request is now
  built by `okx.websocket.login.login_payload()`, which also takes the
  timestamp as an argument. The signature primitive stays in `okx.utils.sign`
  and is shared with the REST layer.
- The `okx.websocket.subscriptions.Subscription` class. A table entry is the
  `(arg, callback)` pair it always held.

## [0.14.1]

### Added
- `WsBaseAsync.subscribe()` rejects an arg whose `channel` is missing or
  blank with `ValueError`, before the subscription table or the socket is
  touched. The server cannot route such a subscription, and the removed
  `checkSocketParams` helper never ran on the production path.

### Fixed
- `WsPublicAsync.from_transport()` raises `ValueError` for any `channel`
  outside `'public'`/`'business'`, including unhashable values such as a
  list. The previous lookup leaked `TypeError` for those, contradicting the
  "exception type and message unchanged" guarantee in ADR-0014.
- The hardcoded `AccountAPI` example in the README builds the account class
  from `Transport`; passing credentials directly has raised `TypeError`
  since 0.10 (ADR-0006 / ADR-0015).

## [0.14.0]

First release since 0.10.0. It rolls up four batches that were prepared but
never published on their own — the WebSocket connection seam (planned as
0.11.0), WebSocket message routing (0.12.0), the REST endpoint parameter
surface (0.13.0) and the API configuration surface (0.14.0). ADR-0004 batches
breaking changes by theme; this is the release that ships them together.

### Added
- `OkxClient.transport` returns the `Transport` the API class was built with;
  it is the one place to read credentials, environment and retry policy from.

### Changed
- `WsPrivateAsync` and `WsPublicAsync` are built with
  `from_transport(transport)` instead of `from_client(client)` (ADR-0008).
  The argument must be an `okx.transport.Transport`; credentials, `flag`,
  `debug` and `proxy` all come from it.
- WebSocket connections go through an injectable `WebSocketConnector`
  (`okx/websocket/connector.py`, ADR-0007). Both clients accept `connector=`
  and `proxy=`; when both are given the connector wins, as
  `Transport(proxy=, http=)` does.
- `Transport` keeps `proxy` on the object, so the WebSocket layer can inherit
  the REST proxy.
- A message is delivered to the callback registered for its `arg` (ADR-0009),
  so two channels on one connection no longer steal each other's messages. An
  acknowledgement without `arg` (an order response) is matched by its `id`.
  The table lives in `okx/websocket/subscriptions.py` (`Subscriptions`).
- `WsBaseAsync.callback` is now only the fallback for messages that match
  neither a subscription nor a request. It stays readable and writable and is
  deprecated; it is removed before 1.0.
- `WsBaseAsync.subscriptions` is a read-only view derived from the routing
  table. Assigning to it raises `AttributeError`.
- A callback passed with an `id` to `send()`/the order helpers answers that
  request once. Without an `id` it still becomes the fallback.
- Every REST endpoint method now passes all of its arguments to `Transport`,
  which drops the ones set to `None`. The 136 `if x is not None: params[x] = x`
  branches in the endpoint modules are gone; no request changes on the wire
  (ADR-0010).
- The WebSocket login protocol lives in `okx.websocket.login.LoginHandshake`.
  The read loop and the direct socket read share one rule for which frame
  answers a login; behaviour is unchanged (ADR-0012).
- Pagination validates the cursor in `okx.pagination`; `OkxClient.paginate`
  only forwards. Both entries raise the same message, naming the method
  (ADR-0013).
- The two WebSocket clients share one `Transport` → session-config mapping in
  `okx.websocket.config`; each client now only supplies its host table.
  Behaviour is unchanged (ADR-0014).

### Fixed
- A WebSocket proxy is never silently downgraded to a direct connection: when
  the installed `websockets` does not accept `proxy=` (it arrived in 15.0),
  `connect()` raises before opening anything. When no proxy is configured the
  argument is not passed at all, so `websockets` keeps its own environment
  detection.
- `FundingAPI.get_deposit_lightning` sent only `to`: `ccy` and `amt` were
  dropped from the request.

### Removed
- `okx.websocket.WebSocketFactory.WebSocketFactory`. To open connections
  yourself, pass `connector=` with an object that has
  `async connect(url) -> Connection` and returns the socket without keeping
  a copy (`WsBaseAsync.websocket` stays the only holder).
- `WsUtils.checkSocketParams`, `WsUtils.initSubscribeSet`,
  `WsUtils.getParamKey` and `WsUtils.isNotBlankStr`. They had no production
  callers and `getParamKey` could collide across channels; routing is now
  `Subscriptions`' job.
- The nine configuration properties `OkxClient` forwarded (ADR-0015):
  `API_KEY`, `API_SECRET_KEY`, `PASSPHRASE`, `flag`, `debug`, `domain`,
  `raise_on_error`, `max_retries` and `retry_backoff`. `proxy` had never
  been forwarded, which is how the second interface started to drift.

### Migration

| Before | After |
| --- | --- |
| `WsPrivateAsync.from_client(rest_api)` | `WsPrivateAsync.from_transport(transport)` |
| `WsPublicAsync.from_client(rest_api, channel="business")` | `WsPublicAsync.from_transport(transport, channel="business")` |
| `WebSocketFactory(url)` | `WsPrivateAsync(..., connector=YourConnector())` |
| `ws.callback = f` for a single channel | `await ws.subscribe(params, f)` |
| `ws.subscribe(a, fa); ws.subscribe(b, fb)` — `fb` got everything | each channel now reaches its own callback |
| `ws.subscriptions = {...}` | `await ws.subscribe(...)`; the view is read-only |
| `api.debug` (and the other eight configuration names) | `api.transport.debug` |

## [0.10.0]

Breaking release, the batch ADR-0004 reserved for the REST transport (ADR-0006).
The REST API surface keeps its endpoint methods; construction and the internal
request seam change.

### Changed
- Every REST API class is constructed with one `okx.transport.Transport`
  instead of its own copy of the connection settings.
- `Transport` owns the credentials, environment, proxy, retry and rate-limit
  configuration. One instance can be passed to any number of API classes; they
  then share a connection pool, a rate limiter and one configuration.
- `_request_with_params` and `_request_without_params` are replaced by
  `request(method, path, params=None)`, the single seam every endpoint method
  calls.

### Removed
- The `client=` constructor argument and its 11-line field copy. Sharing is now
  passing the same `Transport`.
- The configuration arguments on every API class constructor: `api_key`,
  `api_secret_key`, `passphrase`, `flag`, `base_api`, `debug`, `proxy`,
  `raise_on_error`, `max_retries`, `retry_backoff`, `rate_limit`.
- `OkxClient` is no longer an `httpx.Client`. `close()` and the context-manager
  protocol are kept as forwarding methods; other httpx methods (`get`,
  `post`, …) were never used by an endpoint and are gone.

### Migration

| Before | After |
| --- | --- |
| `TradeAPI(api_key=…, api_secret_key=…, passphrase=…, flag=…)` | `TradeAPI(Transport(api_key=…, api_secret_key=…, passphrase=…, flag=…))` |
| `base_api=…` on an API class | `base_api=…` on `Transport` |
| `debug=…` on an API class | `debug=…` on `Transport` |
| `proxy=…` on an API class | `proxy=…` on `Transport` |
| `raise_on_error=…` on an API class | `raise_on_error=…` on `Transport` |
| `max_retries=…` on an API class | `max_retries=…` on `Transport` |
| `retry_backoff=…` on an API class | `retry_backoff=…` on `Transport` |
| `rate_limit=…` on an API class | `rate_limit=…` on `Transport` |
| `AccountAPI(client=trade)` | `AccountAPI(transport)` with the same `Transport` |
| `api._request_with_params(POST, path, params)` | `api.request(POST, path, params)` |
| `api._request_without_params(GET, path)` | `api.request(GET, path)` |

## [0.9.0]

Breaking release, the batch ADR-0004 reserved for the WebSocket layer. The REST
API is untouched.

### Changed
- WebSocket callbacks may now be `async def`; a coroutine returned by the
  callback is awaited, so it does not block the event loop. Plain functions are
  still called inline, so existing callbacks keep working — but a coroutine is
  no longer leaked un-awaited.
- An exception raised by a callback is logged and the next message is still
  delivered. A failing callback no longer ends `consume()`.
- `start()` returns the supervisor task (read loop + heartbeat + reconnect)
  instead of the read loop. It stays alive across connection drops and ends when
  `stop()` cancels it. `reconnect=False` keeps the pre-0.9 shape: the task
  surfaces the connection error and ends.
- `WsPrivateAsync.subscribe()` no longer logs in on every call. The client
  authenticates once per connection, on the first subscribe or order, and again
  after a reconnect.
- `subscriptions` is now a mapping of the exact argument dictionaries instead of
  a never-read set. It is the source of truth for resubscription.
- `consume()` reads one connection; a drop reconnects instead of ending the
  stream.
- `pong` frames are consumed by the heartbeat and are not passed to the
  callback. Because callbacks are awaited in the read loop, one that runs longer
  than `ping_timeout` delays pong handling and can trigger a reconnect; offload
  long work to a task inside the callback.

### Added
- Heartbeat: a text `ping` every 25 seconds (`ping_interval`) with a `pong`
  required within 10 seconds (`ping_timeout`). A missing pong closes the socket
  and triggers a reconnect.
- Reconnect with exponential backoff (`reconnect_backoff`, 1s doubling to
  `reconnect_max_backoff`, 60s) and automatic replay of every recorded
  subscription, for both the public and the private client.
- `WsBaseAsync`, the shared session implementation. `WsPublicAsync` and
  `WsPrivateAsync` are now thin subclasses; their public methods did not change.
- Type annotations across `okx.websocket`.

### Removed
- `WsPrivateAsync(useServerTime=...)` and its `DeprecationWarning`. The argument
  never did anything: the constructor forced `self.useServerTime = False`, so
  login always signed with local time. `WsUtils.initLoginParams` no longer takes
  it either.
- `okx.websocket.WsUtils.getServerTime`, which hardcoded the live-site host and
  existed only to serve that argument.

### Migration
- Await the value of `start()` as the supervisor: it now ends at `stop()`
  rather than when the socket drops. Pass `reconnect=False` to have it end (and
  raise) on a drop, as before.
- `ws.subscriptions` is a `dict` keyed by the JSON form of each channel
  argument. It was never populated before 0.9, so code that read it was reading
  an empty set.
- Calling `start()` on a client that is already started raises `RuntimeError`
  instead of silently running a second read loop.
- Subscribing while a reconnect is in progress raises `RuntimeError` because
  there is no socket to send on; retry after the session is back.
- `useServerTime` is gone, so the positional order after `url` shifted: `debug`
  is now the fifth positional parameter. A call that passed `useServerTime`
  positionally would land on `debug` instead — drop the argument, or pass
  `debug=` by name.
- `WsUtils.initLoginParams` lost its leading `useServerTime` parameter, so
  `initLoginParams(False, key, passphrase, secret)` would now mix up every
  argument; call it with keywords. It is an internal helper, but it was
  importable.

## [0.8.1]

Defect-fix release.

### Fixed
- `WsUtils.isNotBlankStr` used `~param.isspace()`, a bitwise NOT that returns `-2` or `-1` — both truthy. The helper therefore never reported a blank string, and `checkSocketParams` never rejected an empty channel. It now strips and compares.
- `WebSocketFactory.connect` swallowed every exception and returned `None`; callers then iterated `None` and lost the real cause (certificate, proxy, DNS). The original exception is now raised.
- `WsPublicAsync.login` set `isLoggedIn = True` without reading the server's response, so a wrong passphrase looked like success and every later subscription silently went nowhere. Both classes now wait for the `login` acknowledgement, raise `ConnectionError` on a non-zero code, raise `TimeoutError` after `timeout` seconds (default 10), and hand non-login frames to the callback.
- `WsPrivateAsync.subscribe` no longer sleeps five seconds after login — the acknowledgement makes that guess unnecessary.

### Changed
- README no longer claims WebSocket reconnection and multiplexed connections; neither existed.

## [0.8.0]

Feature release. Existing constructor calls keep working; `url` now has a default.

### Added
- WebSocket endpoint constants in `okx.consts`: `WS_PUBLIC_URL`, `WS_PRIVATE_URL`, `WS_BUSINESS_URL` and the demo counterparts (`wspap` host with `brokerId=9999`).
- `WsPublicAsync` and `WsPrivateAsync` default their `url` to the live endpoint, so the host no longer has to be hardcoded.
- `WsPrivateAsync.from_client(client)` and `WsPublicAsync.from_client(client, channel='public')`: take the credentials from an existing REST client and pick the live or demo host from its `flag`. `flag='1'` on REST (demo trading) now selects the demo WebSocket host, so the two layers cannot silently end up in different environments.

### Notes
- Pass `url=` to override; if OKX moves a host before this package is updated, that is the way around it.
- `WsPrivateAsync` still accepts the deprecated `useServerTime` argument. Removing it is a signature change, so it waits for the next breaking window (tracked in `.scratch/ws-config/issues/02-remove-use-server-time.md`).

## [0.7.0]

Feature release. Nothing existing changes behaviour.

### Added
- `OkxClient.paginate(method, cursor=..., params=..., page_size=100, max_pages=None)` and the standalone `okx.pagination.paginate`: walk a list endpoint backwards through `after`, yielding one record at a time.
- `cursor` is **required** and names the response field `after` refers to (`billId`, `ordId`, `ts`, …). The field differs per endpoint and guessing it silently skips or repeats records, so a missing `cursor` raises at the call site.
- Endpoints that paginate by page number (`get_announcements`, `get_tvb_link_list`) are rejected with a message pointing at `page=`.

### Notes
- The walk stops at an empty page or when the cursor stops advancing — the latter guards against a server that ignores `after`.
- A page shorter than `page_size` does **not** stop the walk: endpoints cap `limit` at their own maximum, so a short page means the cap was reached, not the end. Expect one final empty page.
- `before` (fetching newer records) is not supported; polling belongs to the WebSocket layer.
- Every page goes through the retry and rate-limit path like any other request.

## [0.6.0]

Feature release, opt-in only: the defaults are unchanged, so upgrading changes no existing behaviour.

### Added
- `OkxClient` accepts `max_retries` (default `0`), `retry_backoff` (default `1.0` seconds, doubled per attempt) and `rate_limit` (default `False`).
- Retries apply to GET requests, to POST requests that carry an idempotency key (`clOrdId`, `algoClOrdId` or `reqId`), and only when the failure is transient: `httpx.TransportError`, HTTP 429/5xx, or business codes `50001`, `50004`, `50011`, `50013`. A rejection such as `51000` is replayed never — see ADR-0003.
- `rate_limit=True` throttles calls through `okx.consts.rate_limits.RATE_LIMITS`, a per-path `(requests, window_seconds)` table; paths missing from it are not throttled.
- `okx.rate_limit.RateLimiter`: sliding-window limiter, usable on its own.

### Notes
- Every retry rebuilds the timestamp and signature, so an expired signature is never replayed.
- Passing `client=` copies the retry and rate-limit settings from that client, including the shared limiter.

## [0.5.0]

Breaking release. This is the only window in the 0.4/0.5 line for public-API changes, so nothing renamed here keeps a compatibility alias (see ADR-0001). The "Renamed" table below is the complete migration list.

### Changed
- Failed requests raise `OkxAPIException` by default when the HTTP status is `>= 400` or the response `code` is not `'0'`. The exception exposes `code`, `message`, `status_code` and the original `response`; network failures still surface as the underlying `httpx` exception. Pass `raise_on_error=False` to return the payload dict exactly as 0.4.x did.
- All 22 `*API` classes now inherit `OkxClient.__init__`; the duplicated subclass constructors are gone. Adding a client-wide option no longer means editing 22 files.
- The base constructor's `domain` parameter is now `base_api`, matching `OkxClient`. `domain=` keyword calls must switch to `base_api=`.
- `use_server_time` is removed from every constructor; the fourth positional argument is now `flag`. The parameter had been a silent no-op since 0.4.x, so sync the system clock (for example with NTP) if timestamp drift matters.
- The REST layer logs through the standard `logging` module (`okx.okxclient`, `okx.utils`), matching the WebSocket layer. Application handlers receive SDK records; a `NullHandler` on the `okx` logger keeps unconfigured apps quiet.
- `okx.websocket.WsUtils.getServerTime` uses the already-required `httpx` instead of `requests`.
- Empty-value semantics are unified: `None` is the only "not supplied" marker, and an explicit `''` is sent as a real parameter. Every optional REST argument now defaults to `None` instead of `''`. GET query values that are lists or dicts are JSON-encoded; POST bodies drop top-level `None` values. Leftover shared mutable defaults (`attachAlgoOrds=[]` in `place_algo_order`, `params=[]` in `set_marker_instrument`, `ccy=[]` in `convert_dust_assets`) now default to `None`.
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

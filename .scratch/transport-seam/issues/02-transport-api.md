# 传输层对外

Status: resolved
Done in: 0.10.0

## 为什么

`OkxClient` 不再继承 `httpx.Client` 之后（见 `issues/01-transport-internal.md`），9 个配置参数仍然长在每个 API 类的构造函数上，而它们描述的是传输层，不是端点。共享连接池只能靠 `client=` 这种影子适配器。

## 做什么

API 类改收 `Transport`，9 个配置参数移到 `Transport`，删 `client=`。与 ADR-0004 的破坏性批次一起排期。

## 完成标准

1. `TradeAPI(Transport(...))` 可构造；`TradeAPI(api_key=...)` 抛 `TypeError`。
2. `client=` 删除，传入抛 `TypeError`。
3. 同一个 `Transport` 传给多个 API 类时共用一个连接池，且 `rate_limit` / `max_retries` 的配置在构造点唯一。
4. CHANGELOG 迁移表逐条列出：9 个构造参数从 API 类移到 `Transport`；共享连接池从 `client=` 改为传同一个 `Transport`；`_request_with_params` / `_request_without_params` 合并为 `request`。


## Comments

2026-11-05 — implemented on top of 01. API classes now take one `Transport`;
`client=` and the 11 configuration arguments are gone; `_request_with_params` /
`_request_without_params` collapsed into `request`. ADR-0006 records the decision,
CHANGELOG 0.10.0 carries the migration table, README and both notebooks use the
new constructor. Verification: `pytest test/unit` 602 passed, unchanged under
`ALL_PROXY=socks5h://127.0.0.1:1`; contract suite 282 passed. The 17 live-API
modules under `test/` were migrated too (50 skipped without credentials). Released as 0.10.0 (tag `v0.10.0`).

# 超时类错误不自动重放

`okx/transport.py` 的 `_RETRYABLE_CODES` 里有 `50004`，注释称这些码是「rejected before it could be matched, so replaying it cannot double-execute」。但 2026-11-06 对 OKX 官方文档的逐条核对（见 `.scratch/rate-retry-policy/issues/11-idempotency-and-error-codes.md`）表明：`50004` 是**接口请求超时**，官方原文是「does not mean that the request was successful or failed, please check the request result」——结果是未知的，不是「确定未执行」。`51149`（Order timed out）是 HTTP 500，措辞相同。

同一份核对还确认：`clOrdId` 只在 pending 内唯一，终态可复用；即便带键也不保证不重复下单。所以「重放不会二次执行」这个前提对超时类错误不成立。对一个交易 SDK，重试一个结果未知的下单请求可能真的下第二单——这正是 ADR-0003 想避免的事。

我们决定：**只自动重放官方建议「稍后重试」的错误；官方明说「结果未知、请检查请求结果」的错误（当前 `50004`、`51149`）一律不自动重放。** 结果未知时调用方应先查询请求结果，而不是重发。实现上新增 `_OUTCOME_UNKNOWN_CODES`，在 `_is_transient` 里先于 `status >= 500` 判断。

## Considered Options

- **维持现状（50004 与 51149 继续重试）**：注释的理由已被官方原文证伪；对下单类请求，重试可能真的二次下单。
- **只移除 50004、不管 51149**：`51149` 是 HTTP 500，仍会被 `status >= 500` 的规则重试，风险与 50004 同源。
- **所有业务码都不重试**：`50001` / `50011` / `50013` 官方明确说「稍后重试 / 限流」，一并放弃会让 `max_retries` 失去大部分价值。
- **要求调用方显式 `replayable=True` 才允许超时重试**：需要区分「派生」与「显式」的重放判定，复杂度换来的只是极少数场景；当前没有需求。

## Consequences

- `_RETRYABLE_CODES` 从 4 个码减为 3 个：`50001` / `50011` / `50013`。
- 新增 `_OUTCOME_UNKNOWN_CODES = {"50004", "51149"}`，在 `_is_transient` 里先于 `status >= 500` 判断；将来官方新增同类码时加入。
- `okx/transport.py:22-24` 的注释改写；README 补「超时类错误不自动重试、先查结果」。
- 对 opt-in `max_retries` 的用户是行为变化：下单 / 撤单超时不再自动重试。CHANGELOG 进 `### Changed`，不写 Migration（没有 API 签名 / 结构变化）。
- 与 ADR-0003 的关系：不推翻「只重试可重放请求」，只细化「哪些错误算可重试」；`clOrdId` 仍是获得重试的必要条件，但不是 exactly-once 保证。

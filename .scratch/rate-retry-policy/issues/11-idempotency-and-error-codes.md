# 11 · OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查

Type: research
Status: open
Blocked by: —

## Question

[重试判定是否改动](04-retry-judgement.md) 决定维持 ADR-0003 的三条判定原状，但 README.md:111 与 CHANGELOG.md:330 把 `_IDEMPOTENCY_KEYS`（`clOrdId` / `algoClOrdId` / `reqId`）与 `_RETRYABLE_CODES`（50001 / 50004 / 50011 / 50013）当既成事实陈述，没有出处；[OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 的 findings 只查了限流，没覆盖这些。把**事实**铺回来，作为「维持原状」这一决定的依据核实，以及 [11 的事实要不要改重试判定](12-retry-facts-followup.md) 的输入。只查证、不下结论、不替项目定改动：

1. OKX v5 官方是否公布过「幂等键 / 客户订单 ID」的完整清单？除 `clOrdId` / `algoClOrdId` / `reqId` 外还有哪些（例如批量下单、策略委托、提币、划转等场景的等价字段）？逐条给出来源。
2. 业务码 `50001` / `50004` / `50011` / `50013` 官方分别是什么含义？`okx/transport.py:22-24` 的注释称它们「rejected before it could be matched, so replaying it cannot double-execute」——这个解释与官方一致吗？
3. 官方是否还公布其他属于「瞬时 / 可重试」的业务码（例如服务繁忙、限流类）？CHANGELOG.md:330 举 `51000` 为「永不重试」的确定性拒绝，这个分类有官方依据吗？
4. 有没有 GET 端点其实带副作用或会改变服务端状态？ADR-0003 把「GET 一律可重试」当公理，需要核实这个前提。
5. HTTP 429 / 5xx 与业务码同时出现时，官方对优先级有没有说明（04 已确认代码现状是 429/5xx 优先）？

每一条结论追到拥有它的官方来源（OKX docs-v5 错误码页 / 端点详情 / Change Log），不引二手转述；查不到就写明，不要编造数值或 URL。**不回答**：该不该改集合、该不该翻白名单、要不要 ADR——那是 04 与 [11 的事实要不要改重试判定](12-retry-facts-followup.md) / [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 的决策。

## Context

findings 落在 throwaway 分支 `research/idempotency-and-error-codes` 上的 `.scratch/rate-retry-policy/research/idempotency-and-error-codes.md`；按 wayfinder 约定永不合并，沿用本地保留决定、不 push。本工单为 AFK research，被解时由 fresh-context 子代理调用 `/research`；charting 阶段之外不主动 fire。

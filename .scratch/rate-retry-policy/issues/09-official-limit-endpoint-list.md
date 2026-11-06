# 09 · 官方已公布限额的端点清单与 274/135 差异核对

Type: research
Status: claimed
Blocked by: 03

## Question

[表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 把覆盖验收线定为「官方已公布限额、且与项目路径常量对应的端点」，但 [OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 的 findings 只给了统计数字——`Rate Limit:` 标注 137 处、`HTTP Request` 块 141 个、distinct REST 路径 135 个——并声明「未穷尽逐一核验，只作统计性陈述」，没有清单。项目 `okx/consts/endpoints/` 去重后有 274 个 `/api/v5/...` 路径，与 135 差距的原因也未查。

把**事实**铺回来，供 spec 的判定规则与后续施工使用。只查证、不下结论、不替项目定补全策略：

1. 逐个核对 OKX v5 REST 端点详情，产出一份**带 `Rate Limit:` 标注的端点路径清单**（路径 + 限额数值 + 时间窗 + 计数维度 + 来源页），注明取证范围与快照日期。
2. 把这份清单与 `okx/consts/endpoints/` 的 274 个路径常量对齐，逐条标出：两侧都有、仅官方有、仅项目有。
3. 解释 274 与 135 的差异：别名 / 废弃端点 / 同一路径多方法 / 非 REST 路径 / 统计口径差异，各占多少。
4. 标出项目路径常量里**官方无对应端点**的那些（03 的 Answer 明确它们不在验收线内、按「未收录端点」维持不限流）。
5. 若官方某些端点确实没有 `Rate Limit:` 行，逐个列出并说明原文表述（findings 目前「未发现成批」，但只作统计性陈述，需要逐一确认）。

每一条结论追到拥有它的官方来源（OKX docs-v5 端点详情页 / Change Log），不引二手转述；查不到就写明，不要编造数值或 URL。**不回答**：该不该补全、补全到什么程度、表条目什么形状——那是 03 与 [限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 的决策。

## Context

findings 落在 throwaway 分支 `research/official-limit-endpoint-list` 上的 `.scratch/rate-retry-policy/research/official-limit-endpoint-list.md`；按 wayfinder 约定永不合并，沿用本地保留决定、不 push。

> **来自 08 的输入（2026-11-06）**：[限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 已定**保持二元组 + `path` 单键、表不承载计数维度 / 窗口语义 / 多方法 / REST-WS 共享**。因此本工单的清单是这些官方事实的**唯一载体**：解 09 时把「路径 + 限额数值 + 时间窗 + 计数维度 + 多方法区分 + 来源页」逐条列全，尤其标出同路径多方法（`/api/v5/trade/order` 的 POST + GET）限额是否不同——若不同，是 08 触发条件里「另开新工单」的输入。

> **来自 10 的输入（2026-11-06）**：[官方 Change Log 变更时表怎么同步](10-changelog-sync.md) 已定本工单的清单是**一次性事实输入、不是长期维护对象**：findings 留在 throwaway 分支（永不合并、不 push），解 09 时按 08 的要求把字段列全即可，不必设计成可长期维护的结构。长期维护以官方 Change Log + 端点详情页为唯一外部来源，每次同步重新取证并在 PR / CHANGELOG 留痕；不随表同步更新本清单、也不把分支合并进 master。

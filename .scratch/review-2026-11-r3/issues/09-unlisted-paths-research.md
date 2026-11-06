# 09 · 33 条官方清单未收录路径的逐条定性

Type: research
Status: needs-triage
Blocked by: —

## Question

01 把 33 条路径标成 `NOT_IN_OFFICIAL_LIST` 豁免（`okx/consts/rate_limits.py`），但只记录了「官方 S1 快照里没有」，没有回答**为什么没有**。要逐条给出结论：

1. 官方已废弃 / 已改名（给出新路径或迁移说明）；
2. 项目路径拼写错误（给出正确路径）；
3. 官方未公开但实际可用（给出证据，例如 API 错误码或文档外说明）；
4. 无法确认（保留豁免，写明已查范围）。

## 输入

- 研究文档：`.scratch/rate-retry-policy/research/official-limit-endpoint-list.md` 第 4 节（33 条清单，来自 throwaway 分支 805528e，不合并）。
- 当前豁免表：`okx/consts/rate_limits.py` 的 `RATE_LIMIT_EXEMPTIONS`（33 条 `NOT_IN_OFFICIAL_LIST` + 4 条 `ORDERS_BASED`；后者不在本单范围）。
- 路径分组：account 17、affiliate 5、asset 4、market 2、public 2、finance 1、sprd 1、broker 1。

## 取证要求

- 只用 OKX 官方一手来源：S1/S2 文档全文（含正文、示例、Change Log）、官方 Change Log 的历史版本；不接受镜像站、博客、第三方 SDK。
- 每条给出「结论 + 证据 + 查询日期」；查不到就写「无法确认」，不要推断。
- 能用公开只读接口验证的（如 public/market 段），记录请求与返回码（不要用真实凭证）。

## 验收标准

1. 33 条每条一行结论，附证据链接或原文片段与日期。
2. 给出三张候选名单：可删除（方法 + 常量）、应改路径、保留并维持豁免。
3. 明确删除的版本策略：按 ADR-0004 属 minor，需要 Migration 行；研究本身不改代码。
4. 更新 `RATE_LIMIT_EXEMPTIONS` 的注释与原因分类的建议（若需要新增原因码，给出理由）。

## 不在本单

- 4 条 orders-only（已由 `ORDERS_BASED` 解释）。
- 补全 237 条表的数值（已由 1469f30 收口）。
- 实际删除代码（研究结论出来后另开施工单）。

## Comments

- 2026-11-06 由 01 的拍板拆出：`architecture-review-20261106-202110.html` 候选 01，01 工单 1469f30 已收口。

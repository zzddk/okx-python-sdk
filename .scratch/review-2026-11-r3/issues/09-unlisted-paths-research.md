# 09 · 33 条官方清单未收录路径的逐条定性

Type: research
Status: resolved
Done in: research only (2026-11-06)
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

## Answer

**结论（2026-11-06）**：33 条按证据分成三组——**已下线 15 条**、**已改名/迁移 10 条**、**无法确认或非公开 8 条**。可删除 16 个方法 + 1 个常量，7 条应改路径，1 条需重新设计参数；8 条维持豁免。

**取证**：S1 = <https://www.okx.com/docs-v5/en/>，2026-11-06 抓取 5,280,641 B；L = <https://www.okx.com/docs-v5/log_en/>，2026-11-06 抓取 1,194,560 B（Change Log）。以下 33 条路径在 S1 全文中均不出现（逐条 `grep` 为 0）。

### A. 官方已下线（15）

| 路径 | 项目方法 | 证据 |
|---|---|---|
| /api/v5/account/fixed-loan/amend-borrowing-order | AccountAPI.amend_fix_loan_borrowing_order | L 2025-03-03「Fixed Loan API offline」逐条列出该路径 |
| /api/v5/account/fixed-loan/borrowing-limit | AccountAPI.get_fix_loan_borrowing_limit | 同上 |
| /api/v5/account/fixed-loan/borrowing-order | AccountAPI.place_fix_loan_borrowing_order | 同上 |
| /api/v5/account/fixed-loan/borrowing-orders-list | AccountAPI.get_fix_loan_borrowing_orders_list | 同上 |
| /api/v5/account/fixed-loan/borrowing-quote | AccountAPI.get_fix_loan_borrowing_quote | 同上 |
| /api/v5/account/fixed-loan/manual-reborrow | AccountAPI.fix_loan_manual_reborrow | 同上 |
| /api/v5/account/fixed-loan/repay-borrowing-order | AccountAPI.repay_fix_loan_borrowing_order | 同上 |
| /api/v5/account/set-riskOffset-type | AccountAPI.set_risk_offset_type | L 2025-01-17「API offline Set risk offset type (POST /api/v5/account/set-riskOffset-type)」；S1 现为 POST /api/v5/account/set-riskOffset-amt |
| /api/v5/account/vip-interest-accrued | AccountAPI.get_vip_interest_accrued_data | L 2024-11-21「taking VIP Loan ... offline」；S1 无任何 vip 路径 |
| /api/v5/account/vip-interest-deducted | AccountAPI.get_vip_interest_deducted_data | 同上 |
| /api/v5/account/vip-loan-order-detail | AccountAPI.get_vip_loan_order_detail | 同上 |
| /api/v5/account/vip-loan-order-list | AccountAPI.get_vip_loan_order_list | 同上 |
| /api/v5/market/books-lite | MarketAPI.get_order_lite_book | L 2024-03-27「Decommissioned the order lite book endpoint GET /api/v5/market/books-lite」 |
| /api/v5/public/liquidation-orders | （仅常量 LIQUIDATION_ORDERS，无方法） | L 2023-04-03「no longer support ... through the REST endpoint ... subscribe to the websocket channel」 |
| /api/v5/asset/convert-dust-assets | FundingAPI.convert_dust_assets | L 2024-10-17「Small assets convert The API has offline ... recommended to use Easy convert」；S1 有 /api/v5/trade/easy-convert。注：条目给的是功能名，未给路径，按功能对应 |

### B. 已改名 / 迁移（10）

| 旧路径 | 项目方法 | 当前官方路径 | 证据 |
|---|---|---|---|
| /api/v5/account/borrow-repay | AccountAPI.borrow_repay | /api/v5/account/spot-manual-borrow-repay | S1 有「Manual borrow / repay」新路径；项目已另有 MANUAL_REBORROW_REPAY + spot_manual_borrow_repay；L 无改名日期 |
| /api/v5/account/borrow-repay-history | AccountAPI.get_borrow_repay_history | /api/v5/account/spot-borrow-repay-history | S1 有「Get borrow/repay history」新路径；项目已另有 GET_BORROW_REPAY_HISTORY；L 无改名日期 |
| /api/v5/asset/purchase_redempt | FundingAPI.purchase_redempt | /api/v5/finance/savings/purchase-redempt | L 2023-03-15 宣布迁移，L 2024-01-22 旧端点下线；项目已另有 SAVING_PURCHASE_REDEMPTION |
| /api/v5/market/block-trades | MarketAPI.get_block_trades | /api/v5/public/block-trades | L 2023-11-08「Migrated block trade public transactions ... new GET /api/v5/public/block-trades」 |
| /api/v5/sprd/ticker | SpreadTradingAPI.get_ticker | /api/v5/market/sprd-ticker | L 2024-05-10「Added new endpoints for spread trading market data: Get ticker (Public)」；S1 标题为 Get ticker (Public) |
| /api/v5/public/vip-interest-rate-loan-quota | PublicAPI.get_vip_interest_rate_loan_quota | /api/v5/public/interest-rate-loan-quota | S1 有非 vip 路径；项目 PublicData.py:68 的注释已引用该路径；L 无改名条目 |
| /api/v5/affiliate/tvb/invitee/detail | AffiliateAPI.get_tvb_invitee_detail | /api/v5/affiliate/invitee/detail | S1 当前路径去掉 /tvb/；L 无 tvb 相关条目（无法确认 tvb 是否曾上线） |
| /api/v5/affiliate/tvb/invitee/list | AffiliateAPI.get_tvb_invitee_list | /api/v5/affiliate/invitee/list | 同上 |
| /api/v5/affiliate/tvb/link/list | AffiliateAPI.get_tvb_link_list | /api/v5/affiliate/link/list | 同上 |
| /api/v5/affiliate/tvb/performance/summary | AffiliateAPI.get_tvb_performance_summary | /api/v5/affiliate/performance/summary | 同上 |

### C. 无法确认 / 非公开（8，维持豁免）

| 路径 | 项目方法 | 结论 |
|---|---|---|
| /api/v5/account/simulated_margin | AccountAPI.get_simulated_margin | S1 无；L 2024-02-01 起有「Position builder (new)」，项目也已暴露 position-builder；是否同一功能的旧名无明示，不能据此删除 |
| /api/v5/account/subaccount/interest-limits | SubAccountAPI.get_sub_account_borrow_interest_and_limit | S1 无该子账户变体；L 2024-11-21 VIP Loan 下线、loanAlloc 相关字段标 Deprecated，但未点名该路径 |
| /api/v5/account/subaccount/set-loan-allocation | SubAccountAPI.set_sub_accounts_vip_loan | 同上；方法名指向 VIP loan allocation，随 VIP Loan 下线的可能性高，但无直接条目 |
| /api/v5/asset/deposit-lightning | FundingAPI.get_deposit_lightning | S1 无；L 2023-08-22 仍给「Withdrawal Lightning withdrawals」加响应参数，之后无下线条目 |
| /api/v5/asset/withdrawal-lightning | FundingAPI.withdrawal_lightning | 同上；功能最后出现于 2023-08-22，无明确下线记录 |
| /api/v5/affiliate/tvb/tier-breakdown | AffiliateAPI.get_tvb_tier_breakdown | S1 无任何 tier 路径；当前 affiliate 端点只有 invitee/co-inviter/link/performance/sub-affiliate |
| /api/v5/broker/fd/rebate-per-orders | FDBrokerAPI.get_rebate_details_download_link / generate_rebate_details_download_link | S1 没有任何 /broker/ REST 路径，Broker Program 只是介绍页；L 2026-05-14 提到 FD Broker，但公开文档无路径，按 partner-only 处理 |
| /api/v5/finance/savings/set-lending-rate | SavingsAPI.set_lending_rate | L 2023-03-15/2024-01-22 把它作为 savings 迁移的目标路径；S1 当前只保留 lending-history / lending-rate-history / lending-rate-summary，删除时间未记录 |

### 施工候选名单（删除 / 改路径 / 需设计 / 保留）

**1. 可删除（16 个方法 + 1 个常量）**
- Fixed loan 7：`AccountAPI.amend_fix_loan_borrowing_order`、`get_fix_loan_borrowing_limit`、`place_fix_loan_borrowing_order`、`get_fix_loan_borrowing_orders_list`、`get_fix_loan_borrowing_quote`、`fix_loan_manual_reborrow`、`repay_fix_loan_borrowing_order`
- VIP 4：`get_vip_interest_accrued_data`、`get_vip_interest_deducted_data`、`get_vip_loan_order_detail`、`get_vip_loan_order_list`
- Books-lite 1：`MarketAPI.get_order_lite_book`
- Small assets convert 1：`FundingAPI.convert_dust_assets`（推荐改用现成的 `TradeAPI.easy_convert`）
- 重复端点 3：`AccountAPI.borrow_repay`、`AccountAPI.get_borrow_repay_history`、`FundingAPI.purchase_redempt`
- 常量 1：`LIQUIDATION_ORDERS`（无方法；REST 已下线，WS 频道仍可用）

**2. 应改路径（7）**
- `MarketAPI.get_block_trades` → `/api/v5/public/block-trades`
- `SpreadTradingAPI.get_ticker` → `/api/v5/market/sprd-ticker`
- `PublicAPI.get_vip_interest_rate_loan_quota` → `/api/v5/public/interest-rate-loan-quota`（建议同时去掉方法名里的 vip）
- `AffiliateAPI.get_tvb_invitee_detail` → `/api/v5/affiliate/invitee/detail`
- `AffiliateAPI.get_tvb_invitee_list` → `/api/v5/affiliate/invitee/list`
- `AffiliateAPI.get_tvb_link_list` → `/api/v5/affiliate/link/list`
- `AffiliateAPI.get_tvb_performance_summary` → `/api/v5/affiliate/performance/summary`
（后 4 个建议同时去掉 `tvb_` 前缀；属破坏性改名）

**3. 需重新设计（1）**
- `AccountAPI.set_risk_offset_type` → `/api/v5/account/set-riskOffset-amt`。旧端点已下线，但新端点参数是「金额」而非「类型」，不能只换路径；需定新方法名、参数与旧方法的去留。

**4. 保留并维持豁免（8）**
- `simulated_margin`、`subaccount/interest-limits`、`subaccount/set-loan-allocation`、`deposit-lightning`、`withdrawal-lightning`、`affiliate/tvb/tier-breakdown`、`broker/fd/rebate-per-orders`、`finance/savings/set-lending-rate`。

### 版本策略与豁免表建议

- 删除 16 个方法与 7 条改路径都是公共 API 变化，按 ADR-0004 进 **0.16.0** 破坏性批次，写 `### Migration`；与 10（死异常）同批。研究本身不改代码，施工见 11。
- 0.16.0 之后，被删/被改的路径从 `RATE_LIMIT_EXEMPTIONS` 移除；保留的 8 条继续用 `NOT_IN_OFFICIAL_LIST`。现有两个原因码已够，不需要新增。
- 若 8 条后续拿到下线和替代证据，走同一删除流程，不要长期挂着。

**验收对照**：33 条逐条有结论与证据；三张名单与 1 条设计项齐全；版本策略按 ADR-0004；未改任何代码。

## Comments

- 2026-11-06 由 01 的拍板拆出：`architecture-review-20261106-202110.html` 候选 01，01 工单 1469f30 已收口。

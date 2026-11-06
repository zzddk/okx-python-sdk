# 11 · 0.16.0：删除已下线端点、修正改名路径

Type: task
Status: needs-triage
Blocked by: —

## Question

09 的结论给出了 33 条未收录路径的定性。本单把其中的施工项收进 **0.16.0** 破坏性批次（与 10 的死异常同批），研究本身不改代码。

## 施工项

### 删除（16 个方法 + 1 个常量）

- Fixed loan 7：`amend_fix_loan_borrowing_order`、`get_fix_loan_borrowing_limit`、`place_fix_loan_borrowing_order`、`get_fix_loan_borrowing_orders_list`、`get_fix_loan_borrowing_quote`、`fix_loan_manual_reborrow`、`repay_fix_loan_borrowing_order`
- VIP 4：`get_vip_interest_accrued_data`、`get_vip_interest_deducted_data`、`get_vip_loan_order_detail`、`get_vip_loan_order_list`
- Books-lite 1：`get_order_lite_book`
- Small assets convert 1：`convert_dust_assets`（引导用 `easy_convert`）
- 重复端点 3：`borrow_repay`、`get_borrow_repay_history`、`purchase_redempt`（项目已暴露对应的新路径）
- 常量 1：`LIQUIDATION_ORDERS`（无方法）

### 改路径（7）

- `get_block_trades` → `/api/v5/public/block-trades`
- `SpreadTradingAPI.get_ticker` → `/api/v5/market/sprd-ticker`
- `get_vip_interest_rate_loan_quota` → `/api/v5/public/interest-rate-loan-quota`（方法名建议去 vip）
- `get_tvb_invitee_detail` → `/api/v5/affiliate/invitee/detail`
- `get_tvb_invitee_list` → `/api/v5/affiliate/invitee/list`
- `get_tvb_link_list` → `/api/v5/affiliate/link/list`
- `get_tvb_performance_summary` → `/api/v5/affiliate/performance/summary`
（后 4 个建议同时去掉方法名的 `tvb_` 前缀，属破坏性改名）

### 需重新设计（1）

- `set_risk_offset_type` → `/api/v5/account/set-riskOffset-amt`：旧端点已下线，新端点参数是金额而非类型，需定新方法名、参数与旧方法的去留。

### 保留（8，不动）

`simulated_margin`、`subaccount/interest-limits`、`subaccount/set-loan-allocation`、`deposit-lightning`、`withdrawal-lightning`、`affiliate/tvb/tier-breakdown`、`broker/fd/rebate-per-orders`、`finance/savings/set-lending-rate`。

## 验收标准

1. 全仓 grep 旧路径为 0；删除的方法/常量不再出现在 `test/unit/okx/endpoints.py` 表里。
2. 保留下来的 8 条仍在 `RATE_LIMIT_EXEMPTIONS`，原因 `NOT_IN_OFFICIAL_LIST`；被删/改的路径从豁免表消失。
3. 端点契约测试、限流分区测试全绿；`ruff check okx/` 通过。
4. CHANGELOG 的 0.16.0 `### Migration` 覆盖删除与改名；与 10 写在同一段迁移说明里（ADR-0004）。
5. `set_risk_offset_type` 的新旧参数差异有单独的决定记录。

## 未决

- 0.16.0 是否就是下一个版本？本单与 10 都等这个发版决策。
- `broker/fd/rebate-per-orders` 若确认是 partner-only，是否提供 `broker=` 文档链接而不是删方法。

## Comments

- 2026-11-06 由 09 的结论拆出；逐条证据见 `issues/09-unlisted-paths-research.md`。

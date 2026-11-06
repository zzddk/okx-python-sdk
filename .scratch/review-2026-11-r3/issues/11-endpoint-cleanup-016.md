# 11 · 0.16.0：删除已下线端点、修正改名路径

Type: task
Status: resolved
Done in: 0.16.0 (91272dd)
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

## Answer

**拍板（2026-11-06）**：按 09 清单施工，落进 0.16.0 批次；affiliate 改名并对齐参数，risk offset 删除旧方法新增 amount。

**实际落地（与开工清单的差异）**

- 删除 **17 个方法 + 18 个常量**（开工清单写 16+1）：`get_vip_interest_rate_loan_quota` 经查是重复端点——项目已有 `get_interest_rate_loan_quota` 指向正确路径——按重复删除，而不是改路径；另外 `LIQUIDATION_ORDERS` 是只删常量。
- 改路径 **6 条**：`get_block_trades` → `/api/v5/public/block-trades`；`SpreadTradingAPI.get_ticker` → `/api/v5/market/sprd-ticker`；4 条 affiliate 去掉 `/tvb/`。
- 新增 `set_risk_offset_amount(ccy, clSpotInUseAmt)`，删除 `set_risk_offset_type` 与 `SET_RISK_OFFSET_TYPE`；旧端点已下线，新参数完全不同。
- 限流表新增 7 条官方路径（block、sprd、4 affiliate、risk offset），验收快照同步；现在是 **244 / 256**，12 条豁免（4 orders + 8 未收录）。
- 端点表、契约测试、命名测试同步；CHANGELOG 的 Removed 与 Migration 已写。

**验收对照**：846 passed / 322 subtests；`ruff check okx/` 通过；`okx/` 与 `test/unit` 中旧路径为 0；分区测试无未覆盖、无重叠。

**未决**：0.16.0 的版本号、tag 与 push 仍待拍板；`broker/fd/rebate-per-orders` 维持豁免（partner-only 文档尚未取得）。

## Comments

- 2026-11-06 由 09 的结论拆出；逐条证据见 `issues/09-unlisted-paths-research.md`。

# 09 · 官方已公布限额的端点清单与 274/135 差异核对（research findings）

调查快照日期：**2026-11-06**（官方页面当次抓取，见「取证方法与来源」）。
工单：[09 · 官方已公布限额的端点清单与 274/135 差异核对](../issues/09-official-limit-endpoint-list.md)。
性质：AFK research，**只铺事实、不下结论**。该不该补全表、补全到什么程度、表条目什么形状、清单以后怎么维护，均不在本文范围（归 03、08、10）。
上游已定事实（引用，不重复查证）：01 确认官方无集中限额表、数值分散在各端点详情 `Rate Limit:` / `Rate limit rule:` 行，一条限额 = `(请求数, 时间窗, 计数维度)`，窗口不统一、计数维度多样、现有 8 条数值全部对上；03 定覆盖验收线为「官方已公布限额且与项目路径常量对应的端点」，不以 274 为分母；08 定表保持二元组 + `path` 单键，本清单是计数维度 / 窗口语义 / 多方法 / REST-WS 共享等官方事实在图内的唯一载体；10 定本清单是一次性事实输入、留在 throwaway 分支、永不合并、不 push。

---

## 取证方法与来源（均为 OKX 官方一手页面，无二手转述 / 镜像站）

`app.okx.com/docs-v5/en` 是单页应用，WebFetch 每次只能返回前约 15000 字符（全是目录），端点正文取不到（与 01 的经验一致）。因此对**同一批官方 URL** 用 `curl` 抓取完整 HTML，转成纯文本后以脚本把「限额值 ↔ 端点路径」逐一绑定（详见「逐条核验方法」）。本次抓取均为 HTTP 200。

| 代号 | 官方 URL | 当次抓取大小 | 本文用途 |
|---|---|---|---|
| **S1** | <https://www.okx.com/docs-v5/en/> | 5,280,641 B ≈ 5.28 MB | **英文完整版主文档，本文清单主体** |
| **S2** | <https://www.okx.com/docs-v5/zh/> | 4,987,402 B ≈ 4.99 MB | 中文完整版，交叉验证（限速/限速规则写法与数值） |
| **S3** | <https://app.okx.com/docs-v5/en/> | 2,588,051 B ≈ 2.59 MB | 01 的 S1；**只覆盖 10 个业务段**，是 S1 的子集 |
| **S4** | <https://app.okx.com/docs-v5/zh/> | 2,010,042 B ≈ 2.01 MB | 01 的 S2 对应页面 |
| **S5** | <https://www.okx.com/docs-v5/log_en/> | 1,194,560 B ≈ 1.19 MB | 官方 Change Log（英文完整），日期锚点与变更条目 |
| **S6** | <https://app.okx.com/docs-v5/log_en/> | 154,514 B ≈ 154 KB | Change Log 精简页 |

**本文最重要的一条取证发现：两个 host 的 `/docs-v5/en/` 不是同一份内容。** 01 取证的 **S3（`app.okx.com`）只有 135 个 distinct REST 路径 / 141 个端点声明 / 10 个业务段**；而 **S1（`www.okx.com`）是完整版，有 386 个 distinct REST 路径 / 395 个端点声明 / 16 个业务段**（含 `finance`、`tradingBot`、`rfq`、`rubik`、`sprd`、`copytrading` 等 S3 完全没有的段）。逐条比对确认：

- S3 的 135 个路径 **全部**出现在 S1 里（差集 `S3 - S1 = 0`），且这 135 个共同路径在 S1 与 S3 的**限额数值零差异**；
- 因此 S1 是同一套官方文档的更全版本，不是另一套数值；01 的 `135 / 141 / 137` 三个统计数在 S3 上本次全部复现（137 = `Rate Limit:` 标准写法标注数，141 = 不区分大小写的 `HTTP Request`/`HTTP request` 块数，135 = 全文 distinct `/api/v5/...` 路径串数）；
- 09 工单里提到的「135」是 **S3 口径**；下文同时给出 **S1（完整版）口径**与 **S3（01 口径）**两套对齐数字，并明确标注各自来源。

**逐条核验方法（可复现）**：S1/S3 的每个 REST 端点在 HTML 里是一段端点块（多数以 `<h3>` 开头，Status / Announcements 等少数以 `<h2>` 或无独立标题开头），内含固定顺序的 `<h4>` 行——`Rate Limit:`（或 `Rate limit:` / 全角 `Rate limit：`）值行、`Rate limit rule:` 计数维度行、`HTTP Request`/`HTTP request` 声明行，随后 `<p><code>METHOD /api/v5/...</code></p>`。按 `...-http-request` 这个 h4 的 `id` 前缀把同一端点的值行 / 维度行 / 特例行归组，再与声明的 `method + path` 绑定；对全部值行写法做大小写与全角冒号容错。最后与全局 `Rate Limit` 类 h4 总数对账，确保无重复、无遗漏。

**未采信 / 排除**：`www.oyuzh.net`、`www.okx.vote`、`www.okx.ac`、`www.okcoin.com`、`greatapis.com`、`datawallet.com`、CSDN、GitHub 第三方调研等镜像或二手转述，均未作为任何结论来源。S1/S2 与 S3/S4 同为 `okx.com` 官方域。

---

## 1. 带 `Rate Limit:` 标注的端点路径清单

### 1.1 取证范围与快照

- 快照日期 **2026-11-06**；来源 **S1 <https://www.okx.com/docs-v5/en/>**（完整版英文主文档），中文 **S2** 交叉验证。
- S1 当次全文：**395 个 REST 端点声明**（`HTTP Request`/`HTTP request` 块）、**386 个 distinct REST 路径**、**408 条限额值行**（含 WS）、**406 条计数维度行**。
- 408 条值行的去向（已逐一绑定、对账闭合）：**397 条**归 395 个 REST 声明（其中 2 个端点各有 2 条值行 → 397，见 1.4），**11 条**归 WebSocket 端点（7 个 order-book WS + 4 个 spread-trading WS，非 REST 路径，见 1.6）。
- **395 个 REST 声明每一个都带至少一条限额值行**（`WITHOUT limit = 0`）；**394 个带至少一条 `Rate limit rule` 计数维度行**，唯一例外见 1.5。
- 值行写法并不统一。397 条 REST 值行中 **341 条** `Rate Limit:`、**44 条** `Rate limit:`（小写 l）、**12 条** `Rate limit：`（全角冒号 `：`）；另有 11 条 WS 值行（均为 `Rate Limit:` 标准写法），全文合计 408 条。01 的「137 处 `Rate Limit:`」只数了 S3 口径下的标准写法（详见问题 5）。
- 中文 S2 当次：381 个 distinct 路径、16 个业务段、`限速：` 389 处 + `限速:` 20 处、`限速规则` 424 处；比英文少 5 个路径，未逐一比对原因（见「覆盖范围与未查到的部分」）。

### 1.2 完整清单（395 个 REST 端点声明，逐条列全）

列含义：**路径** / **方法** / **限额数值（原文）** / **时间窗** / **计数维度 `Rate limit rule`（原文）** / **值行写法** / **与项目常量对齐** / **来源页锚点**（S1 该端点自己的 `...-http-request` h4 id）。同一路径多个方法分行列出，便于看「多方法区分」。

> 说明：来源页锚点取各端点自己的 `...-http-request` h4 id（该 id 在 S1 页面真实存在）。S1 中 Status / Announcements / 部分 Sub-account 端点的这一 id 被文档生成器错误地插入了 `get-the-invitee-39-s-detail` 中缀（例：`status-get-status-get-the-invitee-39-s-detail-http-request`），是官方页面 HTML 的 id 生成瑕疵，**不影响正文数值**；定位时以「端点标题 + 路径」为准。


| # | 路径 | 方法 | 限额数值（S1 原文） | 时间窗 | 计数维度 `Rate limit rule` | 值行写法 | 对齐 | 来源页锚点 |
|---:|---|---|---|---|---|---|---|---|
| 1 | `/api/v5/account/account-level-switch-preset` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-preset-account-mode-switch-http-request` |
| 2 | `/api/v5/account/account-position-risk` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-account-and-position-risk-http-request` |
| 3 | `/api/v5/account/activate-feature` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-activate-feature-http-request` |
| 4 | `/api/v5/account/activate-option` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-activate-option-http-request` |
| 5 | `/api/v5/account/adjust-leverage-info` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-leverage-estimated-info-http-request` |
| 6 | `/api/v5/account/balance` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-balance-http-request` |
| 7 | `/api/v5/account/bills` | GET | 5 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-bills-details-last-7-days-http-request` |
| 8 | `/api/v5/account/bills-archive` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-bills-details-last-3-months-http-request` |
| 9 | `/api/v5/account/bills-history-archive` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-bills-details-since-2021-http-request` |
| 10 | `/api/v5/account/bills-history-archive` | POST | 12 requests per day | day | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-apply-bills-details-since-2021-http-request` |
| 11 | `/api/v5/account/collateral-assets` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-collateral-assets-http-request` |
| 12 | `/api/v5/account/config` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-account-configuration-http-request` |
| 13 | `/api/v5/account/demo-adjust-balance` | POST | Increase — 3 requests per user per day (resets at UTC 0:00). Reduce — no limit. | user per day | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-adjust-demo-account-balance-http-request` |
| 14 | `/api/v5/account/greeks` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-greeks-http-request` |
| 15 | `/api/v5/account/instruments` | GET | 20 requests per 2 seconds | 2 seconds | User ID + Instrument Type | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-instruments-http-request` |
| 16 | `/api/v5/account/interest-accrued` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-interest-accrued-data-http-request` |
| 17 | `/api/v5/account/interest-limits` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-borrow-interest-and-limit-http-request` |
| 18 | `/api/v5/account/interest-rate` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-interest-rate-http-request` |
| 19 | `/api/v5/account/leverage-info` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-leverage-http-request` |
| 20 | `/api/v5/account/max-avail-size` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-maximum-available-balance-equity-http-request` |
| 21 | `/api/v5/account/max-loan` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-the-maximum-loan-of-instrument-http-request` |
| 22 | `/api/v5/account/max-size` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-maximum-order-quantity-http-request` |
| 23 | `/api/v5/account/max-withdrawal` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-maximum-withdrawals-http-request` |
| 24 | `/api/v5/account/mmp-config` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-mmp-config-http-request` |
| 25 | `/api/v5/account/mmp-config` | POST | 2 requests per 10 seconds | 10 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-set-mmp-http-request` |
| 26 | `/api/v5/account/mmp-reset` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-reset-mmp-status-http-request` |
| 27 | `/api/v5/account/move-positions` | POST | 1 request per second | second | Master account User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-move-positions-http-request` |
| 28 | `/api/v5/account/move-positions-history` | GET | 2 requests per 2 seconds | 2 seconds | Master account UserID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-get-move-positions-history-http-request` |
| 29 | `/api/v5/account/position-builder` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-position-builder-new-http-request` |
| 30 | `/api/v5/account/position-builder-graph` | POST | 1 request per 5 seconds | 5 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-position-builder-trend-graph-http-request` |
| 31 | `/api/v5/account/position-tiers` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-pm-position-limitation-http-request` |
| 32 | `/api/v5/account/position/margin-balance` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-increase-decrease-margin-http-request` |
| 33 | `/api/v5/account/positions` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-positions-http-request` |
| 34 | `/api/v5/account/positions-history` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-positions-history-http-request` |
| 35 | `/api/v5/account/precheck-set-delta-neutral` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#trading-account-rest-api-precheck-set-delta-neutral-http-request` |
| 36 | `/api/v5/account/risk-state` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-account-risk-state-http-request` |
| 37 | `/api/v5/account/set-account-level` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-set-account-mode-http-request` |
| 38 | `/api/v5/account/set-account-switch-precheck` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-precheck-account-mode-switch-http-request` |
| 39 | `/api/v5/account/set-auto-earn` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#trading-account-rest-api-set-auto-earn-http-request` |
| 40 | `/api/v5/account/set-auto-loan` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-set-auto-loan-http-request` |
| 41 | `/api/v5/account/set-auto-repay` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-set-auto-repay-http-request` |
| 42 | `/api/v5/account/set-collateral-assets` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-set-collateral-assets-http-request` |
| 43 | `/api/v5/account/set-fee-type` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-set-fee-type-http-request` |
| 44 | `/api/v5/account/set-greeks` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-set-greeks-pa-bs-http-request` |
| 45 | `/api/v5/account/set-isolated-mode` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-isolated-margin-trading-settings-http-request` |
| 46 | `/api/v5/account/set-leverage` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#trading-account-rest-api-set-leverage-http-request` |
| 47 | `/api/v5/account/set-position-mode` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-set-position-mode-http-request` |
| 48 | `/api/v5/account/set-riskOffset-amt` | POST | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-set-risk-offset-amount-http-request` |
| 49 | `/api/v5/account/set-settle-currency` | POST | 20 times per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#trading-account-rest-api-set-settle-currency-http-request` |
| 50 | `/api/v5/account/set-trading-config` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#trading-account-rest-api-set-trading-config-http-request` |
| 51 | `/api/v5/account/spot-borrow-repay-history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-borrow-repay-history-http-request` |
| 52 | `/api/v5/account/spot-manual-borrow-repay` | POST | 1 request per 3 seconds | 3 seconds | Master Account User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-manual-borrow-repay-http-request` |
| 53 | `/api/v5/account/subaccount/balances` | GET | 6 requests per 2 seconds | 2 seconds | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-get-sub-account-trading-balance-http-request` |
| 54 | `/api/v5/account/subaccount/max-withdrawal` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#sub-account-rest-api-get-sub-account-maximum-withdrawals-http-request` |
| 55 | `/api/v5/account/subtypes` | GET | 20 requests per 2 seconds | 2 seconds | UserId | Rate limit:（小写 l） | 两侧都有 | `#trading-account-rest-api-get-bill-types-http-request` |
| 56 | `/api/v5/account/trade-fee` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-fee-rates-http-request` |
| 57 | `/api/v5/affiliate/co-inviter/list` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-co-inviter-link-list-http-request` |
| 58 | `/api/v5/affiliate/invitee/detail` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-the-invitee-39-s-detail-http-request` |
| 59 | `/api/v5/affiliate/invitee/list` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-invitee-list-http-request` |
| 60 | `/api/v5/affiliate/link/list` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-link-list-http-request` |
| 61 | `/api/v5/affiliate/performance/summary` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-performance-summary-http-request` |
| 62 | `/api/v5/affiliate/sub-affiliate/list` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#affiliate-rest-api-get-sub-affiliate-list-http-request` |
| 63 | `/api/v5/asset/asset-valuation` | GET | 1 request per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-account-asset-valuation-http-request` |
| 64 | `/api/v5/asset/balances` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-balance-http-request` |
| 65 | `/api/v5/asset/bills` | GET | 6 Requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-asset-bills-details-http-request` |
| 66 | `/api/v5/asset/bills-history` | GET | 1 Requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-asset-bills-history-http-request` |
| 67 | `/api/v5/asset/cancel-withdrawal` | POST | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-cancel-withdrawal-http-request` |
| 68 | `/api/v5/asset/convert/currencies` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-convert-currencies-http-request` |
| 69 | `/api/v5/asset/convert/currency-pair` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-convert-currency-pair-http-request` |
| 70 | `/api/v5/asset/convert/estimate-quote` | POST | 10 requests per second ; 1 request per 5 seconds | second ; 5 seconds | User ID ; Instrument ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-estimate-quote-http-request` |
| 71 | `/api/v5/asset/convert/history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-convert-history-http-request` |
| 72 | `/api/v5/asset/convert/trade` | POST | 10 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-convert-trade-http-request` |
| 73 | `/api/v5/asset/currencies` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-currencies-http-request` |
| 74 | `/api/v5/asset/deposit-address` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-deposit-address-http-request` |
| 75 | `/api/v5/asset/deposit-history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-deposit-history-http-request` |
| 76 | `/api/v5/asset/deposit-withdraw-status` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-deposit-withdraw-status-http-request` |
| 77 | `/api/v5/asset/exchange-list` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-exchange-list-public-http-request` |
| 78 | `/api/v5/asset/monthly-statement` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-monthly-statement-last-year-http-request` |
| 79 | `/api/v5/asset/monthly-statement` | POST | 20 requests per month | month | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-apply-for-monthly-statement-last-year-http-request` |
| 80 | `/api/v5/asset/non-tradable-assets` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-non-tradable-assets-http-request` |
| 81 | `/api/v5/asset/subaccount/balances` | GET | 6 requests per 2 seconds | 2 seconds | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-get-sub-account-funding-balance-http-request` |
| 82 | `/api/v5/asset/subaccount/bills` | GET | 6 requests per second | second | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-get-history-of-sub-account-transfer-http-request` |
| 83 | `/api/v5/asset/subaccount/managed-subaccount-bills` | GET | 6 requests per second | second | User ID | Rate limit：（全角冒号） | 仅官方有 | `#sub-account-rest-api-get-history-of-managed-sub-account-transfer-http-request` |
| 84 | `/api/v5/asset/subaccount/transfer` | POST | 1 request per second | second | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-master-accounts-manage-the-transfers-between-sub-accounts-http-request` |
| 85 | `/api/v5/asset/transfer` | POST | 2 requests per second | second | User ID + Currency | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-funds-transfer-http-request` |
| 86 | `/api/v5/asset/transfer-state` | GET | 10 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-funds-transfer-state-http-request` |
| 87 | `/api/v5/asset/withdrawal` | POST | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-withdrawal-http-request` |
| 88 | `/api/v5/asset/withdrawal-history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#funding-account-rest-api-get-withdrawal-history-http-request` |
| 89 | `/api/v5/copytrading/algo-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-post-place-lead-stop-order-http-request` |
| 90 | `/api/v5/copytrading/amend-copy-settings` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-post-amend-copy-settings-http-request` |
| 91 | `/api/v5/copytrading/amend-profit-sharing-ratio` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-post-amend-profit-sharing-ratio-http-request` |
| 92 | `/api/v5/copytrading/close-subposition` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-post-close-lead-position-http-request` |
| 93 | `/api/v5/copytrading/config` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-account-configuration-http-request` |
| 94 | `/api/v5/copytrading/copy-settings` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-copy-settings-http-request` |
| 95 | `/api/v5/copytrading/current-lead-traders` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-my-lead-traders-http-request` |
| 96 | `/api/v5/copytrading/current-subpositions` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-existing-lead-positions-http-request` |
| 97 | `/api/v5/copytrading/first-copy-settings` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-post-first-copy-settings-http-request` |
| 98 | `/api/v5/copytrading/instruments` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-leading-instruments-http-request` |
| 99 | `/api/v5/copytrading/profit-sharing-details` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-profit-sharing-details-http-request` |
| 100 | `/api/v5/copytrading/public-config` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-copy-trading-configuration-http-request` |
| 101 | `/api/v5/copytrading/public-copy-traders` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-copy-traders-http-request` |
| 102 | `/api/v5/copytrading/public-current-subpositions` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-current-lead-positions-http-request` |
| 103 | `/api/v5/copytrading/public-lead-traders` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-ranks-http-request` |
| 104 | `/api/v5/copytrading/public-pnl` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-daily-pnl-http-request` |
| 105 | `/api/v5/copytrading/public-preference-currency` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-currency-preferences-http-request` |
| 106 | `/api/v5/copytrading/public-stats` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-stats-http-request` |
| 107 | `/api/v5/copytrading/public-subpositions-history` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-lead-position-history-http-request` |
| 108 | `/api/v5/copytrading/public-weekly-pnl` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-lead-trader-weekly-pnl-http-request` |
| 109 | `/api/v5/copytrading/set-instruments` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-post-amend-leading-instruments-http-request` |
| 110 | `/api/v5/copytrading/stop-copy-trading` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-post-stop-copying-http-request` |
| 111 | `/api/v5/copytrading/subpositions-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-lead-position-history-http-request` |
| 112 | `/api/v5/copytrading/total-profit-sharing` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-total-profit-sharing-http-request` |
| 113 | `/api/v5/copytrading/total-unrealized-profit-sharing` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 仅官方有 | `#order-book-trading-copy-trading-get-total-unrealized-profit-sharing-http-request` |
| 114 | `/api/v5/copytrading/unrealized-profit-sharing-details` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate limit:（小写 l） | 两侧都有 | `#order-book-trading-copy-trading-get-unrealized-profit-sharing-details-http-request` |
| 115 | `/api/v5/fiat/buy-sell/currencies` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-buy-sell-currencies-http-request` |
| 116 | `/api/v5/fiat/buy-sell/currency-pair` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-buy-sell-currency-pair-http-request` |
| 117 | `/api/v5/fiat/buy-sell/history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-buy-sell-trade-history-http-request` |
| 118 | `/api/v5/fiat/buy-sell/quote` | POST | 10 requests per second ; 1 request per 5 seconds | second ; 5 seconds | User ID ; Instrument ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-buy-sell-quote-http-request` |
| 119 | `/api/v5/fiat/buy-sell/trade` | POST | 1 request per 5 seconds | 5 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-buy-sell-trade-http-request` |
| 120 | `/api/v5/fiat/cancel-withdrawal` | POST | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-cancel-withdrawal-order-http-request` |
| 121 | `/api/v5/fiat/create-withdrawal` | POST | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-create-withdrawal-order-http-request` |
| 122 | `/api/v5/fiat/deposit` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-deposit-order-detail-http-request` |
| 123 | `/api/v5/fiat/deposit-order-history` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-deposit-order-history-http-request` |
| 124 | `/api/v5/fiat/deposit-payment-methods` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-deposit-payment-methods-http-request` |
| 125 | `/api/v5/fiat/withdrawal` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-withdrawal-order-detail-http-request` |
| 126 | `/api/v5/fiat/withdrawal-order-history` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-withdrawal-order-history-http-request` |
| 127 | `/api/v5/fiat/withdrawal-payment-methods` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#funding-account-rest-api-get-withdrawal-payment-methods-http-request` |
| 128 | `/api/v5/finance/flexible-loan/adjust-collateral` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-post-adjust-collateral-http-request` |
| 129 | `/api/v5/finance/flexible-loan/borrow` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-post-borrow-http-request` |
| 130 | `/api/v5/finance/flexible-loan/borrow-currencies` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-borrowable-currencies-http-request` |
| 131 | `/api/v5/finance/flexible-loan/collateral-assets` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-collateral-assets-http-request` |
| 132 | `/api/v5/finance/flexible-loan/emode-info` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-e-mode-info-http-request` |
| 133 | `/api/v5/finance/flexible-loan/interest-accrued` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-accrued-interest-http-request` |
| 134 | `/api/v5/finance/flexible-loan/loan-history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-loan-history-http-request` |
| 135 | `/api/v5/finance/flexible-loan/loan-info` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-loan-info-http-request` |
| 136 | `/api/v5/finance/flexible-loan/max-collateral-redeem-amount` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-get-maximum-collateral-redeem-amount-http-request` |
| 137 | `/api/v5/finance/flexible-loan/max-loan` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-post-maximum-loan-amount-http-request` |
| 138 | `/api/v5/finance/flexible-loan/repay` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-flexible-loan-post-repay-http-request` |
| 139 | `/api/v5/finance/okusd/account` | GET | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-okusd-get-get-okusd-account-http-request` |
| 140 | `/api/v5/finance/okusd/limits` | GET | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#financial-product-okusd-get-okusd-limits-http-request` |
| 141 | `/api/v5/finance/okusd/rate/history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-okusd-get-get-apr-history-http-request` |
| 142 | `/api/v5/finance/okusd/redeem` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#financial-product-okusd-post-redeem-okusd-http-request` |
| 143 | `/api/v5/finance/okusd/redeem/history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-okusd-get-get-redemption-history-http-request` |
| 144 | `/api/v5/finance/okusd/rewards/history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-okusd-get-get-rewards-history-http-request` |
| 145 | `/api/v5/finance/okusd/subscribe` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#financial-product-okusd-post-subscribe-okusd-http-request` |
| 146 | `/api/v5/finance/okusd/subscribe/history` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-okusd-get-get-subscription-history-http-request` |
| 147 | `/api/v5/finance/savings/balance` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-simple-earn-flexible-get-saving-balance-http-request` |
| 148 | `/api/v5/finance/savings/lending-history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-simple-earn-flexible-get-lending-history-http-request` |
| 149 | `/api/v5/finance/savings/lending-rate-history` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 两侧都有 | `#financial-product-simple-earn-flexible-get-public-borrow-history-public-http-request` |
| 150 | `/api/v5/finance/savings/lending-rate-summary` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 两侧都有 | `#financial-product-simple-earn-flexible-get-public-borrow-info-public-http-request` |
| 151 | `/api/v5/finance/savings/purchase-redempt` | POST | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-simple-earn-flexible-post-savings-purchase-redemption-http-request` |
| 152 | `/api/v5/finance/sfp/dcd/currency-pair` | GET | 1 request per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-get-currency-pairs-http-request` |
| 153 | `/api/v5/finance/sfp/dcd/order-history` | GET | 1 request per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-get-order-history-http-request` |
| 154 | `/api/v5/finance/sfp/dcd/order-status` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-get-order-state-http-request` |
| 155 | `/api/v5/finance/sfp/dcd/products` | GET | 1 request per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-get-product-info-http-request` |
| 156 | `/api/v5/finance/sfp/dcd/quote` | POST | 10 requests per 60 seconds | 60 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-post-request-for-quote-http-request` |
| 157 | `/api/v5/finance/sfp/dcd/redeem` | POST | 2 requests per 60 seconds | 60 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-post-redeem-http-request` |
| 158 | `/api/v5/finance/sfp/dcd/redeem-quote` | POST | 10 requests per 60 seconds | 60 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-post-request-for-redeem-quote-http-request` |
| 159 | `/api/v5/finance/sfp/dcd/trade` | POST | 2 requests per 60 seconds | 60 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-dual-investment-post-trade-http-request` |
| 160 | `/api/v5/finance/stable-rewards/apy-history` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 仅官方有 | `#financial-product-stable-rewards-get-apy-history-http-request` |
| 161 | `/api/v5/finance/stable-rewards/balance` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#financial-product-stable-rewards-get-balance-http-request` |
| 162 | `/api/v5/finance/stable-rewards/product-info` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#financial-product-stable-rewards-get-product-info-http-request` |
| 163 | `/api/v5/finance/staking-defi/cancel` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-post-cancel-purchases-redemptions-http-request` |
| 164 | `/api/v5/finance/staking-defi/eth/apy-history` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-get-apy-history-public-http-request` |
| 165 | `/api/v5/finance/staking-defi/eth/balance` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-get-balance-http-request` |
| 166 | `/api/v5/finance/staking-defi/eth/cancel-redeem` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-post-cancel-redeem-http-request` |
| 167 | `/api/v5/finance/staking-defi/eth/product-info` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-get-product-info-http-request` |
| 168 | `/api/v5/finance/staking-defi/eth/purchase` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-post-purchase-http-request` |
| 169 | `/api/v5/finance/staking-defi/eth/purchase-redeem-history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-get-purchase-amp-redeem-history-http-request` |
| 170 | `/api/v5/finance/staking-defi/eth/redeem` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-eth-staking-post-redeem-http-request` |
| 171 | `/api/v5/finance/staking-defi/offers` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-get-offers-http-request` |
| 172 | `/api/v5/finance/staking-defi/orders-active` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-get-active-orders-http-request` |
| 173 | `/api/v5/finance/staking-defi/orders-history` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-get-order-history-http-request` |
| 174 | `/api/v5/finance/staking-defi/purchase` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-post-purchase-http-request` |
| 175 | `/api/v5/finance/staking-defi/redeem` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-on-chain-earn-post-redeem-http-request` |
| 176 | `/api/v5/finance/staking-defi/sol/apy-history` | GET | 6 requests per second | second | IP | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-get-apy-history-public-http-request` |
| 177 | `/api/v5/finance/staking-defi/sol/balance` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-get-balance-http-request` |
| 178 | `/api/v5/finance/staking-defi/sol/product-info` | GET | 3 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-get-product-info-http-request` |
| 179 | `/api/v5/finance/staking-defi/sol/purchase` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-post-purchase-http-request` |
| 180 | `/api/v5/finance/staking-defi/sol/purchase-redeem-history` | GET | 6 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-get-purchase-amp-redeem-history-http-request` |
| 181 | `/api/v5/finance/staking-defi/sol/redeem` | POST | 2 requests per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#financial-product-sol-staking-post-redeem-http-request` |
| 182 | `/api/v5/market/block-ticker` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-block-ticker-http-request` |
| 183 | `/api/v5/market/block-tickers` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-block-tickers-http-request` |
| 184 | `/api/v5/market/books` | GET | 40 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-order-book-http-request` |
| 185 | `/api/v5/market/books-full` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-market-data-get-full-order-book-http-request` |
| 186 | `/api/v5/market/books-rpi` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-rpi-order-book-http-request` |
| 187 | `/api/v5/market/books-sbe` | GET | 10 requests per 10 seconds | 10 seconds | IP + instIdCode | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-sbe-market-data-sbe-order-book-http-request` |
| 188 | `/api/v5/market/call-auction-details` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-market-data-get-call-auction-details-http-request` |
| 189 | `/api/v5/market/candles` | GET | 40 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-candlesticks-http-request` |
| 190 | `/api/v5/market/exchange-rate` | GET | 1 request per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-exchange-rate-http-request` |
| 191 | `/api/v5/market/history-candles` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-candlesticks-history-http-request` |
| 192 | `/api/v5/market/history-index-candles` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-index-candlesticks-history-http-request` |
| 193 | `/api/v5/market/history-mark-price-candles` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-mark-price-candlesticks-history-http-request` |
| 194 | `/api/v5/market/history-trades` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-trades-history-http-request` |
| 195 | `/api/v5/market/index-candles` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-index-candlesticks-http-request` |
| 196 | `/api/v5/market/index-components` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-index-components-http-request` |
| 197 | `/api/v5/market/index-tickers` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-index-tickers-http-request` |
| 198 | `/api/v5/market/mark-price-candles` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-mark-price-candlesticks-http-request` |
| 199 | `/api/v5/market/option/instrument-family-trades` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-option-trades-by-instrument-family-http-request` |
| 200 | `/api/v5/market/platform-24-volume` | GET | 2 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-24h-total-volume-http-request` |
| 201 | `/api/v5/market/sprd-candles` | GET | 40 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-get-candlesticks-http-request` |
| 202 | `/api/v5/market/sprd-history-candles` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-get-candlesticks-history-http-request` |
| 203 | `/api/v5/market/sprd-ticker` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-get-ticker-public-http-request` |
| 204 | `/api/v5/market/ticker` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-ticker-http-request` |
| 205 | `/api/v5/market/tickers` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-tickers-http-request` |
| 206 | `/api/v5/market/trades` | GET | 100 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-trades-http-request` |
| 207 | `/api/v5/public/block-trades` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#block-trading-rest-api-get-public-single-leg-transactions-of-block-trades-http-request` |
| 208 | `/api/v5/public/convert-contract-coin` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-unit-convert-http-request` |
| 209 | `/api/v5/public/delivery-exercise-history` | GET | 40 requests per 2 seconds | 2 seconds | IP + (Instrument Type + instFamily) | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-delivery-exercise-history-http-request` |
| 210 | `/api/v5/public/delta-hedge-currencies` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-delta-hedge-currencies-http-request` |
| 211 | `/api/v5/public/discount-rate-interest-free-quota` | GET | 2 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-discount-rate-and-interest-free-quota-http-request` |
| 212 | `/api/v5/public/economic-calendar` | GET | 1 request per 5 seconds | 5 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-economic-calendar-data-http-request` |
| 213 | `/api/v5/public/estimated-price` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-estimated-delivery-exercise-price-http-request` |
| 214 | `/api/v5/public/estimated-settlement-info` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-estimated-future-settlement-price-http-request` |
| 215 | `/api/v5/public/event-contract/events` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-events-http-request` |
| 216 | `/api/v5/public/event-contract/markets` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-markets-http-request` |
| 217 | `/api/v5/public/event-contract/series` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-series-http-request` |
| 218 | `/api/v5/public/funding-rate` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-funding-rate-http-request` |
| 219 | `/api/v5/public/funding-rate-history` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-funding-rate-history-http-request` |
| 220 | `/api/v5/public/instrument-tick-bands` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-instrument-tick-bands-http-request` |
| 221 | `/api/v5/public/instruments` | GET | 20 requests per 2 seconds | 2 seconds | IP + Instrument Type | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-instruments-http-request` |
| 222 | `/api/v5/public/insurance-fund` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-security-fund-http-request` |
| 223 | `/api/v5/public/interest-rate-loan-quota` | GET | 2 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-interest-rate-and-loan-quota-http-request` |
| 224 | `/api/v5/public/mark-price` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-mark-price-http-request` |
| 225 | `/api/v5/public/market-data-history` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-historical-market-data-http-request` |
| 226 | `/api/v5/public/mm-instrument-types` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-mm-instrument-types-http-request` |
| 227 | `/api/v5/public/open-interest` | GET | 20 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-open-interest-http-request` |
| 228 | `/api/v5/public/opt-summary` | GET | 20 requests per 2 seconds | 2 seconds | IP + instFamily | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-option-market-data-http-request` |
| 229 | `/api/v5/public/option-trades` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-market-data-get-option-trades-http-request` |
| 230 | `/api/v5/public/position-tiers` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-position-tiers-http-request` |
| 231 | `/api/v5/public/premium-history` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-premium-history-http-request` |
| 232 | `/api/v5/public/price-limit` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-limit-price-http-request` |
| 233 | `/api/v5/public/settlement-history` | GET | 40 requests per 2 seconds | 2 seconds | IP + (Instrument Family) | Rate Limit:（标准） | 仅官方有 | `#public-data-rest-api-get-futures-settlement-history-http-request` |
| 234 | `/api/v5/public/time` | GET | 10 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-system-time-http-request` |
| 235 | `/api/v5/public/underlying` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#public-data-rest-api-get-underlying-http-request` |
| 236 | `/api/v5/rfq/cancel-all-after` | POST | 1 request per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#block-trading-rest-api-cancel-all-after-http-request` |
| 237 | `/api/v5/rfq/cancel-all-quotes` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-all-quotes-http-request` |
| 238 | `/api/v5/rfq/cancel-all-rfqs` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-all-rfqs-http-request` |
| 239 | `/api/v5/rfq/cancel-batch-quotes` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-multiple-quotes-http-request` |
| 240 | `/api/v5/rfq/cancel-batch-rfqs` | POST | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-multiple-rfqs-http-request` |
| 241 | `/api/v5/rfq/cancel-quote` | POST | 50 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-quote-http-request` |
| 242 | `/api/v5/rfq/cancel-rfq` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-cancel-rfq-http-request` |
| 243 | `/api/v5/rfq/counterparties` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-counterparties-http-request` |
| 244 | `/api/v5/rfq/create-quote` | POST | 50 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-create-quote-http-request` |
| 245 | `/api/v5/rfq/create-rfq` | POST | 5 requests per 2 seconds; 80 requests per 12 hours | 12 hours | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-create-rfq-http-request` |
| 246 | `/api/v5/rfq/execute-quote` | POST | 2 requests per 3 seconds | 3 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-execute-quote-http-request` |
| 247 | `/api/v5/rfq/maker-instrument-settings` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-quote-products-http-request` |
| 248 | `/api/v5/rfq/maker-instrument-settings` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-set-quote-products-http-request` |
| 249 | `/api/v5/rfq/mmp-config` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#block-trading-rest-api-get-mmp-config-http-request` |
| 250 | `/api/v5/rfq/mmp-config` | POST | 1 request per 10 seconds | 10 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#block-trading-rest-api-set-mmp-http-request` |
| 251 | `/api/v5/rfq/mmp-reset` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-reset-mmp-status-http-request` |
| 252 | `/api/v5/rfq/public-trades` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-public-multi-leg-transactions-of-block-trades-http-request` |
| 253 | `/api/v5/rfq/quotes` | GET | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-quotes-http-request` |
| 254 | `/api/v5/rfq/rfqs` | GET | 2 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-rfqs-http-request` |
| 255 | `/api/v5/rfq/trades` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#block-trading-rest-api-get-trades-http-request` |
| 256 | `/api/v5/rubik/stat/contracts/long-short-account-ratio` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-long-short-ratio-http-request` |
| 257 | `/api/v5/rubik/stat/contracts/long-short-account-ratio-contract` | GET | 5 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate limit:（小写 l） | 仅官方有 | `#trading-statistics-rest-api-get-contract-long-short-ratio-http-request` |
| 258 | `/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader` | GET | 5 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate limit:（小写 l） | 仅官方有 | `#trading-statistics-rest-api-get-top-traders-contract-long-short-ratio-http-request` |
| 259 | `/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader` | GET | 5 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate limit:（小写 l） | 仅官方有 | `#trading-statistics-rest-api-get-top-traders-contract-long-short-ratio-by-position-http-request` |
| 260 | `/api/v5/rubik/stat/contracts/open-interest-history` | GET | 10 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate limit:（小写 l） | 两侧都有 | `#trading-statistics-rest-api-get-contract-open-interest-history-http-request` |
| 261 | `/api/v5/rubik/stat/contracts/open-interest-volume` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-contracts-open-interest-and-volume-http-request` |
| 262 | `/api/v5/rubik/stat/margin/loan-ratio` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-margin-long-short-ratio-http-request` |
| 263 | `/api/v5/rubik/stat/option/open-interest-volume` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-options-open-interest-and-volume-http-request` |
| 264 | `/api/v5/rubik/stat/option/open-interest-volume-expiry` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-open-interest-and-volume-expiry-http-request` |
| 265 | `/api/v5/rubik/stat/option/open-interest-volume-ratio` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-put-call-ratio-http-request` |
| 266 | `/api/v5/rubik/stat/option/open-interest-volume-strike` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-open-interest-and-volume-strike-http-request` |
| 267 | `/api/v5/rubik/stat/option/taker-block-volume` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-taker-flow-http-request` |
| 268 | `/api/v5/rubik/stat/taker-volume` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-taker-volume-http-request` |
| 269 | `/api/v5/rubik/stat/taker-volume-contract` | GET | 5 requests per 2 seconds | 2 seconds | IP + Instrument ID | Rate limit:（小写 l） | 仅官方有 | `#trading-statistics-rest-api-get-contract-taker-volume-http-request` |
| 270 | `/api/v5/rubik/stat/trading-data/support-coin` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#trading-statistics-rest-api-get-support-coin-http-request` |
| 271 | `/api/v5/sprd/amend-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-amend-order-http-request` |
| 272 | `/api/v5/sprd/books` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-order-book-public-http-request` |
| 273 | `/api/v5/sprd/cancel-all-after` | POST | 1 request per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-cancel-all-after-http-request` |
| 274 | `/api/v5/sprd/cancel-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-cancel-order-http-request` |
| 275 | `/api/v5/sprd/mass-cancel` | POST | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-cancel-all-orders-http-request` |
| 276 | `/api/v5/sprd/order` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-order-details-http-request` |
| 277 | `/api/v5/sprd/order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-place-order-http-request` |
| 278 | `/api/v5/sprd/orders-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-orders-last-21-days-http-request` |
| 279 | `/api/v5/sprd/orders-history-archive` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#spread-trading-rest-api-get-orders-history-last-3-months-http-request` |
| 280 | `/api/v5/sprd/orders-pending` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-active-orders-http-request` |
| 281 | `/api/v5/sprd/public-trades` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-public-trades-public-http-request` |
| 282 | `/api/v5/sprd/spreads` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-spreads-public-http-request` |
| 283 | `/api/v5/sprd/trades` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#spread-trading-rest-api-get-trades-last-7-days-http-request` |
| 284 | `/api/v5/support/announcement-types` | GET | 1 request per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#announcement-get-announcement-types-get-sub-affiliate-list-http-request` |
| 285 | `/api/v5/support/announcements` | GET | 5 requests per 2 seconds | 2 seconds | User ID(Private) or IP(Public) | Rate Limit:（标准） | 两侧都有 | `#announcement-get-announcements-get-sub-affiliate-list-http-request` |
| 286 | `/api/v5/system/status` | GET | 1 request per 5 seconds | 5 seconds | （无此行） | Rate Limit:（标准） | 两侧都有 | `#status-get-status-get-sub-affiliate-list-http-request` |
| 287 | `/api/v5/trade/account-rate-limit` | GET | 1 request per second | second | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-trade-get-account-rate-limit-http-request` |
| 288 | `/api/v5/trade/amend-algos` | POST | 20 requests per 2 seconds | 2 seconds | User ID + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-post-amend-algo-order-http-request` |
| 289 | `/api/v5/trade/amend-batch-orders` | POST | 300 orders per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-amend-multiple-orders-http-request` |
| 290 | `/api/v5/trade/amend-order` | POST | 60 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-amend-order-http-request` |
| 291 | `/api/v5/trade/batch-orders` | POST | 300 orders per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-place-multiple-orders-http-request` |
| 292 | `/api/v5/trade/cancel-algos` | POST | 20 orders per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-post-cancel-algo-order-http-request` |
| 293 | `/api/v5/trade/cancel-all-after` | POST | 1 request per second | second | User ID + tag | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-trade-post-cancel-all-after-http-request` |
| 294 | `/api/v5/trade/cancel-batch-orders` | POST | 300 orders per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-cancel-multiple-orders-http-request` |
| 295 | `/api/v5/trade/cancel-order` | POST | 60 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-cancel-order-http-request` |
| 296 | `/api/v5/trade/close-position` | POST | 20 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-close-positions-http-request` |
| 297 | `/api/v5/trade/easy-convert` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-place-easy-convert-http-request` |
| 298 | `/api/v5/trade/easy-convert-currency-list` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-easy-convert-currency-list-http-request` |
| 299 | `/api/v5/trade/easy-convert-history` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-easy-convert-history-http-request` |
| 300 | `/api/v5/trade/fills` | GET | 60 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-transaction-details-last-3-days-http-request` |
| 301 | `/api/v5/trade/fills-history` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-transaction-details-last-3-months-http-request` |
| 302 | `/api/v5/trade/mass-cancel` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-trade-post-mass-cancel-order-http-request` |
| 303 | `/api/v5/trade/one-click-repay` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-trade-one-click-repay-http-request` |
| 304 | `/api/v5/trade/one-click-repay-currency-list` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-one-click-repay-currency-list-http-request` |
| 305 | `/api/v5/trade/one-click-repay-currency-list-v2` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-one-click-repay-currency-list-new-http-request` |
| 306 | `/api/v5/trade/one-click-repay-history` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-one-click-repay-history-http-request` |
| 307 | `/api/v5/trade/one-click-repay-history-v2` | GET | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-one-click-repay-history-new-http-request` |
| 308 | `/api/v5/trade/one-click-repay-v2` | POST | 1 request per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-trade-one-click-repay-new-http-request` |
| 309 | `/api/v5/trade/order` | GET | 60 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-order-details-http-request` |
| 310 | `/api/v5/trade/order` | POST | 60 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-post-place-order-http-request` |
| 311 | `/api/v5/trade/order-algo` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-get-algo-order-details-http-request` |
| 312 | `/api/v5/trade/order-algo` | POST | 20 requests per 2 seconds | 2 seconds | (except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-post-place-algo-order-http-request` |
| 313 | `/api/v5/trade/order-precheck` | POST | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-trade-post-order-precheck-http-request` |
| 314 | `/api/v5/trade/orders-algo-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-get-algo-order-history-http-request` |
| 315 | `/api/v5/trade/orders-algo-pending` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-algo-trading-get-algo-order-list-http-request` |
| 316 | `/api/v5/trade/orders-history` | GET | 40 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-order-history-last-7-days-http-request` |
| 317 | `/api/v5/trade/orders-history-archive` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-order-history-last-3-months-http-request` |
| 318 | `/api/v5/trade/orders-pending` | GET | 60 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-trade-get-order-list-http-request` |
| 319 | `/api/v5/tradingBot/dca/amend-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-amend-spot-dca-basic-param-http-request` |
| 320 | `/api/v5/tradingBot/dca/create` | POST | 20 requests per 2 seconds | 2 seconds | User ID + Instrument ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-place-dca-algo-order-http-request` |
| 321 | `/api/v5/tradingBot/dca/cycle-list` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-get-dca-cycle-list-http-request` |
| 322 | `/api/v5/tradingBot/dca/history-list` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-get-dca-algo-order-history-http-request` |
| 323 | `/api/v5/tradingBot/dca/margin/add` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-add-dca-margin-http-request` |
| 324 | `/api/v5/tradingBot/dca/margin/reduce` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-reduce-dca-margin-http-request` |
| 325 | `/api/v5/tradingBot/dca/ongoing-list` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-get-dca-algo-order-details-http-request` |
| 326 | `/api/v5/tradingBot/dca/orders` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-get-dca-sub-orders-http-request` |
| 327 | `/api/v5/tradingBot/dca/orders/manual-buy` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-add-investment-http-request` |
| 328 | `/api/v5/tradingBot/dca/position-details` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-get-dca-algo-order-position-details-http-request` |
| 329 | `/api/v5/tradingBot/dca/settings/reinvestment` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-amend-dca-reinvestment-http-request` |
| 330 | `/api/v5/tradingBot/dca/settings/take-profit` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-amend-dca-take-profit-settings-http-request` |
| 331 | `/api/v5/tradingBot/dca/stop` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-dca-trading-post-stop-dca-algo-order-http-request` |
| 332 | `/api/v5/tradingBot/grid/adjust-investment` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-add-investment-http-request` |
| 333 | `/api/v5/tradingBot/grid/ai-param` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-ai-parameter-public-http-request` |
| 334 | `/api/v5/tradingBot/grid/amend-algo-basic-param` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-amend-grid-algo-order-basic-param-http-request` |
| 335 | `/api/v5/tradingBot/grid/amend-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-amend-grid-algo-order-http-request` |
| 336 | `/api/v5/tradingBot/grid/cancel-close-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-cancel-close-position-order-for-contract-grid-http-request` |
| 337 | `/api/v5/tradingBot/grid/close-position` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-close-position-for-contract-grid-http-request` |
| 338 | `/api/v5/tradingBot/grid/compute-margin-balance` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-compute-margin-balance-http-request` |
| 339 | `/api/v5/tradingBot/grid/copy-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID + Instrument ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-copy-grid-algo-order-http-request` |
| 340 | `/api/v5/tradingBot/grid/grid-quantity` | GET | 5 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-get-max-grid-quantity-public-http-request` |
| 341 | `/api/v5/tradingBot/grid/margin-balance` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-adjust-margin-balance-http-request` |
| 342 | `/api/v5/tradingBot/grid/min-investment` | POST | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-compute-min-investment-public-http-request` |
| 343 | `/api/v5/tradingBot/grid/order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID + Instrument ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-place-grid-algo-order-http-request` |
| 344 | `/api/v5/tradingBot/grid/order-instant-trigger` | POST | 20 requests per 2 seconds | 2 seconds | User ID + Instrument ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-post-instant-trigger-grid-algo-order-http-request` |
| 345 | `/api/v5/tradingBot/grid/orders-algo-details` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-algo-order-details-http-request` |
| 346 | `/api/v5/tradingBot/grid/orders-algo-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-algo-order-history-http-request` |
| 347 | `/api/v5/tradingBot/grid/orders-algo-pending` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-algo-order-list-http-request` |
| 348 | `/api/v5/tradingBot/grid/positions` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-algo-order-positions-http-request` |
| 349 | `/api/v5/tradingBot/grid/stop-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-stop-grid-algo-order-http-request` |
| 350 | `/api/v5/tradingBot/grid/sub-orders` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-get-grid-algo-sub-orders-http-request` |
| 351 | `/api/v5/tradingBot/grid/withdraw-income` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-grid-trading-post-spot-grid-withdraw-income-http-request` |
| 352 | `/api/v5/tradingBot/public/rsi-back-testing` | GET | 20 requests per 2 seconds | 2 seconds | IP | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-grid-trading-get-rsi-back-testing-public-http-request` |
| 353 | `/api/v5/tradingBot/recurring/add-investment` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-add-investment-http-request` |
| 354 | `/api/v5/tradingBot/recurring/amend-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-post-amend-recurring-buy-order-http-request` |
| 355 | `/api/v5/tradingBot/recurring/amend-price-range` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-amend-price-range-http-request` |
| 356 | `/api/v5/tradingBot/recurring/amend-recurring-amount` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-amend-recurring-buy-amount-http-request` |
| 357 | `/api/v5/tradingBot/recurring/amend-recurring-time` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-amend-recurring-buy-time-http-request` |
| 358 | `/api/v5/tradingBot/recurring/order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-post-place-recurring-buy-order-http-request` |
| 359 | `/api/v5/tradingBot/recurring/orders-algo-details` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-get-recurring-buy-order-details-http-request` |
| 360 | `/api/v5/tradingBot/recurring/orders-algo-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-get-recurring-buy-order-history-http-request` |
| 361 | `/api/v5/tradingBot/recurring/orders-algo-pending` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-get-recurring-buy-order-list-http-request` |
| 362 | `/api/v5/tradingBot/recurring/pause` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-pause-recurring-buy-http-request` |
| 363 | `/api/v5/tradingBot/recurring/restart` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-recurring-buy-post-restart-recurring-buy-http-request` |
| 364 | `/api/v5/tradingBot/recurring/stop-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-post-stop-recurring-buy-order-http-request` |
| 365 | `/api/v5/tradingBot/recurring/sub-orders` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#order-book-trading-recurring-buy-get-recurring-buy-sub-orders-http-request` |
| 366 | `/api/v5/tradingBot/signal/amendTPSL` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-amend-tpsl-http-request` |
| 367 | `/api/v5/tradingBot/signal/cancel-sub-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-cancel-sub-order-http-request` |
| 368 | `/api/v5/tradingBot/signal/close-position` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-close-position-http-request` |
| 369 | `/api/v5/tradingBot/signal/create-signal` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-create-signal-http-request` |
| 370 | `/api/v5/tradingBot/signal/event-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signal-bot-event-history-http-request` |
| 371 | `/api/v5/tradingBot/signal/margin-balance` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-adjust-margin-balance-http-request` |
| 372 | `/api/v5/tradingBot/signal/order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-create-signal-bot-http-request` |
| 373 | `/api/v5/tradingBot/signal/orders-algo-details` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signal-bot-order-details-http-request` |
| 374 | `/api/v5/tradingBot/signal/orders-algo-history` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signal-bot-history-http-request` |
| 375 | `/api/v5/tradingBot/signal/orders-algo-pending` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-active-signal-bot-http-request` |
| 376 | `/api/v5/tradingBot/signal/positions` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signal-bot-order-positions-http-request` |
| 377 | `/api/v5/tradingBot/signal/positions-history` | GET | 10 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-position-history-http-request` |
| 378 | `/api/v5/tradingBot/signal/set-instruments` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-set-instruments-http-request` |
| 379 | `/api/v5/tradingBot/signal/signals` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signals-http-request` |
| 380 | `/api/v5/tradingBot/signal/stop-order-algo` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-cancel-signal-bots-http-request` |
| 381 | `/api/v5/tradingBot/signal/sub-order` | POST | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-post-place-sub-order-http-request` |
| 382 | `/api/v5/tradingBot/signal/sub-orders` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#order-book-trading-signal-bot-trading-get-signal-bot-sub-orders-http-request` |
| 383 | `/api/v5/users/entrust-subaccount-list` | GET | 1 request per second | second | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-get-custody-trading-sub-account-list-http-request` |
| 384 | `/api/v5/users/glp/historicalperformance` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-get-glp-historical-performance-http-request` |
| 385 | `/api/v5/users/glp/todayperformance` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 两侧都有 | `#trading-account-rest-api-get-get-glp-today-performance-http-request` |
| 386 | `/api/v5/users/glp/v2/details` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-get-glp-v2-assessment-details-http-request` |
| 387 | `/api/v5/users/glp/v2/history/performance` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-get-glp-v2-performance-history-http-request` |
| 388 | `/api/v5/users/glp/v2/overview` | GET | 5 requests per 2 seconds | 2 seconds | User ID | Rate Limit:（标准） | 仅官方有 | `#trading-account-rest-api-get-get-glp-v2-overview-http-request` |
| 389 | `/api/v5/users/subaccount/apikey` | GET | 20 request per 2 seconds | 2 seconds | User ID | Rate limit：（全角冒号） | 仅官方有 | `#sub-account-rest-api-query-the-api-key-of-a-sub-account-http-request` |
| 390 | `/api/v5/users/subaccount/apikey` | POST | 1 request per second | second | User ID | Rate limit：（全角冒号） | 仅官方有 | `#sub-account-rest-api-create-an-api-key-for-a-sub-account-http-request` |
| 391 | `/api/v5/users/subaccount/create-subaccount` | POST | 1 request per second | second | User ID | Rate limit：（全角冒号） | 仅官方有 | `#sub-account-rest-api-create-sub-account-http-request` |
| 392 | `/api/v5/users/subaccount/delete-apikey` | POST | 1 request per second | second | User ID | Rate limit：（全角冒号） | 仅官方有 | `#sub-account-rest-api-delete-the-api-key-of-sub-accounts-http-request` |
| 393 | `/api/v5/users/subaccount/list` | GET | 20 requests per 2 seconds | 2 seconds | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-get-sub-account-list-http-request` |
| 394 | `/api/v5/users/subaccount/modify-apikey` | POST | 1 request per second | second | User ID | Rate limit：（全角冒号） | 两侧都有 | `#sub-account-rest-api-reset-the-api-key-of-a-sub-account-http-request` |
| 395 | `/api/v5/users/subaccount/set-transfer-out` | POST | 1 request per second | second | User ID | Rate Limit:（标准） | 两侧都有 | `#sub-account-rest-api-set-permission-of-transfer-out-http-request` |

> 上表 395 行即 S1 全部 REST 端点声明（386 个 distinct 路径）。因表只列官方端点，声明级「对齐」只出现「两侧都有」(246) 与「仅官方有」(149) 两类；「仅项目有」的 33 个路径不在官方清单里，完整列于问题 4，路径级三分类数字见问题 2。

### 1.3 字段释义与官方事实（表是这些事实在本图内的唯一载体，08 已定表不承载它们）

- **限额数值 + 时间窗**：官方写法 `Rate Limit: N requests per <window>`（中文 `限速：N次/<window>`）。时间窗**不统一**，S1 内可见 `per second`、`per 2 seconds`、`per 5 seconds`、`per 10 seconds`、`per day`、`per month`，以及带 UTC 重置的方向性写法（`/api/v5/account/demo-adjust-balance`：`Increase — 3 requests per user per day (resets at UTC 0:00). Reduce — no limit.`）。2 秒只是其中一种。
- **计数维度**：每个端点另带 `Rate limit rule:`（中文 `限速规则：`），如 `User ID`、`IP`、`User ID + Instrument ID`、`User ID + Instrument Family`、`Instrument ID`、`User ID(Private) or IP(Public)`、`(except Options): User ID + Instrument ID` / `(Options only): User ID + Instrument Family` 等。同一数值按何种维度计数，是表 `(requests, window)` 二元组之外的官方事实。
- **多方法区分**：S1 有 **9 个路径同时有 POST + GET 两个声明**（395 声明 → 386 路径，差 9），逐条对比见 1.4。项目表以 `path` 单键、不区分方法（08 已定）。
- **REST-WS 共享 / 下单类额外规则**：S1 `POST / Place order` 等端点原文另有 `Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds`（跟单带单员特例，共 5 个端点，见 1.4）与 `Rate limit of this endpoint will also be affected by the rules Sub-account rate limit and Fill ratio based sub-account rate limit.` 说明段；01 已记录 REST 与 WebSocket 下单限额共享、单笔/批量独立等规则。这些都不在二元组里。
- **来源页**：每条都可追到 S1 该端点自己的 `...-http-request` h4 id（上表末列）；S2 中文页同名端点可交叉验证。

### 1.4 同路径多方法（9 个）与特殊值行

| 路径 | POST 声明 | GET 声明 | 数值是否相同 |
|---|---|---|---|
| `/api/v5/account/bills-history-archive` | 12 requests per day（维度：User ID） | 10 requests per 2 seconds（维度：User ID） | 不同 |
| `/api/v5/account/mmp-config` | 2 requests per 10 seconds（维度：User ID） | 5 requests per 2 seconds（维度：User ID） | 不同 |
| `/api/v5/asset/monthly-statement` | 20 requests per month（维度：User ID） | 10 requests per 2 seconds（维度：User ID） | 不同 |
| `/api/v5/rfq/maker-instrument-settings` | 5 requests per 2 seconds（维度：User ID） | 5 requests per 2 seconds（维度：User ID） | 相同 |
| `/api/v5/rfq/mmp-config` | 1 request per 10 seconds（维度：User ID） | 5 requests per 2 seconds（维度：User ID） | 不同 |
| `/api/v5/sprd/order` | 20 requests per 2 seconds（维度：User ID） | 20 requests per 2 seconds（维度：User ID） | 相同 |
| `/api/v5/trade/order` | 60 requests per 2 seconds（维度：(except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family） | 60 requests per 2 seconds（维度：(except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family） | 相同 |
| `/api/v5/trade/order-algo` | 20 requests per 2 seconds（维度：(except Options): User ID + Instrument ID ; (Options only): User ID + Instrument Family） | 20 requests per 2 seconds（维度：User ID） | 相同 |
| `/api/v5/users/subaccount/apikey` | 1 request per second（维度：User ID） | 20 request per 2 seconds（维度：User ID） | 不同 |

其中 **5 个路径 POST 与 GET 限额数值不同**（`bills-history-archive`、`mmp-config`、`monthly-statement`、`rfq/mmp-config`、`users/subaccount/apikey`），**4 个相同**（`rfq/maker-instrument-settings`、`sprd/order`、`trade/order`、`trade/order-algo`）。另注：`/api/v5/trade/order-algo` 虽数值相同（均 20/2s），但计数维度不同：GET 为 `User ID`，POST 为两行 `(except Options): User ID + Instrument ID` / `(Options only): User ID + Instrument Family`（S1 完整版原文；S3 子集里 POST 只写 `User ID + Instrument ID` 一行）。

**2 个带 2 条值行 / 2 个维度的端点**（同一端点详情内并列两组，原文如此）：
- `POST /api/v5/asset/convert/estimate-quote` = `Rate Limit: 10 requests per second`（`Rate limit rule: User ID`）+ `Rate Limit: 1 request per 5 seconds`（`Rate limit rule: Instrument ID`）；
- `POST /api/v5/fiat/buy-sell/quote` = `Rate Limit: 10 requests per second`（`Rate limit rule: User ID`）+ `Rate Limit: 1 request per 5 seconds`（`Rate limit rule: Instrument ID`）。

**5 个带跟单带单员特例段的端点**（S1 原文 `Rate Limit of lead trader lead instruments for Copy Trading: ...`）：

- `POST /api/v5/trade/order` — Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds
- `POST /api/v5/trade/batch-orders` — Rate Limit of lead trader lead instruments for Copy Trading: 4 orders per 2 seconds
- `POST /api/v5/trade/amend-order` — Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds
- `POST /api/v5/trade/amend-batch-orders` — Rate Limit of lead trader lead instruments for Copy Trading: 4 orders per 2 seconds
- `POST /api/v5/trade/order-algo` — Rate Limit of lead trader lead instruments for Copy Trading: 1 request per 2 seconds

### 1.5 唯一无 `Rate limit rule` 计数维度行的端点

- `GET /api/v5/system/status` — S1 原文只有 `Rate Limit: 1 request per 5 seconds`，**没有** `Rate limit rule:` 行（其余 394 个声明都有）。中文 S2 同端点亦仅 `限速：1次/5s`，无 `限速规则` 行。原文未给出该端点按何种维度计数。

### 1.6 有 `Rate Limit:` 值行但**不是 REST 路径**的端点（11 个 WebSocket 端点，S1）

这些端点带 `Rate Limit:` 行，但没有 `HTTP Request` 声明、路径不是 `/api/v5/...`，故**不计入**上面 386 个 REST 路径：

- `60 requests per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-place-order-rate-limit-60-requests-per-2-seconds`
- `300 orders per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-place-multiple-orders-rate-limit-300-orders-per-2-seconds`
- `60 requests per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-cancel-order-rate-limit-60-requests-per-2-seconds`
- `300 orders per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-cancel-multiple-orders-rate-limit-300-orders-per-2-seconds`
- `60 requests per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-amend-order-rate-limit-60-requests-per-2-seconds`
- `300 orders per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-amend-multiple-orders-rate-limit-300-orders-per-2-seconds`
- `5 requests per 2 seconds` — S1 锚点 `#order-book-trading-trade-ws-mass-cancel-order-rate-limit-5-requests-per-2-seconds`
- `20 requests per 2 seconds` — S1 锚点 `#spread-trading-websocket-trade-api-ws-place-order-rate-limit-20-requests-per-2-seconds`
- `20 requests per 2 seconds` — S1 锚点 `#spread-trading-websocket-trade-api-ws-amend-order-rate-limit-20-requests-per-2-seconds`
- `20 requests per 2 seconds` — S1 锚点 `#spread-trading-websocket-trade-api-ws-cancel-order-rate-limit-20-requests-per-2-seconds`
- `5 requests per 2 seconds` — S1 锚点 `#spread-trading-websocket-trade-api-ws-cancel-all-orders-rate-limit-5-requests-per-2-seconds`

---

## 2. 官方清单与项目 `okx/consts/endpoints/` 路径常量对齐

项目侧：`okx/consts/endpoints/*.py` 共 **279 个常量赋值**，全部是 `/api/v5/...` 字符串（无其它形式），去重后 **274 个 distinct 路径**（与 09 工单所述一致）。其中 **5 个路径被 2 个常量名共用**：

| 路径 | 共用的常量名 |
|---|---|
| `/api/v5/asset/non-tradable-assets` | `NON_TRADABLE_ASSETS`, `GET_NON_TRADABLE_ASSETS` |
| `/api/v5/broker/fd/rebate-per-orders` | `FD_GET_REBATE_PER_ORDERS`, `FD_REBATE_PER_ORDERS` |
| `/api/v5/sprd/order` | `SPREAD_PLACE_ORDER`, `SPREAD_GET_ORDER_DETAILS` |
| `/api/v5/trade/order` | `PLACE_ORDER`, `ORDER_INFO` |
| `/api/v5/trade/order-algo` | `PLACE_ALGO_ORDER`, `GET_ALGO_ORDER_DETAILS` |

### 2.1 对齐结果（两套口径并列，各自标注来源）

| 口径 | 官方 distinct 路径 | 项目 distinct 路径 | 两侧都有 | 仅官方有 | 仅项目有 |
|---|---:|---:|---:|---:|---:|
| **S1 完整版 `www.okx.com/docs-v5/en/`（本文主口径）** | 386 | 274 | **241** | **145** | **33** |
| S3 子集 `app.okx.com/docs-v5/en/`（01 工单所用） | 135 | 274 | 104 | 31 | 170 |

逐条标注见 1.2 主表的「对齐」列（395 行，每行一个声明都标了）。集合关系：`274 - 386 = -112` 的差由「仅项目 33 − 仅官方 145」构成；S3 口径下为 `274 - 135 = 139 = 170 − 31`。

### 2.2 仅官方有（145 个，S1 完整版口径）

官方已给出限额、项目 `okx/consts/endpoints/` 无同名路径常量。按业务段分组计数（完整路径清单见附录 A）：

| 业务段 | 个数 |
|---|---:|
| `/api/v5/tradingBot` | 45 |
| `/api/v5/copytrading` | 17 |
| `/api/v5/account` | 16 |
| `/api/v5/fiat` | 13 |
| `/api/v5/public` | 10 |
| `/api/v5/market` | 8 |
| `/api/v5/users` | 6 |
| `/api/v5/finance` | 6 |
| `/api/v5/affiliate` | 6 |
| `/api/v5/asset` | 4 |
| `/api/v5/rubik` | 4 |
| `/api/v5/trade` | 4 |
| `/api/v5/sprd` | 3 |
| `/api/v5/rfq` | 2 |
| `/api/v5/support` | 1 |

### 2.3 仅项目有（33 个，S1 完整版口径）

项目常量里有、S1 全文**连路径串都不出现**（无 REST 端点详情、无 `Rate Limit:` 行）。完整清单见问题 4。按业务段分组：

| 业务段 | 个数 |
|---|---:|
| `/api/v5/account` | 17 |
| `/api/v5/affiliate` | 5 |
| `/api/v5/asset` | 4 |
| `/api/v5/market` | 2 |
| `/api/v5/public` | 2 |
| `/api/v5/finance` | 1 |
| `/api/v5/sprd` | 1 |
| `/api/v5/broker` | 1 |

---

## 3. 274 与 135 的差异解释（逐项给数字 / 给不出则说明原因）

**先给结论：这个差额主要不是「别名 / 废弃 / 非 REST」，而是「01 取证的页面是完整版文档的子集」这一统计口径差异。** 01 的 135 来自 S3（`app.okx.com/docs-v5/en/`，10 个业务段）；同一官方文档的完整版 S1（`www.okx.com/docs-v5/en/`）有 386 个路径、16 个业务段，且 S3 的 135 个路径全部在 S1 内、数值零差异。

### 3.1 按问题所列的五类原因逐项分解

| 差异原因 | 数字 | 说明 / 来源 |
|---|---|---|
| **统计口径 / 取证页面覆盖范围（主因）** | 由「仅项目 170 → 33」体现：**137 个**端点在 S3 里查不到、但在 S1 完整版里有对应端点 | S3 口径「仅项目有」= 170 个；S1 口径 = 33 个，差 137 个。这 137 个是 S1 相对 S3 补齐的端点：**112 个**属于 S3 完全没有、S1 新增的 6 个业务段（`finance` / `tradingBot` / `rfq` / `rubik` / `sprd` / `copytrading`），**25 个**属于 S3 已有的 10 个段内但 S3 未给 REST 详情、S1 给了。S3 口径下「段外」路径共 115 个（7 类：`finance` 49 / `tradingBot` 19 / `rfq` 16 / `rubik` 11 / `sprd` 10 / `copytrading` 9 / `broker` 1），其中 112 个在 S1 有对应，另 3 个（`broker` 1、`finance` 1、`sprd` 1）连 S1 也没有、留在 33 个里；其余 55 个属 S3 已有段。S1 补齐后两侧都有从 104 升到 241。（S1/S3 逐路径比对） |
| **别名 / 同一路径多个常量名** | **5 个**路径被 2 个名字共用 → 常量名 279 → 路径 274，差 5 | 即 2.1 表所列 5 个；08 特别关注的 `/api/v5/trade/order` = `PLACE_ORDER` + `ORDER_INFO` 属此类。这解释「常量名数 > 路径数」，不解释 274 vs 135。 |
| **同一路径多方法** | S1：**9 个**路径有 POST+GET 双声明（395 声明 → 386 路径，差 9）；S3：**6 个**（141 → 135，差 6） | 逐条见 1.4。这是「声明数 vs distinct 路径数」的差，不改变 distinct 路径集合；项目按 `path` 单键（08），故不体现在 274 里。 |
| **非 REST 路径** | **0 个** | `okx/consts/endpoints/` 的 274 个路径**全部**是 `/api/v5/...` REST 路径，无混入。WS 地址常量在 `okx/consts/websocket.py`（`wss://ws.okx.com:8443/ws/v5/...`），不在 `endpoints/` 内、不计入 274。官方另有 11 个 WebSocket 端点带 `Rate Limit:` 行（1.6），但它们不是 REST 路径，不进 135/386。 |
| **废弃端点 / 本页未收录端点** | S1 完整版口径：**33 个**（问题 4 清单）；S3 口径：170 个 | 这 33 个在 S1 全文里连路径串都不出现，本次取证的官方页面内无对应端点详情。是否属「官方废弃」未能查证（见「覆盖范围与未查到的部分」），只如实记「本页无对应」；03 已定它们按「未收录端点」维持不限流、不在验收线内。 |

### 3.2 差额恒等式

- S1 口径：`274 − 386 = −112 = 33(仅项目) − 145(仅官方)`；两侧都有 `241`。
- S3 口径（01/09 工单所用）：`274 − 135 = 139 = 170(仅项目) − 31(仅官方)`；两侧都有 `104`。
- 「135」本身 = S3 全文 distinct `/api/v5/...` 路径串数（本次复现，与 S3 的 141 个声明去重后的 135 个路径**恰好是同一集合**）；S3 的 137 是标准写法值行数，141 是不区分大小写的 `HTTP Request`/`HTTP request` 块数。01 当时声明「未穷尽逐一核验」，本次已把 S3 的 141 个声明逐一绑定到值行 / 维度 / 路径（见问题 5）。


---

## 4. 项目路径常量里「官方无对应端点」的那些（S1 完整版口径，33 个）

判据：路径串在 **S1 全文（含 Request Example、表格、Change Log 提及）** 中**完全不出现**。以下逐条列出（左为路径，右为项目里指向它的常量名）。按 03 已定：它们不在覆盖验收线内、按「未收录端点」维持不限流。

| 路径 | 项目常量名 |
|---|---|
| `/api/v5/account/borrow-repay` | `BORROW_REPAY` |
| `/api/v5/account/borrow-repay-history` | `BORROW_REPAY_HISTORY` |
| `/api/v5/account/fixed-loan/amend-borrowing-order` | `AMEND_BORROWING_ORDER` |
| `/api/v5/account/fixed-loan/borrowing-limit` | `BORROWING_LIMIT` |
| `/api/v5/account/fixed-loan/borrowing-order` | `PLACE_BORROWING_ORDER` |
| `/api/v5/account/fixed-loan/borrowing-orders-list` | `BORROWING_ORDERS_LIST` |
| `/api/v5/account/fixed-loan/borrowing-quote` | `BORROWING_QUOTE` |
| `/api/v5/account/fixed-loan/manual-reborrow` | `MANUAL_REBORROW` |
| `/api/v5/account/fixed-loan/repay-borrowing-order` | `REPAY_BORROWING_ORDER` |
| `/api/v5/account/set-riskOffset-type` | `SET_RISK_OFFSET_TYPE` |
| `/api/v5/account/simulated_margin` | `SIMULATED_MARGIN` |
| `/api/v5/account/subaccount/interest-limits` | `GET_SUB_ACCOUNT_BORROW_INTEREST_AND_LIMIT` |
| `/api/v5/account/subaccount/set-loan-allocation` | `SET_SUB_ACCOUNTS_VIP_LOAN` |
| `/api/v5/account/vip-interest-accrued` | `GET_VIP_INTEREST_ACCRUED_DATA` |
| `/api/v5/account/vip-interest-deducted` | `GET_VIP_INTEREST_DEDUCTED_DATA` |
| `/api/v5/account/vip-loan-order-detail` | `GET_VIP_LOAN_ORDER_DETAIL` |
| `/api/v5/account/vip-loan-order-list` | `GET_VIP_LOAN_ORDER_LIST` |
| `/api/v5/affiliate/tvb/invitee/detail` | `AFFILIATE_TVB_INVITEE_DETAIL` |
| `/api/v5/affiliate/tvb/invitee/list` | `AFFILIATE_TVB_INVITEE_LIST` |
| `/api/v5/affiliate/tvb/link/list` | `AFFILIATE_TVB_LINK_LIST` |
| `/api/v5/affiliate/tvb/performance/summary` | `AFFILIATE_TVB_PERFORMANCE_SUMMARY` |
| `/api/v5/affiliate/tvb/tier-breakdown` | `AFFILIATE_TVB_TIER_BREAKDOWN` |
| `/api/v5/asset/convert-dust-assets` | `CONVERT_DUST_ASSETS` |
| `/api/v5/asset/deposit-lightning` | `DEPOSIT_LIGHTNING` |
| `/api/v5/asset/purchase_redempt` | `PURCHASE_REDEMPT` |
| `/api/v5/asset/withdrawal-lightning` | `WITHDRAWAL_LIGHTNING` |
| `/api/v5/broker/fd/rebate-per-orders` | `FD_GET_REBATE_PER_ORDERS`, `FD_REBATE_PER_ORDERS` |
| `/api/v5/finance/savings/set-lending-rate` | `SET_LENDING_RATE` |
| `/api/v5/market/block-trades` | `BLOCK_TRADES` |
| `/api/v5/market/books-lite` | `GET_ORDER_LITE_BOOK` |
| `/api/v5/public/liquidation-orders` | `LIQUIDATION_ORDERS` |
| `/api/v5/public/vip-interest-rate-loan-quota` | `VIP_INTEREST_RATE_LOAN_QUOTA` |
| `/api/v5/sprd/ticker` | `SPREAD_GET_TICKER` |

> 补充（S3 口径）：若只看 01 用的 `app.okx.com/docs-v5/en/`，「仅项目有」是 **170** 个，其中 **115** 个属于 S3 完全没有的业务段（`finance` 49 / `tradingBot` 19 / `rfq` 16 / `rubik` 11 / `sprd` 10 / `copytrading` 9 / `broker` 1），另 **55** 个在 S3 已有的 10 个段内但 S3 未给 REST 详情；S3 全文只有 1 个项目独有路径（`/api/v5/public/funding-rate`）曾作为文本出现过但无 REST 声明。这些在 S1 完整版下大多已有对应端点，故不列入上表。

---

## 5. 官方是否确有端点没有 `Rate Limit:` 行（逐一确认）

**结论：逐一核验后，本次取证范围内没有「缺 `Rate Limit:` 限额值行」的 REST 端点。** 01 的「未发现成批、只作统计性陈述」在本次被做实为「0 个」，但发现了两处需要说明的**写法与口径**问题：

**(a) S1 完整版：395 个 REST 声明全部带值行**（397 条）；唯一「无 `Rate limit rule` 计数维度行」的是 `GET /api/v5/system/status`（1.5）。11 个带值行的 WS 端点不是 REST 声明（1.6）。

**(b) 12 个端点用的是变体值行写法，01 的「137 处 `Rate Limit:`」只数标准写法、没把它们数进去。** 在 S3 口径下，这 12 个端点（1 个 `Get bill types` + 11 个 Sub-account 端点）用 `Rate limit:`（小写 l）或**全角冒号** `Rate limit：` 给值；它们连同另 1 个 `Get the invitee's detail` 端点，HTTP 声明标题都写成小写 `HTTP request`（共 13 处）。逐条核验这 12 个端点**都有**限额，不是缺失。原文表述如下（S1/S3 一致，逐条列出）：

| 端点（S3 标题） | 方法 路径 | 原文值行写法 | 原文限额值 | 原文计数维度 |
|---|---|---|---|---|
| Get sub-account trading balance | `GET /api/v5/account/subaccount/balances` | `Rate limit：（全角冒号）` | 6 requests per 2 seconds | User ID |
| Get sub-account maximum withdrawals | `GET /api/v5/account/subaccount/max-withdrawal` | `Rate limit:（小写 l）` | 20 requests per 2 seconds | User ID |
| Get bill types | `GET /api/v5/account/subtypes` | `Rate limit:（小写 l）` | 20 requests per 2 seconds | UserId |
| Get sub-account funding balance | `GET /api/v5/asset/subaccount/balances` | `Rate limit：（全角冒号）` | 6 requests per 2 seconds | User ID |
| Get history of sub-account transfer | `GET /api/v5/asset/subaccount/bills` | `Rate limit：（全角冒号）` | 6 requests per second | User ID |
| Master accounts manage the transfers between sub-accounts | `POST /api/v5/asset/subaccount/transfer` | `Rate limit：（全角冒号）` | 1 request per second | User ID |
| Create an API Key for a sub-account | `POST /api/v5/users/subaccount/apikey` | `Rate limit：（全角冒号）` | 1 request per second | User ID |
| Query the API Key of a sub-account | `GET /api/v5/users/subaccount/apikey` | `Rate limit：（全角冒号）` | 20 request per 2 seconds | User ID |
| Create sub-account | `POST /api/v5/users/subaccount/create-subaccount` | `Rate limit：（全角冒号）` | 1 request per second | User ID |
| Delete the API Key of sub-accounts | `POST /api/v5/users/subaccount/delete-apikey` | `Rate limit：（全角冒号）` | 1 request per second | User ID |
| Get sub-account list | `GET /api/v5/users/subaccount/list` | `Rate limit：（全角冒号）` | 20 requests per 2 seconds | User ID |
| Reset the API Key of a sub-account | `POST /api/v5/users/subaccount/modify-apikey` | `Rate limit：（全角冒号）` | 1 request per second | User ID |

（共 12 行；例：`Get sub-account list` 原文 `Rate limit：20 requests per 2 seconds` + `Rate limit rule: User ID`；`Get bill types` 原文 `Rate limit: 20 requests per 2 seconds` + `Rate limit rule: UserId`；`Create sub-account` 原文 `Rate limit：1 request per second`。全角冒号 `：` 为 U+FF1A，是官方页面原文字符，不是本文转写。）

**(c) 全局对账闭合**：S1 的 408 条限额值行 = 397（REST 声明）+ 11（WS 端点）。S3 的 137 处标准写法 `Rate Limit:` = **130 条 REST 声明值行**（129 个声明带标准值行，其中 `convert/estimate-quote` 有 2 条）+ **7 条 WS 端点值行**；另 12 个 REST 声明**只有变体写法**值行，故 S3 的 141 个 REST 声明合计 **142 条值行、全部有值行**。S3 的 141 个声明 = **128 个** `HTTP Request` + **13 个** `HTTP request`（小写 r）；其中 `Get the invitee's detail`（`GET /api/v5/affiliate/invitee/detail`，`Rate Limit: 3 requests per second`、`Rate limit rule: User ID`）标题用了小写 `HTTP request`，曾被初版解析漏掉，已补入并核对：Change Log（S5）2026-05-08「Rate Limit Changes」条目记「Rate limit of Get the invitee's detail has been changed from 20 requests per 2 seconds to 3 requests per second」，S1/S3 主文档当前值 `3 requests per second`，已同步。

**(d) 一处主文档与 Change Log 不一致（如实记录）**：S5 的 2026-06-11 条目「Apply bills details (since 2021): rate limit relaxed」原文「The rate limit of POST / Apply bills details (since 2021) has been changed from 12 requests per day to 1 request per 10 seconds per user.」；但 S1 与 S3 两版主文档在 2026-11-06 快照中 `POST /api/v5/account/bills-history-archive` 的端点详情**仍写 `Rate Limit: 12 requests per day`**（`Rate limit rule: User ID`）。本次未查到主文档已同步该变更的证据。本文清单按**主文档端点详情原文**记 `12 requests per day`，并在此标注与该 Change Log 条目的冲突。

---

## 6. 特别关注：`/api/v5/trade/order` 的 POST + GET 限额是否不同（08 触发条件输入）

**结论：相同。** S1 英文与 S2 中文、S3/S4 子集四份官方页面一致。

| | POST `Place order`（项目 `PLACE_ORDER`） | GET `Order details`（项目 `ORDER_INFO`） |
|---|---|---|
| 数值（S1 原文） | `Rate Limit: 60 requests per 2 seconds` | `Rate Limit: 60 requests per 2 seconds` |
| 数值（S2 中文原文） | `限速：60次/2s` | `限速：60次/2s` |
| 计数维度（S1 原文） | `Rate limit rule (except Options): User ID + Instrument ID` ；`Rate limit rule (Options only): User ID + Instrument Family` | 与左侧**完全相同**的两行 |
| 计数维度（S2 中文原文） | `限速规则（期权以外）：User ID + Instrument ID` ；`限速规则（只限期权）：User ID + Instrument Family` | 与左侧**完全相同**的两行 |
| 额外段落 | 有 `Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds`（S2：`跟单交易带单员带单产品的限速：4次/2s`），以及「本接口限速同时受子账户限速 / 基于成交比率的子账户限速影响」说明 | 无此两段 |

即：**主限额数值相同（60/2s）、计数维度相同**；两者唯一差别是 POST 端点详情多一段「跟单带单员带单产品」特例限额与一段子账户限速说明，GET 端点没有。项目里 `PLACE_ORDER` 与 `ORDER_INFO` 共用同一 `path` 单键（08 已定不改 key），现有 `RATE_LIMITS['/api/v5/trade/order'] = (60, 2)` 对两个方法都成立。

> 与 01 findings 的差异（如实标注）：01 第 6 节曾写「`/api/v5/trade/order` 的 POST 与 GET 均标 60/2 但 `Rate limit rule` 不同」。本次逐一核验四份官方页面，**未复现 rule 不同**：POST 与 GET 的 `Rate limit rule` 两行完全相同；01 所述差异可能源于把 POST 独有的跟单特例段计入了比较。以本次快照原文为准。

> 对 08 触发条件的含义（只陈述事实）：08 预留的「若同路径 POST+GET 限额不同则另开新工单」这一条件，**就 `/api/v5/trade/order` 而言未触发**。但作为事实输入需并列记录：S1 的 9 个多方法路径中有 **5 个 POST/GET 数值确实不同**（`bills-history-archive` 12/day vs 10/2s、`mmp-config` 2/10s vs 5/2s、`monthly-statement` 20/month vs 10/2s、`rfq/mmp-config` 1/10s vs 5/2s、`users/subaccount/apikey` 1/s vs 20/2s），且 `trade/order-algo` 数值相同但计数维度不同（GET `User ID`；POST 为 `(except Options): User ID + Instrument ID` / `(Options only): User ID + Instrument Family` 两行）。这些是否另开工单是决策工单的事，本文不下结论。

---


## 附录 A：仅官方有（145 个，S1 完整版口径）完整路径清单

官方已给出限额、项目 `okx/consts/endpoints/` 无对应常量。按路径排序：


- `/api/v5/account/account-level-switch-preset` — POST 5 requests per 2 seconds
- `/api/v5/account/activate-feature` — POST 5 requests per 2 seconds
- `/api/v5/account/adjust-leverage-info` — GET 5 requests per 2 seconds
- `/api/v5/account/collateral-assets` — GET 5 requests per 2 seconds
- `/api/v5/account/demo-adjust-balance` — POST Increase — 3 requests per user per day (resets at UTC 0:00). Reduce — no limit.
- `/api/v5/account/mmp-config` — POST 2 requests per 10 seconds ; GET 5 requests per 2 seconds
- `/api/v5/account/mmp-reset` — POST 5 requests per 2 seconds
- `/api/v5/account/move-positions` — POST 1 request per second
- `/api/v5/account/move-positions-history` — GET 2 requests per 2 seconds
- `/api/v5/account/position-builder-graph` — POST 1 request per 5 seconds
- `/api/v5/account/set-account-switch-precheck` — GET 5 requests per 2 seconds
- `/api/v5/account/set-collateral-assets` — POST 5 requests per 2 seconds
- `/api/v5/account/set-fee-type` — POST 5 requests per 2 seconds
- `/api/v5/account/set-riskOffset-amt` — POST 10 requests per 2 seconds
- `/api/v5/account/set-settle-currency` — POST 20 times per 2 seconds
- `/api/v5/account/subaccount/max-withdrawal` — GET 20 requests per 2 seconds
- `/api/v5/affiliate/co-inviter/list` — GET 3 requests per second
- `/api/v5/affiliate/invitee/detail` — GET 3 requests per second
- `/api/v5/affiliate/invitee/list` — GET 3 requests per second
- `/api/v5/affiliate/link/list` — GET 3 requests per second
- `/api/v5/affiliate/performance/summary` — GET 3 requests per second
- `/api/v5/affiliate/sub-affiliate/list` — GET 3 requests per second
- `/api/v5/asset/bills-history` — GET 1 Requests per second
- `/api/v5/asset/exchange-list` — GET 6 requests per second
- `/api/v5/asset/monthly-statement` — POST 20 requests per month ; GET 10 requests per 2 seconds
- `/api/v5/asset/subaccount/managed-subaccount-bills` — GET 6 requests per second
- `/api/v5/copytrading/amend-copy-settings` — POST 5 requests per 2 seconds
- `/api/v5/copytrading/amend-profit-sharing-ratio` — POST 5 requests per 2 seconds
- `/api/v5/copytrading/config` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/copy-settings` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/current-lead-traders` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/first-copy-settings` — POST 5 requests per 2 seconds
- `/api/v5/copytrading/public-config` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-copy-traders` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-current-subpositions` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-lead-traders` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-pnl` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-preference-currency` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-stats` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-subpositions-history` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/public-weekly-pnl` — GET 5 requests per 2 seconds
- `/api/v5/copytrading/stop-copy-trading` — POST 5 requests per 2 seconds
- `/api/v5/copytrading/total-unrealized-profit-sharing` — GET 5 requests per 2 seconds
- `/api/v5/fiat/buy-sell/currencies` — GET 6 requests per second
- `/api/v5/fiat/buy-sell/currency-pair` — GET 6 requests per second
- `/api/v5/fiat/buy-sell/history` — GET 6 requests per second
- `/api/v5/fiat/buy-sell/quote` — POST 10 requests per second, 1 request per 5 seconds
- `/api/v5/fiat/buy-sell/trade` — POST 1 request per 5 seconds
- `/api/v5/fiat/cancel-withdrawal` — POST 3 requests per second
- `/api/v5/fiat/create-withdrawal` — POST 3 requests per second
- `/api/v5/fiat/deposit` — GET 3 requests per second
- `/api/v5/fiat/deposit-order-history` — GET 3 requests per second
- `/api/v5/fiat/deposit-payment-methods` — GET 3 requests per second
- `/api/v5/fiat/withdrawal` — GET 3 requests per second
- `/api/v5/fiat/withdrawal-order-history` — GET 3 requests per second
- `/api/v5/fiat/withdrawal-payment-methods` — GET 3 requests per second
- `/api/v5/finance/okusd/limits` — GET 2 requests per 2 seconds
- `/api/v5/finance/okusd/redeem` — POST 1 request per 2 seconds
- `/api/v5/finance/okusd/subscribe` — POST 1 request per 2 seconds
- `/api/v5/finance/stable-rewards/apy-history` — GET 6 requests per second
- `/api/v5/finance/stable-rewards/balance` — GET 5 requests per 2 seconds
- `/api/v5/finance/stable-rewards/product-info` — GET 5 requests per 2 seconds
- `/api/v5/market/books-full` — GET 10 requests per 2 seconds
- `/api/v5/market/books-sbe` — GET 10 requests per 10 seconds
- `/api/v5/market/call-auction-details` — GET 20 requests per 2 seconds
- `/api/v5/market/history-index-candles` — GET 10 requests per 2 seconds
- `/api/v5/market/history-mark-price-candles` — GET 20 requests per 2 seconds
- `/api/v5/market/sprd-candles` — GET 40 requests per 2 seconds
- `/api/v5/market/sprd-history-candles` — GET 20 requests per 2 seconds
- `/api/v5/market/sprd-ticker` — GET 20 requests per 2 seconds
- `/api/v5/public/block-trades` — GET 20 requests per 2 seconds
- `/api/v5/public/delta-hedge-currencies` — GET 20 requests per 2 seconds
- `/api/v5/public/economic-calendar` — GET 1 request per 5 seconds
- `/api/v5/public/estimated-settlement-info` — GET 10 requests per 2 seconds
- `/api/v5/public/event-contract/events` — GET 10 requests per 2 seconds
- `/api/v5/public/event-contract/markets` — GET 10 requests per 2 seconds
- `/api/v5/public/event-contract/series` — GET 10 requests per 2 seconds
- `/api/v5/public/mm-instrument-types` — GET 5 requests per 2 seconds
- `/api/v5/public/premium-history` — GET 20 requests per 2 seconds
- `/api/v5/public/settlement-history` — GET 40 requests per 2 seconds
- `/api/v5/rfq/cancel-all-after` — POST 1 request per second
- `/api/v5/rfq/mmp-config` — POST 1 request per 10 seconds ; GET 5 requests per 2 seconds
- `/api/v5/rubik/stat/contracts/long-short-account-ratio-contract` — GET 5 requests per 2 seconds
- `/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader` — GET 5 requests per 2 seconds
- `/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader` — GET 5 requests per 2 seconds
- `/api/v5/rubik/stat/taker-volume-contract` — GET 5 requests per 2 seconds
- `/api/v5/sprd/amend-order` — POST 20 requests per 2 seconds
- `/api/v5/sprd/cancel-all-after` — POST 1 request per second
- `/api/v5/sprd/orders-history-archive` — GET 20 requests per 2 seconds
- `/api/v5/support/announcement-types` — GET 1 request per 2 seconds
- `/api/v5/trade/account-rate-limit` — GET 1 request per second
- `/api/v5/trade/cancel-all-after` — POST 1 request per second
- `/api/v5/trade/mass-cancel` — POST 5 requests per 2 seconds
- `/api/v5/trade/order-precheck` — POST 5 requests per 2 seconds
- `/api/v5/tradingBot/dca/amend-order-algo` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/create` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/cycle-list` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/history-list` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/margin/add` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/margin/reduce` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/ongoing-list` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/orders` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/orders/manual-buy` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/position-details` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/settings/reinvestment` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/settings/take-profit` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/dca/stop` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/adjust-investment` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/amend-algo-basic-param` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/cancel-close-order` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/close-position` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/copy-order-algo` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/grid-quantity` — GET 5 requests per 2 seconds
- `/api/v5/tradingBot/grid/min-investment` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/grid/order-instant-trigger` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/public/rsi-back-testing` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/add-investment` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/amend-price-range` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/amend-recurring-amount` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/amend-recurring-time` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/pause` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/recurring/restart` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/amendTPSL` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/cancel-sub-order` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/close-position` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/create-signal` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/event-history` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/margin-balance` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/order-algo` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/orders-algo-details` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/orders-algo-history` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/orders-algo-pending` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/positions` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/positions-history` — GET 10 requests per 2 seconds
- `/api/v5/tradingBot/signal/set-instruments` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/signals` — GET 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/stop-order-algo` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/sub-order` — POST 20 requests per 2 seconds
- `/api/v5/tradingBot/signal/sub-orders` — GET 20 requests per 2 seconds
- `/api/v5/users/glp/v2/details` — GET 5 requests per 2 seconds
- `/api/v5/users/glp/v2/history/performance` — GET 5 requests per 2 seconds
- `/api/v5/users/glp/v2/overview` — GET 5 requests per 2 seconds
- `/api/v5/users/subaccount/apikey` — POST 1 request per second ; GET 20 request per 2 seconds
- `/api/v5/users/subaccount/create-subaccount` — POST 1 request per second
- `/api/v5/users/subaccount/delete-apikey` — POST 1 request per second

---

## 覆盖范围与未查到的部分（如实说明取证范围、快照日期、穷尽程度）

**已逐一核验、可称穷尽的部分**
- S1（完整版英文主文档）**全部 395 个 REST 端点声明**：每个都绑定了 method + path + 限额值行 + 计数维度行 + 值行写法 + 端点 `...-http-request` h4 来源锚点，并与 408 条全局值行、406 条维度行对账闭合；无重复、无漏绑。
- S3（01 子集）**全部 141 个声明**同样逐一绑定，复现 01 的 137 / 141 / 135 三个统计数，并定位到 12 个变体写法端点。
- 项目侧：`okx/consts/endpoints/*.py` 全部 279 个赋值、274 个 distinct 路径、5 个多名字共用路径，逐条与官方集合做精确字符串对齐。
- `trade/order` 的 POST + GET 在 **S1 / S2 / S3 / S4 四份**官方页面上逐字比对。
- 官方 Change Log（S5 / S6）的 621 个带日期标题中，检索并核对了全部 `Rate Limit` / `rate limit` / `限速` 相关条目（2026-05-08、2026-06-11、2025-12-10 等）。

**未查到 / 未能穷尽 / 查不到的部分**
- **未做 OKX 全站爬取**。本次只取证了上表 6 个 `docs-v5` 官方 URL。OKX 可能另有独立文档站点（赚币 / 经纪商 / 机构 / 期权做市 / WebSocket 专页等）。因此对问题 4 的 33 个路径，只能说「**在本次取证的 S1 全文里无对应端点详情**」，**不能断言「OKX 官方全网未公布这些端点」**；这一区别对 03 的「官方已公布」口径是实质性的，本文不给结论。
- **中文完整版 S2 有 381 个 distinct 路径，比 S1 的 386 少 5 个**，未逐一比对是哪 5 个、也未能确定原因（可能中文版内容滞后）。S2 仅用于交叉验证数值与写法，未作为清单分母。
- **145 个「仅官方有」路径**（附录 A）只做了与项目常量的**字符串精确匹配**；未逐条核查项目里是否存在「命名不同但语义等价」的别名实现，也未核查这些端点在官方是否标注为 deprecated。
- **33 个「仅项目有」路径**未逐条到 Change Log 或历史版本里追溯是否为已下线 / 改名端点；只确认它们在当前 S1 全文不出现。
- **Change Log 621 个带日期标题**未逐条通读，只检索了限流相关关键字；未穷尽其它可能改动限额的条目。
- **S1 与 S5 在 `POST /api/v5/account/bills-history-archive` 上数值冲突**（主文档 12/day，Change Log 2026-06-11 称改为 1/10s），本次**未查到**主文档同步该变更的证据，也未能判定哪一版为准。
- **页面本身无版本号 / 最后更新日期**（与 01 一致）；全部数值是 **2026-11-06 抓取快照**，未做历史快照对比。Change Log 最新带日期条目为 **2026-10-27**。
- **未复核** 01 已确认的「官方是否有集中限额表」「VIP 分层基准」「表外端点通用政策」等结论（按任务要求不重复查证，直接引用）；本次也未再验证 01 findings 里的 Options 帮助页（01 自己编号的 S5 旁证，与本文 S5=Change Log 不同）等页面。
- WebFetch 未产出有效正文（SPA 只回目录），故全部正文取自媒体 curl 的完整 HTML；未使用 WebSearch 结果作任何结论来源（避免二手转述）。

**覆盖比例总结**：以 S1 完整版为分母，官方 386 个 distinct REST 路径 **100% 逐一核验**（每个都绑定到值行 / 维度 / 来源）；项目 274 个路径 **100% 逐一对齐**。以「OKX 官方全部已发布 API 文档」为分母，本次**未能穷尽**（只覆盖 6 个 docs-v5 URL），故问题 4 的「官方无对应」严格限于本次取证范围。

---

## 对后续决策的输入（只陈述事实含义，不给建议）

- 03 的覆盖验收线「官方已公布限额、且与项目路径常量对应的端点」：在 **S1 完整版口径下对应 241 个路径**（两侧都有）；在 **S3（01）口径下对应 104 个路径**。两者差异来自取证页面覆盖范围，不是端点本身。
- 官方**每一个 REST 端点都给了限额数值**（本次取证范围内 0 个缺失），但数值分散在各端点详情、且写法有 `Rate Limit:` / `Rate limit:` / `Rate limit：` 三种；不存在「官方未公布限额」的 REST 端点这一类别（就本次取证页面而言）。
- 官方一条限额实际含 `(请求数, 时间窗, 计数维度)`，另可能有跟单特例段、子账户限速说明段；时间窗有 second / 2s / 5s / 10s / day / month / UTC 0:00 重置方向性写法；9 个路径同 `path` 有 POST+GET 双声明，其中 5 个数值不同、1 个（`trade/order-algo`）数值同但维度不同。这些是 08 已定「表不承载」的官方事实，本清单是它们在本图内的唯一载体。
- `/api/v5/trade/order` 的 POST + GET **主限额数值与计数维度相同**（60/2s）；08 的「同路径 POST+GET 限额不同则另开新工单」触发条件就该路径而言**未触发**；但 9 个多方法路径里有 5 个数值不同，是并列的事实输入。
- 项目常量里 **33 个路径**在 S1 全文无对应端点详情（按 03 已定归「未收录端点」、维持不限流、不在验收线内）；另 **145 个**官方已公布限额的路径项目没有常量。
- 项目常量 279 个名字 → 274 个路径，5 个路径被 2 个名字共用；274 全是 `/api/v5/` REST 路径，WS 地址另在 `okx/consts/websocket.py`。
- 主文档（S1/S3）与 Change Log（S5）在 `POST /api/v5/account/bills-history-archive` 的限额数值上存在冲突（12/day vs 1/10s），未查到同步证据；取哪个来源、如何留痕会影响「数值来源口径」的判定，本文不下结论。
- 所有数值锚定 **2026-11-06** 快照；页面无版本号，Change Log 最新带日期条目 **2026-10-27**；端点数值在 Change Log 中有被改动的记录（2026-05-08、2026-06-11、2025-12-10 等）。


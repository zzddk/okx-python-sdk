# 01 · OKX 官方限流文档的事实结构（research findings）

调查快照日期：2026-11-06（官方页面当次抓取；WebSearch 结果标注 2026-11-05）。
工单：[01 · OKX 官方限流文档的事实结构](../issues/01-okx-rate-limit-docs.md)。
性质：AFK research，只铺事实；本项目采用哪级账户口径、表外端点默认怎么处置、要不要全量补全端点表，均不在本文范围。

## 取证方法与来源

结论均追到以下 OKX 官方页面（一手来源）：

- **S1** OKX v5 API 主文档（英文）<https://app.okx.com/docs-v5/en> —— `Overview → Rate Limits` 总章节，以及每个 REST 端点详情里的 `Rate Limit:` / `Rate limit rule:` 行。
- **S2** OKX v5 API 主文档（中文）<https://app.okx.com/docs-v5/zh> —— 同一内容中文版，用于交叉验证 `限速:…/限速规则:…` 写法。
- **S3** OKX v5 API Change Log（英文）<https://www.okx.com/docs-v5/log_en> —— 日期化条目与限流变更原文。
- **S4** OKX v5 API Change Log（中文）<https://app.okx.com/docs-v5/log_zh>。
- **S5** OKX Options 帮助页 <http://app.okx.com/help/get-started-with-okx-options> —— 期权做市语境下的单笔/批量/colocation 限额（**帮助页，非 docs-v5 端点详情**，单独标注，仅作旁证）。

取证说明：`app.okx.com/docs-v5/en` 是单页应用，WebFetch 每次只能返回前约 15000 字符（全是目录），端点正文取不到。因此对**同一个官方 URL** 用 `curl` 抓取完整 HTML（当次快照约 2.5 MB），转成纯文本后用脚本把「限流值 ↔ 端点路径」逐一绑定；Change Log 同样取全文。所有数值均来自官方页面原文，未采用任何二手转述。

未采信/排除：`www.oyuzh.net`、`www.okx.vote`、`www.okx.ac` 为非主域镜像（其文案与官方一致，但不作为出处）；`www.okcoin.com/docs-v5/en` 是姊妹站文档；`greatapis.com`、`datawallet.com`、CSDN、gitcode、GitHub 第三方调研等均为二手转述，未作为任何结论的来源。

---

## 1. 官方是否公布一份覆盖全部端点的限流表？还是只有分类规则 / 部分端点示例？

**结论：没有一张集中式的「全端点限额数值表」；数值分散写在每一个端点的详情页里，另有一套分类/维度规则。**

- S1 的 `Rate Limits` 总章节原文：
  > "The rate limit is different for each endpoint. You can find the limit for each endpoint from the endpoint details."

  S2 中文版：「每个接口的限速都不同。您可以从接口详细信息中找到每个接口的限制。」
- 该总章节给出的是**规则分类**而非数值表：
  > "Rate limit definitions are detailed below: WebSocket login and subscription rate limits are based on connection. Public unauthenticated REST rate limits are based on IP address. Private REST rate limits are based on User ID (sub-accounts have individual User IDs). WebSocket order management rate limits are based on User ID."

  以及交易类 API 的共享/独立、Instrument ID（期权为 Instrument Family）、单笔/批量独立、一笔订单最多 3 个在途改单（错误码 51513）等规则。
- 每个端点详情自成一段，格式固定（S1，例）：
  > "Get balance ... Rate Limit: 10 requests per 2 seconds / Rate limit rule: User ID / HTTP Request GET /api/v5/account/balance"
  > "Get instruments ... Rate Limit: 20 requests per 2 seconds / Rate limit rule: User ID + Instrument Type"
- 从 S1 当次全文统计：`Rate Limit:` 标注 137 处、`HTTP Request` 端点块 141 个、distinct REST 路径 135 个。即官方是**逐端点**给值，且几乎覆盖全部 REST 端点，而非一张可整体引用的汇总表。
- 文档另有 `GET / Account rate limit` 端点（S1：「The exchange offers GET / Account rate limit endpoint that provides ratio and rate limit data, which will be updated daily at 8am UTC」），但它返回的是账户当前 fill ratio / 子账户限额，**不是**全端点数值表。
- 超限错误码（S1）：`50011` = "Rate limit reached. Please refer to API documentation and throttle requests accordingly"；子账户超限 `50061`；在途改单过多 `51513`。

（来源：S1 `Overview → Rate Limits` 及各端点详情；S2 同名章节；S1 当次全文统计）

## 2. 限额的单位是什么？窗口长度是否统一？

**结论：单位是「请求数 / 时间窗」，并且每个端点还绑定一个「计数维度」(`Rate limit rule`)；窗口长度不统一，2 秒只是其中一种。**

- 单位写法（S1/S2）：`Rate Limit: N requests per <window>`（中文 `限速:N次/<window>`），紧随一行 `Rate limit rule: <维度>`。因此官方一条限额实际是 `(请求数, 时间窗, 计数维度)`，例 `/api/v5/account/balance` = `10 requests per 2 seconds` + `User ID`。
- 计数维度种类（S1 当次全文统计）：`User ID`（90）、`IP`（27）、`IP + Instrument ID`（4）、`User ID + Instrument ID`（3），以及 `User ID + Instrument Type`、`IP + Instrument Type`、`IP + (Instrument Type + instFamily)`、`IP + (Instrument Family)`、`IP + instFamily`、`User ID + Currency`、`User ID + tag`、`Instrument ID`、`User ID(Private) or IP(Public)` 等。
- **窗口不统一**。S1 当次全文里除大量 `per 2 seconds` 外，还有多种窗口，例：

  | 窗口写法 | 官方端点示例（S1） |
  |---|---|
  | `per second` | `/api/v5/account/bills` = 5 requests per second；`/api/v5/asset/currencies`、`/api/v5/asset/balances` 等 = 6 requests per second；`/api/v5/fiat/*` = 3 requests per second |
  | `per 5 seconds` | `/api/v5/asset/convert/estimate-quote`、`/api/v5/system/status` = 1 request per 5 seconds |
  | `per 10 seconds` | `/api/v5/account/mmp-config` = 2 requests per 10 seconds |
  | `per day` | `/api/v5/account/bills-history-archive` = 12 requests per day |
  | `per month` | `/api/v5/asset/monthly-statement` = 20 requests per month |
  | 复合 | `/api/v5/account/demo-adjust-balance` = "Increase — 3 requests per user per day (resets at UTC 0:00). Reduce — no limit." |

- S3 Change Log 亦印证窗口会变、且并非全是 2 秒：
  - 2026-05-08 `Rate Limit Changes`：「Rate limit of Get the invitee's detail has been changed from 20 requests per 2 seconds to 3 requests per second.」
  - 2026-06-11 `Apply bills details (since 2021): rate limit relaxed`：「...has been changed from 12 requests per day to 1 request per 10 seconds per user.」
- 本项目表现有 8 条恰好都是 2 秒，是因为这 8 个端点本身在官方均为 `per 2 seconds`；**这不是官方统一窗口**。

（来源：S1 各端点详情 + 当次全文统计；S3 2026-05-08、2026-06-11 条目）

## 3. 限额数值是否按账户等级 / VIP 分层？文档以哪一级为基准？

**结论：绝大多数端点（含本项目表内 8 条）的 `Rate Limit: N ...` 是固定数值，不按 VIP 分层，文档也没有声明「以某级 VIP 为基准」；VIP 分层只出现在订单类的「子账户限流 / fill ratio」机制里。**

- 端点详情中的数值（balance/positions/ticker/tickers/books/order 等）均为单一固定值 + `Rate limit rule`，旁边**没有**「VIP1…VIP9 各多少」的等级表，也**没有**「以 Lv1 / VIP1 为准」之类的基准声明。（S1 端点详情；S2 同）
- VIP 分层只出现在 S1 `Rate Limits` 的两个子节：
  - `Sub-account rate limit`：「At the sub-account level, we allow a maximum of 1000 order requests per 2 seconds. Only new order requests and amendment order requests will be counted towards this limit. ... Error code 50061 is returned when the sub-account rate limit is exceeded.」——这是**默认 / Tier 1** 基准。
  - `Fill ratio based sub-account rate limit`：「This is only applicable to >= VIP5 customers.」按过去 7 天成交比率抬高子账户限额；「In the event of client demotion to VIP4, their rate limit will be downgraded to Tier 1」；示例算出 `2500 order requests/2s`、`1750 order requests/2s`。
  - S3（2026-04-07 前后条目）：「Sub-account rate limit defaults to a maximum of 1,000 order and amend requests per 2 seconds. VIP5 and above users can obtain higher rate limits based on fill ratio.」
- S5（Options 帮助页，非端点详情）另述：「Single order rate limit is 60 requests per 2 seconds. Batch order rate limit is 300 requests per 2 seconds. Colocation users have 4 times of the standard limits. For market makers, please contact your account manager ... to raise any rate limit.」——即 colocation / 做市可获更高限额，但这是议价/托管安排，不是按 VIP 等级列在端点详情里的数值。
- 因此：项目注释「higher VIP levels get larger limits, so treat these numbers as a floor」在**普通端点数值**上没有官方依据；官方只在**订单类子账户维度**存在 >=VIP5 的 fill-ratio 上调与 Tier 1 默认，且是 tier / fill-ratio 机制而非「每升一级数值线性变大」。

（来源：S1 `Rate Limits → Sub-account rate limit` / `Fill ratio based sub-account rate limit` 及端点详情；S3 相关条目；S5 6.5 节）

## 4. 官方对「文档未列出限额的端点」怎么表述？

**结论：查不到官方对「未列出限额的端点」的通用表述——官方既没说「不限流」、也没说「归入某个默认类」、也没说「未公布」；它声称每个端点的限额都在各自端点详情里给出。**

- S1 `Rate Limits` 总章节全文没有出现 unthrottled / not limited / default / not published 之类对「缺失端点」的政策性措辞，只有「The rate limit is different for each endpoint. You can find the limit for each endpoint from the endpoint details.」和按 IP / User ID / connection 的分类。
- S1 当次全文统计：137 个 `Rate Limit:` 标注对应 135 个 distinct REST 路径（141 个 `HTTP Request` 块），绝大多数端点都有显式标注；本次未发现成批「未列限额」的 REST 端点（未穷尽逐一核验每个路径，故只作统计性陈述）。
- 官方唯一出现 `no limit` 字样处，是 `POST /api/v5/account/demo-adjust-balance`：「Increase — 3 requests per user per day (resets at UTC 0:00). Reduce — no limit. Rate limit rule: User ID」——这是**针对某个端点的某一操作方向**明确说不限，不是对「文档未列限额端点」的通用政策。
- 需区分：`okx/consts/rate_limits.py` 注释「paths missing from it are not throttled」说的是**本项目表里没收录的路径**，与「OKX 文档未列限额的端点」不是同一对象；本次未在官方找到与该注释对应的表述。

（来源：S1 `Rate Limits` 总章节 + 当次全文统计 + `demo-adjust-balance` 端点详情）

## 5. 文档有没有可引用的版本标识、更新日期或快照日期？

**结论：主文档页没有统一版本号，也没有 "last updated" 标记；官方提供的是按日期组织的 Change Log，可引用的时间锚是条目日期。**

- 对 S1 主文档 `app.okx.com/docs-v5/en` 当次全文检索 `Last updated` / `last updated` / `version:` / `document version` / `Release date` 等，命中均为 0 —— 页面本身没有可引用的版本标识或最后更新日期。
- S3/S4 为独立 Change Log（导航栏 "Change Log"），**无单一文档版本号**，而是按日期倒序的条目；当次快照最靠前的带日期条目为 **2026-10-27**，其上是无日期的 `Upcoming Changes` 区。日期序列示例（S3）：2026-10-27、2026-09-30、2026-09-29、2026-09-15、2026-08-26、2026-08-20 …（更早还有 2025 年条目）。
- Change Log 中有多处限流相关、可作「数值有效期」锚点的带日期条目：2026-06-11（bills-archive 放宽）、2026-05-08（invitee detail 变更）、2025-12-10（Manual borrow rate limit Update）、2026-04-07 前后的 VIP4/VIP5 子账户说明等（S3/S4）。
- 本次调查的**快照日期为 2026-11-06**（官方页面当次抓取；WebSearch 结果标注 2026-11-05）。官方页面内容本身不带抓取日期，故本文数值以此快照为准。

（来源：S1 全文检索；S3/S4 Change Log 目录与条目）

## 6. 现有 8 条路径的数值能否在官方文档里逐条对上？

**结论：8 条数值全部能在 S1 端点详情里逐条对上**（均为 `N requests per 2 seconds`），但官方在这几条上还带有项目表未体现的维度/共享/方法信息。以下为 S1 当次全文逐条提取：

| 路径 | 本项目 `RATE_LIMITS` | S1 官方原文 | `Rate limit rule` | 数值对上 |
|---|---|---|---|---|
| `/api/v5/account/balance` | (10, 2) | `Rate Limit: 10 requests per 2 seconds` | User ID | ✅ |
| `/api/v5/account/positions` | (10, 2) | `Rate Limit: 10 requests per 2 seconds` | User ID | ✅ |
| `/api/v5/trade/order` | (60, 2) | `Rate Limit: 60 requests per 2 seconds` | (except Options) User ID + Instrument ID；(Options only) User ID + Instrument Family | ✅ |
| `/api/v5/trade/cancel-order` | (60, 2) | `Rate Limit: 60 requests per 2 seconds` | 同上 | ✅ |
| `/api/v5/trade/amend-order` | (60, 2) | `Rate Limit: 60 requests per 2 seconds` | 同上 | ✅ |
| `/api/v5/market/ticker` | (20, 2) | `Rate Limit: 20 requests per 2 seconds` | IP | ✅ |
| `/api/v5/market/tickers` | (20, 2) | `Rate Limit: 20 requests per 2 seconds` | IP | ✅ |
| `/api/v5/market/books` | (40, 2) | `Rate Limit: 40 requests per 2 seconds` | IP | ✅ |

S2 中文版写法一致（例：`查看账户余额 … 限速:10次/2s 限速规则:User ID`）。S5 亦给出 "Single order rate limit is 60 requests per 2 seconds" 作为旁证。

数值之外，官方在这几条上还有以下**事实**（项目表当前只有 `(requests, window)` 两元组）：

- **计数维度**：每条端点都带 `Rate limit rule`；trade 三条是 `User ID + Instrument ID`（期权为 `+ Instrument Family`），即 60/2 是**按 instrument** 计，不是该路径的全局 60/2；market 三条按 `IP` 计，account 两条按 `User ID` 计。（S1）
- **下单端点的额外规则**（S1 `Rate Limits → Trading-related APIs` 及 Place/Amend order 端点段）：
  > "Rate limits are shared across the REST and WebSocket channels. Rate limits for placing orders, amending orders, and cancelling orders are independent from each other. ... Rate limits for a multiple order endpoint and a single order endpoint are also independent ..."

  Place order 与 Amend order 段另有 "Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds"，并注明 "Rate limit of this endpoint will also be affected by the rules Sub-account rate limit and Fill ratio based sub-account rate limit"；Cancel order 段无 Copy Trading 特例行。
- **同路径多方法**：`/api/v5/trade/order` 在 S1 中同时出现 `POST`（Place order）与 `GET`（Get order details）两种端点描述，均标 60/2 但 `Rate limit rule` 不同。项目表以 path 为唯一键，不区分 HTTP 方法。（S1）
- S3 Change Log 显示端点数值会随日期变更（见问题 2、5），故上述对上关系是 **2026-11-06 快照**下的对上。

（来源：S1 八个端点详情 + `Rate Limits` 章节；S2 对应中文端点；S3 相关变更条目；S5 6.5 节）

---

## 对后续决策的输入

以下只陈述已查证事实的含义，不含任何口径选择、默认处置或补全范围的建议。

- 官方把限额数值放在**每个端点详情**里，未提供一张可整体引用的集中数值表；官方给的是逐端点数值 + 分类/维度规则 + 交易类特殊规则。
- 官方一条限额含 `(请求数, 时间窗, 计数维度)`；时间窗存在 `per second` / `per 2 seconds` / `per 5 seconds` / `per 10 seconds` / `per day` / `per month` 等多种，2 秒不是统一值。
- 普通端点（含本项目 8 条）的数值在官方为固定值、不按 VIP 分层，文档也未声明基准等级；VIP 分层只作用于订单类子账户维度（默认 1000/2s，>=VIP5 按 fill ratio 上调，VIP4 降回 Tier 1）。
- 官方未对「文档未列出限额的端点」给出通用处置措辞；官方口径是每个端点详情各自给出限额，唯一 `no limit` 字样属于 `demo-adjust-balance` 的 Reduce 操作方向。
- 主文档页无版本号/最后更新日期；可引用的时间锚是 Change Log 的日期条目（当次快照最新带日期条目 2026-10-27）与本次快照日期 2026-11-06；端点数值在 Change Log 中有被改动的记录。
- 本项目 8 条数值与官方 2026-11-06 快照逐条一致；官方在这些端点上另带计数维度、下单类共享/独立/批量/Copy-Trading 规则、以及同路径多方法的区分，这些不在现有 `(requests, window)` 两元组里。

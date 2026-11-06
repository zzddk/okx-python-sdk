# 11 · OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查（research findings）

调查快照日期：**2026-11-06**（当日抓取官方页面，来源见下表）。
工单：[11 · OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](../issues/11-idempotency-and-error-codes.md)。
性质：AFK research，**只铺事实、不下结论**。该不该改集合、该不该翻白名单、要不要 ADR，均不在本文范围（归 04、12、07）。

---

## 取证方法与来源（均为 OKX 官方一手页面，无二手转述 / 镜像站）

| 代号 | 官方 URL | 当次抓取 | 用途 |
|---|---|---|---|
| **S1** | <https://www.okx.com/docs-v5/en/> | 5,280,641 B ≈ 5.28 MB（HTTP 200，完整） | 英文完整版 API 文档，本文主体 |
| **S2** | <https://www.okx.com/docs-v5/zh/> | 4,987,402 B ≈ 4.99 MB（HTTP 200，完整） | 中文完整版，交叉核对措辞 |
| **S3** | <https://www.okx.com/docs-v5/log_en/> | 1,194,560 B ≈ 1.19 MB | 官方 Change Log（最新条目 2026-10-27 + Upcoming） |
| **S4** | <https://www.okx.com/docs-v5/trick_en> | 89,623 B | 官方 Best Practice 页（导航栏 "Best Practice"） |

WebFetch 对这两个单页应用只能取到前部目录，正文取不全；因此对上述 URL 用 `curl --compressed` 抓完整 HTML，转纯文本后检索。S1 转文本后 **1,649,992 字符**，用脚本从「错误码 → HTTP 状态码 → 消息」三行一组解析出 **1,091 行、997 个不重复基础码**；用 `^GET /api/v5/...` 匹配到 **255 个不重复 GET 路径**。关键码另行人工逐字复核，避免启发式解析漏行。

本文所有英文引文逐字取自 S1，中文引文取自 S2；引用锚点均为 S1 页面真实存在的 `href="#..."`。

---

## 1. OKX v5 是否公布过「幂等键 / 客户订单 ID」的完整清单？

### 1.1 没有集中清单，也没有「幂等键」专题页

- S1 全文出现 **idempotency / idempotent** 仅 4 处，全部在两个端点的参数说明里（见 1.3）：`POST /api/v5/finance/flexible-loan/borrow`、`POST /api/v5/finance/flexible-loan/repay`、`POST /api/v5/finance/okusd/subscribe`、`POST /api/v5/finance/okusd/redeem`。
- S1 无「Idempotency」「Client Order ID list」之类的统一章节或下载表；客户端 ID 字段散落在各端点参数表里。
- 因此：**官方没有公布过一份「幂等键完整清单」**。能查到的是「哪些端点有哪些客户端 ID 字段」，且**各字段的语义并不统一**。

### 1.2 官方文档里实际存在的客户端 ID 字段

| 字段 | 出现的端点（请求参数，已逐端点核对） | 官方原文语义 | 是否声明去重 / 幂等 |
|---|---|---|---|
| **clOrdId** | 下单/批量下单/撤单/批量撤单/改单/批量改单/市价平仓；价差下单与撤单；法币买卖；OKUSD 申购/赎回；flexible-loan 借/还（明细见 1.3） | 见 1.3，不同端点措辞不同 | **不统一**：从「无任何去重表述」到「60 秒幂等键」都有 |
| **algoClOrdId** | `POST /api/v5/trade/order-algo`、`cancel-algos`、`amend-algos`；`POST /api/v5/tradingBot/{grid/order-algo, grid/copy-order-algo, dca/create, recurring/order-algo}` | "Client-supplied Algo ID / A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters." [S1 #order-book-trading-algo-trading-post-place-algo-order] | **未声明**唯一性、未声明幂等、未声明重复调用的返回码 |
| **attachAlgoClOrdId** | 普通下单 `attachAlgoOrds` 数组内的附带 TP/SL / 移动止损 | "Client-supplied Algo ID when placing order with attached TP/SL or trailing stop ... It will be posted to `algoClOrdId` when placing the attached algo order once the general order is filled completely." [S1 #order-book-trading-trade-post-place-order] | **未声明** |
| **reqId** | `POST /api/v5/trade/amend-order`、`amend-batch-orders`、`amend-algos`、`POST /api/v5/sprd/amend-order` | "Client Request ID as assigned by the client for order amendment ... The response will include the corresponding reqId to help you identify the request if you provide it in the request." [S1 #order-book-trading-trade-post-amend-order] | **未声明**重复请求行为；WS 侧另有「客户端自行丢弃重复消息」的建议（见 1.3） |
| **clientId** | `POST /api/v5/asset/transfer`、`POST /api/v5/asset/withdrawal`、`POST /api/v5/account/move-positions`、`POST /api/v5/fiat/create-withdrawal`（查询类端点作过滤条件） | "Client-supplied ID / A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters." [S1 #funding-account-rest-api-funds-transfer、#funding-account-rest-api-withdrawal、#trading-account-rest-api-move-positions] | **未声明**去重或幂等 |
| **clRfqId** | `POST /api/v5/rfq/create-rfq`、`cancel-rfq`（查询端点作过滤） | "Client-supplied RFQ ID."；"Either rfqId or clRfqId is required. If both are passed, rfqId will be used." [S1 #block-trading-rest-api-create-rfq] | **未声明** |
| **clQuoteId** | `POST /api/v5/rfq/create-quote`、`cancel-quote`（查询端点作过滤） | "Client-supplied Quote ID."；"This attribute is treated as client sensitive information." [S1 #block-trading-rest-api-create-quote] | **未声明** |

### 1.3 clOrdId 的语义按端点分成三档（逐字引文）

**A. 标准订单（唯一性只在「未成交挂单」范围内）**

> "clOrdId is a user-defined unique order identifier at the User ID level. ... **clOrdId must be unique among all currently pending (live or partially_filled) orders in the account. Once an order reaches a terminal state (filled, canceled, mmp_canceled), the same clOrdId may be reused for a new order. Uniqueness is not enforced historically** — GET /api/v5/trade/order returns only the latest match when multiple orders share a clOrdId."
> — S1 #order-book-trading-trade-post-place-order

> "clOrdId must be unique among all pending orders **and the current request**."（批量下单）
> — S1 #order-book-trading-trade-post-place-multiple-orders

> "clOrdId cannot duplicate any existing clOrdId of all current pending orders."（下单预检）
> — S1 #order-book-trading-trade-post-order-precheck

> "clOrdId must be unique among the clOrdIds of all pending orders."（价差下单）
> — S1 #spread-trading-rest-api-place-order

官方 Best Practice 页把这条讲得更直白：

> "**clOrdId uniqueness check is only applied towards all pending orders.** It is recommended to use a unique clOrdId at all times for troubleshooting etc."
> — S4 <https://www.okx.com/docs-v5/trick_en>（"Placing an order" 节）

即：**clOrdId 不是跨终态的幂等键**。订单一旦 filled / canceled，同一个 clOrdId 可以再下一单；官方还明说历史唯一性不做校验。

**B. 唯一明确写成「幂等键」的端点（仅 2 组）**

> "Client-defined order ID. Maximum 32 characters (letters, digits, -, _). **Must be unique per UID. Used for order tracking and idempotency**"
> — OKUSD 申购与赎回的 clOrdId（必填），S1 #financial-product-okusd-post-subscribe-okusd、#financial-product-okusd-post-redeem-okusd

> "Client-supplied ID. **The idempotency key is scoped to the UID and endpoint path. It is retained for 60 seconds; a completed duplicate returns 51016, and an in-flight duplicate returns 51784.**"
> — flexible-loan 借款与还款的 clOrdId（必填），S1 #financial-product-flexible-loan-post-borrow、#financial-product-flexible-loan-post-repay

**C. 其余端点只写「客户端订单号」，不写唯一性也不写去重**

- 市价平仓：clOrdId 描述仅为 "Client-supplied ID / ... up to 32 characters" — S1 #order-book-trading-trade-post-close-positions
- 法币买卖：clOrdId 描述仅为 "Client Order ID as assigned by the client / ... up to 32 characters"（必填）— S1 #funding-account-rest-api-buy-sell-trade
- 撤单 / 改单：clOrdId 作为定位键（"Either ordId or clOrdId is required"），无幂等表述 — S1 #order-book-trading-trade-post-cancel-order、#order-book-trading-trade-post-amend-order

**D. reqId 的「去重」只出现在 WS 订单频道的消费建议里，不是 REST 请求保证**

> "If `reqId` is present, it indicates a response to a user-requested order modification. It is recommended to use a unique `reqId` for each modification request. **For modification messages with the same `reqId`, process only the first message received and discard subsequent messages.**"
> — S1 #order-book-trading-trade-ws-order-channel

### 1.4 与重复请求有关的官方错误码

| 码 | HTTP | 官方消息 | 出处 |
|---|---|---|---|
| 50071 | 200 | `{param} already exists`（表内举例 `e.g. clOrdId already exists`） | S1 #error-code-rest-api |
| 51016 | 200 | `Client order ID already exists.` | S1 #error-code-rest-api |
| 51784 | 200 | `Client order ID is being processed` | S1 #error-code-rest-api |
| 50042 | 200 | `Repeated request` | S1 #error-code-rest-api |

官方没有解释 50071 / 50042 与 51016 / 51784 的适用边界，只能从消息文本区分。

### 1.5 对问题 1 的事实回答

- 官方**没有**「幂等键完整清单」；「幂等」字样只出现在 flexible-loan 与 OKUSD 四个端点。
- 除 `clOrdId` / `algoClOrdId` / `reqId` 外，官方文档确实还有 **`attachAlgoClOrdId`、`clientId`、`clRfqId`、`clQuoteId`** 四个客户端 ID 字段；`clientId` 覆盖的正是提币、划转、移动仓位、法币提币这些资金类写操作。
- 这些字段**语义不统一**：只有 flexible-loan 写明「幂等键 + 60 秒保留 + 51016/51784」，OKUSD 写明 "used for ... idempotency"，其余均无去重保证；标准订单的 clOrdId 只在 pending 范围内唯一。

---

## 2. 50001 / 50004 / 50011 / 50013 的官方含义，以及 transport.py 注释是否与官方一致

### 2.1 官方原文（S1 错误码表 + S2 中文对照）

| 码 | HTTP | 官方英文（S1） | 官方中文（S2） |
|---|---|---|---|
| 50001 | 503 | Service temporarily unavailable. Please try again later. | 服务暂时不可用，请稍后重试 |
| 50004 | 400 | API endpoint request timeout. (does not mean that the request was successful or failed, please check the request result). | 接口请求超时（不代表请求成功或者失败，请检查请求结果） |
| 50011 | 200 | Rate limit reached. Please refer to API documentation and throttle requests accordingly. | 用户请求频率过快，超过该接口允许的限额。请参考 API 文档并限制请求 |
| 50011 | 429 | Too Many Requests | 请求频率太高 |
| 50013 | 429 | Systems are busy. Please try again later. | 当前系统繁忙，请稍后重试 |

出处：S1 <https://www.okx.com/docs-v5/en/#error-code-rest-api>（General Class）；S2 <https://www.okx.com/docs-v5/zh/#error-code-rest-api>。

注意两个结构事实：

1. **同一个业务码可以对应多个 HTTP 状态**：50011 同时登记为 200 与 429。业务码与 HTTP 状态是两层，不是一对一。
2. 50004 的 HTTP 状态是 **400**（不是 5xx），50001 是 503，50013 是 429。

### 2.2 与 `okx/transport.py:22-24` 注释的对照

注释原文（`okx/transport.py:22-24`）：

> "Business codes worth retrying: the request was **rejected before it could be matched, so replaying it cannot double-execute**."

逐码核对：

| 码 | 官方是否说「请求未被撮合 / 未被处理」？ | 结论 |
|---|---|---|
| 50001 | 只说「服务暂时不可用，请稍后重试」，**未说明请求是否已被受理** | 相容，但**无官方依据** |
| 50004 | 官方明说「**不代表请求成功或者失败，请检查请求结果**」 | **相反**：官方明确结果是未知的，不能断言「不会重复执行」 |
| 50011 | 只说「触发限流」，**未说明是否已进入撮合** | 相容，但**无官方依据** |
| 50013 | 只说「系统繁忙」，**未说明是否已进入撮合** | 相容，但**无官方依据** |

补充事实：即使请求带 `clOrdId`，官方也只保证「未成交挂单范围内唯一」，终态后允许复用（1.3 A）。因此「重放不会重复执行」在官方文本里**没有任何一条能覆盖 50004**；对 50001/50011/50013 也只是「不矛盾」，不是「官方这样定义」。

### 2.3 对问题 2 的事实回答

- 四个码的官方含义如上表，均为**服务端 / 限流侧**的消息，不含「未被撮合」的表述。
- 注释里的「rejected before it could be matched」**不是官方说法**；对 50004 而言与官方原文**直接冲突**（官方说结果未知）。
- 官方另有 `51149`（"Order timed out. Please try again. (does not mean that the request was successful or failed, please check the request result)"）用同样的「结果未知」措辞，说明这类「超时」在官方口径里属于**结果不确定**，不是「确定未执行」。

---

## 3. 官方是否还公布其他「瞬时 / 可重试」业务码？51000 的分类有依据吗？

### 3.1 官方没有「可重试 / 不可重试」分类

- S1 全文检索 `retry` / `retries` / `retrying`，只命中 4 条错误消息（`System maintenance, please retry` 等），**没有任何一段重试策略说明**。
- 错误码表只有三列：`Error Code` / `HTTP Status Code` / `Error Message`，**没有「是否可重试」列**，也没有「瞬时错误」章节。
- 因此「哪些码可重试」在官方文档里**查不到分类**，只能从消息语义与 HTTP 状态推断。

### 3.2 官方错误表里所有带 5xx 的码（共 7 个）

| 码 | HTTP | 官方消息（S1） |
|---|---|---|
| 50001 | 503 | Service temporarily unavailable. Please try again later. |
| 50026 | 500 | System error. Try again later |
| 51054 | 500 | Request timed out. Please try again. |
| 51149 | 500 | Order timed out. Please try again. (does not mean that the request was successful or failed, please check the request result) |
| 52910 | 500 | Service unavailable, please try again later |
| 52911 | 500 | RFQ service unavailable, please try again later |
| 52912 | 500 | Server timeout |

### 3.3 官方错误表里所有带 429 的码（共 5 个）

| 码 | HTTP | 官方消息（S1） |
|---|---|---|
| 50011 | 429 | Too Many Requests |
| 50013 | 429 | Systems are busy. Please try again later. |
| 51113 | 429 | Market-price liquidation requests too frequent. |
| **51115** | **429** | **Cancel all pending close-orders before liquidation.** |
| 58102 | 429 | Rate limit reached. Please refer to API docs and throttle requests accordingly. |

**关键反例：51115 是 429，但消息是确定性业务条件（「先撤销所有待平仓委托」），不是「稍后重试就会好」。** 这说明官方层面 **HTTP 429 并不等价于「瞬时 / 可重试」**。

### 3.4 消息带「try again later / temporarily unavailable / busy」的其他码（举例，非穷尽）

50040（Too frequent operations, please try again later）、50046、50057、50064、51767（System maintenance, please retry）、51739、51759、52923（Service unavailable. Try again later.）、52924（Too many orders）、51290（The Bot engine is being upgraded）、70208（Cancellation failed as service is unavailable）、58120、59119、59120、58310 等。

这些码的「稍后重试」多数依赖业务状态（维护、ADL、风控、bot 升级），**官方没有把它们归为「瞬时故障」**，也没有说明重试是否安全。

### 3.5 51000 的含义与「永不重试」分类

官方原文（S1 #error-code-rest-api，General Class / Trade Class）：

- `51000 | 400 | Parameter {param0} error`
- 端点级错误表里另有 `51000 | 200 | Parameter error`、`51000 | 400 | Parameter {param} error. This would also be returned when a grid bot does not support the parameter`（如 GLP、Grid 端点自己的 Error Code 表）

即 **51000 = 参数错误**，是调用方输入问题，不是服务状态。事实层面：

- **「51000 永不重试」这一分类在官方文档里查不到**；官方没有「可重试 / 不可重试」标签。
- 但从消息语义看，「参数错误」属于确定性拒绝，与 `CHANGELOG.md:330` 的用法一致；这属于**合理推断**，不是官方明文。
- 另一个细节：51000 的 HTTP 状态并不固定为 400（端点级表里有 200 的写法），所以用「HTTP 4xx = 确定性」也不成立。

### 3.6 对问题 3 的事实回答

- 官方**没有**公布「瞬时 / 可重试」分类；可查到的是逐码的消息与 HTTP 状态。
- 官方另有 6 个 5xx 码（50026、51054、51149、52910、52911、52912）与多个 "try again later" 语义的码，都不在项目的 `_RETRYABLE_CODES` 里。
- 51000 的「确定性参数错误」语义与官方消息一致，但「永不重试」这个**分类**没有官方依据。
- 51115（429 + 确定性消息）表明「HTTP 状态 → 可重试」在官方层面也不成立。

---

## 4. 有没有 GET 端点其实带副作用或改变服务端状态？

### 4.1 扫描口径

- 从 S1 抽出 **255 个不重复 `GET /api/v5/...` 路径**（含公有与私有）。
- 对每个 GET 所在端点块，取标题 + 描述段（`HTTP Request` 之前的文本）与请求参数表，检索 `create / cancel / close / activate / modify / update / delete / redeem / subscribe / trigger / settle / reset / generate / initiate / change` 等动作词。
- 命中的全部是**名词或响应字段**（如 `canceled` 订单状态、`created` 时间、`redeemed` 状态、`updated` 时间、`triggered` 状态），**没有一条 GET 的描述写「本端点会创建 / 取消 / 修改 / 触发 …」**。
- 全库检索 `will be created` / `automatically create` 也无命中。

### 4.2 唯一可疑点：`GET /api/v5/asset/deposit-address`

- 端点描述只有："Retrieve the deposit addresses of currencies, **including previously-used addresses**."（S1 #funding-account-rest-api-get-deposit-address）；中文同为「获取各个币种的充值地址，包括曾使用过的老地址。」（S2）。
- **正文没有写「地址不存在时会创建」**。
- 但官方错误码表存在 `58310 | 200 | Unable to create new deposit address, try again later`（中文「无法创建新的充币地址，请稍后重试」），且全文档只有这一个充值地址端点。
- 因此：**「该 GET 在地址不存在时会创建地址」是从错误码反推的推断，不是文档明示**；文档也没有说明重复调用是否返回同一地址、是否幂等。
- 即便该推断成立，它改变的是「地址簿」而非资金 / 订单状态；重放是否安全，官方未表态。

### 4.3 官方是否声明「GET 无副作用」

**没有。** S1/S2/S4 均无「GET 是安全方法 / 可安全重放」的表述；也没有「GET 不改变服务端状态」的通用条款。ADR-0003 的「GET 一律可重试」在官方文档里**找不到对应的公理**。

补充两个「非业务写入但确实发生」的事实：

- 每个 GET 都消耗限流配额（端点详情有 `Rate Limit:` 行），即 GET 会改变服务端的限流计数。
- 部分行情 GET 明确说返回的是服务端缓存（如 `GET /api/v5/market/books`："returns the latest data once the server-side cache has been updated"），读取本身会触达缓存，但这不构成业务状态变更。

### 4.4 对问题 4 的事实回答

- 在 255 个官方 GET 路径中，**没有一条被官方描述为会改变订单 / 资金 / 账户状态**。
- 官方**从未**声明 GET 一律无副作用；这是项目的建模前提，不是 OKX 公布的事实。
- 唯一有间接证据的候选是 `GET /api/v5/asset/deposit-address`（错误码 58310 提到「创建充值地址」），但文档未明示、也未说明其幂等性。

---

## 5. HTTP 429 / 5xx 与业务码同时出现时，官方是否说明优先级？

### 5.1 查不到优先级说明

- S1/S2 检索 `priorit` / `优先级` / `HTTP status` / `status code` / `5xx`，没有「先看 HTTP 状态还是先看业务码」的表述。
- 错误码表只是并列两列（`Error Code` / `HTTP Status Code`），没有「当两者同时出现以谁为准」的脚注。
- 限流章节只说："When a request is rejected by our system due to rate limits, the system returns error code 50011 (Rate limit reached...)."（S1 "Rate Limits" 节），未说此时 HTTP 状态是什么。

### 5.2 官方给出的结构事实

| 事实 | 出处 |
|---|---|
| 业务码与 HTTP 状态是多对多：50011 同时是 200 与 429；51000 在不同端点表里既是 400 也是 200 | S1 #error-code-rest-api 及各端点 Error Code 表 |
| 50013 固定 429、50001 固定 503、50026 固定 500 | S1 #error-code-rest-api |
| 所有 7 个 5xx 码的消息都是「服务不可用 / 超时 / 稍后重试」类，未见「参数错误」类码配 5xx | 3.2 表 |
| 存在 429 + 确定性消息的反例 51115 | 3.3 表 |
| 未见任何「HTTP 429 一定可重试」或「业务码优先于 HTTP 状态」的说明 | 全文检索无命中 |

### 5.3 对问题 5 的事实回答

- **官方没有说明优先级**。
- 可以确定的只有：业务码与 HTTP 状态是两层独立信息，官方不保证一一对应；429 不必然代表可重试（51115），5xx 在现有表里都伴随「稍后重试」类消息。
- 项目 `_is_transient` 的「429/5xx 优先、再看业务码」是**项目自己的判定顺序**，官方既未背书也未反对。

---

## 覆盖范围与未查到的部分

**已覆盖**

- S1 完整英文文档（5.28 MB HTML → 1.65 M 字符）：错误码表 **1,091 行 / 997 个基础码**全部解析；**255 个 GET 路径**逐一扫描述与参数。
- S2 中文文档：仅用于交叉核对 4 个目标错误码、deposit-address 描述、幂等相关措辞（未逐条比对全表）。
- S3 Change Log（2026-10-27 为最新条目）：检索 `clOrdId` / `algoClOrdId` / `idempot` / `51016` / `51784` / `50004`，未发现与幂等语义或这四个码相关的变更说明。
- S4 Best Practice 页：确认 clOrdId 唯一性只作用于挂单。
- 1.2 表中的每个字段都按「请求参数表」解析后逐端点确认，不是全文关键字命中。

**明确查不到 / 无法核验**

1. **官方幂等键完整清单**：不存在。官方只有分散的字段说明，且语义不一。
2. **官方「可重试 / 不可重试」分类**：不存在。只有消息与 HTTP 状态。
3. **HTTP 429/5xx 与业务码的优先级**：官方无任何说明。
4. **GET 副作用**：官方无「GET 无副作用」声明；deposit-address 是否创建地址只有错误码 58310 的间接证据，未获文档明示。
5. **运行时行为**：未发任何真实 API 请求（无凭证），因此「50011 在 429 响应里是否也带 body code」「deposit-address 重复调用是否返回同一地址」等只能靠文档、无法实证。
6. **错误码表解析的覆盖边界**：三行一组的启发式解析可能漏掉格式异常的表格行；已对本文引用的所有码人工复核，但未对 997 个码逐一人工确认。
7. **WebSocket 错误码与 WS 重试语义**：仅顺带核到 `reqId` 的 WS 消费建议，未系统核查 WS 错误码表（不在本工单 5 问范围内）。
8. **官方 Agent / Broker 专页、历史版本文档**：未查。S1 之外是否有更全的字段说明，未验证。
9. **其他可能带副作用的 GET**：只覆盖 S1 已公布的 255 个 GET；未公开端点或未文档化行为无法核查。

---

## 对后续决策的输入（只陈述事实含义，不给建议）

- `_IDEMPOTENCY_KEYS` 目前只有 `clOrdId` / `algoClOrdId` / `reqId`；官方文档里另有 **`attachAlgoClOrdId`、`clientId`（提币 / 划转 / 移动仓位 / 法币提币）、`clRfqId`、`clQuoteId`** 四类客户端 ID。
- 官方唯一写明「幂等键」的是 **flexible-loan 借 / 还**（UID + 路径维度、保留 60 秒、重复返回 51016/51784）与 **OKUSD 申购 / 赎回**（"used for order tracking and idempotency"）。
- 标准订单的 `clOrdId` 只在 **pending 未成交**范围内唯一，**终态后允许复用**，且官方明说历史唯一性不校验；因此「带 clOrdId 的重放不会重复下单」在官方文本里**不成立**。
- `50004` 的官方消息明确写「**不代表请求成功或者失败**」；`51149` 同样措辞。二者都属于「结果未知」，与 `transport.py:22-24` 的「rejected before it could be matched」相反。
- 官方错误表里带 5xx 的码共 7 个，除 50001 外还有 **50026 / 51054 / 51149 / 52910 / 52911 / 52912**；另有大量 "try again later" 语义的 200 码。
- `51000` 官方含义是参数错误（HTTP 400，个别端点表为 200）；「永不重试」没有官方分类依据，但与「参数错误」语义相容。
- `51115` 是 **HTTP 429 + 确定性业务条件**；说明「HTTP 429 ⇒ 可重试」在官方层面不成立。
- 官方没有「GET 无副作用」的公理；255 个 GET 路径中未发现被描述为写操作的端点，`GET /api/v5/asset/deposit-address` 是唯一有间接证据（错误码 58310）的候选。
- 官方没有 429/5xx 与业务码的优先级说明；两者是多对多关系（50011 同时是 200 与 429），项目的「状态优先」是本地策略。

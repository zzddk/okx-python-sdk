# 09 · 官方已公布限额的端点清单与 274/135 差异核对

Type: research
Status: resolved
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

findings 落在 throwaway 分支 `research/official-limit-endpoint-list` 上的 `.scratch/rate-retry-policy/research/official-limit-endpoint-list.md`（commit `805528e`，877 行）；按 wayfinder 约定永不合并，沿用本地保留决定、不 push。

> **来自 08 的输入（2026-11-06）**：[限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 已定**保持二元组 + `path` 单键、表不承载计数维度 / 窗口语义 / 多方法 / REST-WS 共享**。因此本工单的清单是这些官方事实的**唯一载体**：解 09 时把「路径 + 限额数值 + 时间窗 + 计数维度 + 多方法区分 + 来源页」逐条列全，尤其标出同路径多方法（`/api/v5/trade/order` 的 POST + GET）限额是否不同——若不同，是 08 触发条件里「另开新工单」的输入。

> **来自 10 的输入（2026-11-06）**：[官方 Change Log 变更时表怎么同步](10-changelog-sync.md) 已定本工单的清单是**一次性事实输入、不是长期维护对象**：findings 留在 throwaway 分支（永不合并、不 push），解 09 时按 08 的要求把字段列全即可，不必设计成可长期维护的结构。长期维护以官方 Change Log + 端点详情页为唯一外部来源，每次同步重新取证并在 PR / CHANGELOG 留痕；不随表同步更新本清单、也不把分支合并进 master。

## Answer

事实已由 AFK research 子代理查回，全文见 Context 段所指分支（commit `805528e`）。**结论：清单已做实，且发现 01 的取证页面只是子集。**

**最重要的取证发现**：01 取证的 `app.okx.com/docs-v5/en`（S3）只有 **135 distinct REST 路径 / 141 声明 / 10 业务段**；完整版 `www.okx.com/docs-v5/en`（S1）有 **386 distinct REST 路径 / 395 声明 / 16 业务段**（含 `finance`、`tradingBot`、`rfq`、`rubik`、`sprd`、`copytrading` 等 S3 完全没有的段）。逐条比对：S3 的 135 个路径**全部**在 S1 内（`S3 - S1 = 0`），且共同路径的限额数值**零差异**；01 的 `137 / 141 / 135` 三个统计数在 S3 上本次全部复现。因此 S1 是同一套官方文档的更全版本，不是另一套数值——**01 的定性结论成立，但「135」是子集口径，不是官方全量**。这也是 274 与 135 差距的大头。

1. **清单**：以 S1 完整版为准，395 个 REST 声明 / 386 distinct 路径 / 408 条限额值行，**100% 逐一绑定**（路径 + 方法 + 数值 + 时间窗 + `Rate limit rule` 计数维度 + 多方法区分 + 值行写法 + 来源页锚点），主表 395 行逐条列全，408 条值行对账闭合（397 归 REST 声明、11 归 WS 端点）；中文完整版 S2 交叉验证。快照 2026-11-06。
2. **对齐**：S1 完整版口径 **两侧都有 241 / 仅官方 145 / 仅项目 33**；S3 口径为 **104 / 31 / 170**。项目 279 个常量名 → 274 个路径，其中 5 个路径被两名共用（含 `trade/order`）。
3. **274 vs 135 差异**：主因是**取证页面覆盖范围**（换成 S1 后「仅项目有」从 170 降到 33，137 个端点是 S1 有而 S3 无）；别名 5、多方法 S1 9 个 / S3 6 个、非 REST 0（274 全是 `/api/v5/...`，WS 在 `websocket.py`）、本页未收录 33。
4. **官方无对应端点**：S1 口径 **33 个**，逐一列出（这些路径在 S1 全文连路径串都不出现）；按 03 归「未收录端点」、维持不限流。
5. **无 `Rate Limit:` 行的端点**：逐一核验 **0 个** REST 端点缺失——但 12 个端点用变体写法 `Rate limit:` / 全角 `Rate limit：`，01 的「137」只数了标准写法；唯一无计数维度行的是 `/api/v5/system/status`；另有 11 个 WS 端点有值行但非 REST。
6. **08 的触发条件**：08 特指的 `/api/v5/trade/order` POST + GET **数值相同**（S1/S2/S3/S4 四份官方页面一致，均 `60 requests per 2 seconds`、维度也相同），该特指**未触发**。但 S1 的 9 个同路径多方法里有 **5 个数值确实不同**（`bills-history-archive`、`mmp-config`、`monthly-statement`、`rfq/mmp-config`、`users/subaccount/apikey`），4 个相同；`/api/v5/trade/order-algo` 数值相同但计数维度不同。08 的答案留的是泛指条件「09 若查出同路径多方法限额不同 → 新开工单、不重开 08」，故按步骤 5 **新开 [同路径多方法限额不同怎么处理](14-multi-method-limits.md)**（grilling，blocked by 09）。
7. **额外事实冲突**：`bills-history-archive` 主文档为 `12 requests per day`，而 Change Log 2026-06-11 记载改为 `1 request per 10 seconds per user`；本次未查到同步证据、**未能判定哪一版为准**。按 10 已定的流程「每次同步重新取证」处理，09 不判定。

**未查到 / 未能穷尽**：未做 OKX 全站爬取（只取 6 个 `docs-v5` URL），因此**不能断言**那 33 个路径「官方全网无文档」，只能说本次取证页面内无对应；中文完整版 381 vs 英文 386 差 5 个未比对原因；145 个「仅官方有」未逐条核查项目等价别名 / deprecated；33 个未追历史版本；Change Log 621 个带日期标题只检索了限流关键字、未逐条通读；页面无版本号 / 最后更新日期，全部数值为 2026-11-06 快照；`bills-archive` 冲突未查到同步证据；按任务要求未复核 01 已确认的结论。WebFetch 因 SPA 只回目录，正文改用 curl 取完整 HTML，**未用任何二手来源**。

来源全部为 OKX 官方一手页面 S1–S6（`www.okx.com/docs-v5/en|zh`、`app.okx.com/docs-v5/en|zh`、`www.okx.com/docs-v5/log_en`、`app.okx.com/docs-v5/log_en`）。

## 边界（口径修正与事实含义）

- **01 的「135 / 137 / 141」是 `app.okx.com` 子集口径，不是官方全量**；01 的定性结论（无集中限额表、逐端点给值、窗口不统一、普通端点不按 VIP 分层、现有 8 条数值对得上）在 S1 上依然成立，**不重开 01**（结论未被推翻，只是补了取证范围）。口径说明已写进地图 Notes。
- **03 的验收线措辞不变**——「官方已公布限额、且与项目路径常量对应的端点」；但「官方已公布」的实际规模是 S1 的 386 路径 / 395 声明，两侧都有的是 **241**（不是 135）。03 已 resolved、决策未变，不重开；此数字作为 spec 第 ② 节判定规则与施工取数的输入。
- 09 是 AFK research，只铺事实 → **无公开面变化、不建 ADR、不写 `### Migration` 行**；不回答该不该补全、补全到什么程度、表条目形状、清单怎么维护（归 03 / 08 / 10 / 14）。
- 本清单是**一次性事实输入**（10 已定），留在 throwaway 分支、不长期维护、不合并进 master。
- **不收图**：09 resolved 后还有 11（AFK research）、12（被 11 阻塞）、14（新开）三张 open；09 不代解、不触发第二个子代理。
- 本图只决策，不改 `okx/consts/rate_limits.py` / `okx/consts/endpoints/`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（AFK research，由 fresh-context 子代理调用 `/research` 完成；findings 落 `research/official-limit-endpoint-list` @ `805528e`，本地保留、不 push）。

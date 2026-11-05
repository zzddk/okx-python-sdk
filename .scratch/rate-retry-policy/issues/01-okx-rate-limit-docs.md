# 01 · OKX 官方限流文档的事实结构

Type: research
Status: resolved
Blocked by: —

## Question

把 OKX v5 REST 官方限流文档的**事实**铺开，供后续口径与表覆盖决策使用。只查证、不下结论、不替项目定口径。具体要回答：

1. 官方是否公布一份覆盖全部 REST 端点的限额表？还是只给出分类规则 / 部分端点示例？
2. 限额以什么单位给出：请求数 / 时间窗，还是别的？窗口长度是否统一（现有表 8 条全部写的是 2 秒）？
3. 限额数值是否按账户等级 / VIP 分层？若分层，文档把哪一级作为基准？
4. 官方对「文档未列出限额的端点」是怎么表述的——不限流、归到某个默认类、还是未公布？
5. 文档有没有可引用的版本标识、更新日期或快照日期？
6. 现有表里的 8 条（`/api/v5/account/balance`、`/api/v5/account/positions`、`/api/v5/trade/order`、`/api/v5/trade/cancel-order`、`/api/v5/trade/amend-order`、`/api/v5/market/ticker`、`/api/v5/market/tickers`、`/api/v5/market/books`）数值能否在官方文档里逐条对上？

每一条结论都要追到拥有它的官方来源（OKX docs-v5 或官方公告），不要引二手转述；查不到就写明查不到，不要编造数值。

**不回答**：本项目该采用哪一级账户口径、表外端点默认怎么处置、要不要全量补全——那是 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 与 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 的决策。

## Context

findings 落在 throwaway 分支 `research/okx-rate-limit-docs` 上的 `.scratch/rate-retry-policy/research/okx-rate-limits-docs.md`；该分支按 wayfinder 约定永不合并。

## Answer

事实已由 AFK research 子代理查回，全文见上方 Context 段所指分支（commit `57e08ab`）。要点：

- **没有全端点集中限额表**：官方把数值分散在各端点详情页——「The rate limit is different for each endpoint. You can find the limit for each endpoint from the endpoint details.」全文约 137 处 `Rate Limit:` 对应 135 个 REST 路径。
- **单位与窗口不统一**：单位是「请求数 / 时间窗」，每行另带 `Rate limit rule` 计数维度（User ID / IP / +Instrument ID 等）；窗口存在 per second / 2s / 5s / 10s / day / month，2 秒只是多数，Change Log 里也有 `20/2s → 3/second` 的改动。
- **普通端点不按 VIP 分层**：这 8 条是固定值，文档未声明基准等级；VIP 只作用于订单类的「子账户限流 / fill ratio」（默认 1000/2s，≥VIP5 按成交比率上调）。`rate_limits.py` 注释里「VIP 越高限额越大、当 floor」对普通端点没有官方依据。
- **表外端点**：官方查不到通用政策表述（既未说不限流、也未说归默认类 / 未公布），口径是「每个端点详情各自给值」。
- **无统一版本号 / 最后更新日期**：主文档页查不到；可引用的是按日期倒序的 Change Log（最新带日期条目 2026-10-27）。本次快照日期 2026-11-06。
- **现有 8 条数值全部与官方对上**，但官方还带项目表没有的信息：trade 三条按 `User ID + Instrument ID` 计、Place/Amend 有 Copy-Trading 4/2 特例、REST 与 WS 共享限额、place/amend/cancel 相互独立、`/api/v5/trade/order` 同路径有 POST + GET 两个方法。

未查到 / 未确认：官方对「未列限额端点」的通用政策；主文档页的统一版本号或最后更新日期；未逐一核验全部约 135 个 REST 路径是否每一个都带 `Rate Limit:` 行（只做了统计性陈述）。

来源全部为 OKX 官方 `app.okx.com/docs-v5/en|zh`、`www.okx.com/docs-v5/log_en` 及中文 `log_zh`；镜像站与二手转述未采信。三个 HITL 决策（账户层级口径、表外默认处置、是否全量补全）按分工未在此回答，留给后续工单。

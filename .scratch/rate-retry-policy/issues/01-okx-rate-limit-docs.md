# 01 · OKX 官方限流文档的事实结构

Type: research
Status: open
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

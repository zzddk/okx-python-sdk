# 03 · 表外端点怎么处置、表要不要全量补全

Type: grilling
Status: open
Blocked by: 02

## Question

`RATE_LIMITS` 现在只有 8 条，`okx/consts/endpoints/` 去重后约 274 个 `/api/v5/...` 路径在表外且不限流（`okx/consts/rate_limits.py` 与 README.md:113 都把这条写成了免责声明）。在 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 的口径之下拍板：

1. 表外端点：继续「不限流」并保留 README 免责声明，还是按 02 定的兜底值统一限流？
2. 「全量补全」是**图内要做的决策**，还是明确留作图外施工？若留作施工，spec 里要写到什么程度——给判定规则即可，还是要给出最终表？
3. 若官方只公布了部分端点（[OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 的事实），「覆盖」的验收线按「官方已公布的」还是「全部端点」？
4. 表的维护成本：新增端点时谁负责补表？要不要一个测试断言「每个端点路径都在表里或显式豁免」？

注意：本图只决策，不动 `okx/consts/rate_limits.py`；补全 274 条是图外施工。

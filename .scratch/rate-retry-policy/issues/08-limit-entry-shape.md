# 08 · 限额表条目要不要容纳计数维度与任意窗口

Type: grilling
Status: open
Blocked by: 02

## Question

[OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 的 findings 表明，官方一条限额是三元组 `(请求数, 时间窗, 计数维度)`：窗口有 `per second` / `2s` / `5s` / `10s` / `per day` / `per month`，部分按 UTC 0:00 重置；计数维度有 `User ID`、`IP`、`User ID + Instrument ID` 等；`POST /api/v5/trade/order` 同路径还挂着 POST + GET 两个方法，且 REST 与 WS 共享限额、place/amend/cancel 相互独立。而 `RATE_LIMITS` 现在只有二元组 `(requests, window_seconds)`，8 条窗口全写 2 秒；`okx/rate_limit.py:28` 的 `count, window = limit` 按 path 计数，不区分方法与维度。

[采用哪个账户层级口径与文档快照](02-limit-scope.md) 定下了数值口径（取官方端点详情页固定值），但没定表的**条目形状**。要拍板：

1. `RATE_LIMITS` 的 value 要不要从二元组升级成能表达计数维度与窗口语义的形状？还是保持二元组、把差异只写在文档里？
2. key 要不要从 `path` 变成 `(method, path)`？`/api/v5/trade/order` 的 POST 与 GET 是否共用一个配额？
3. 非 2 秒窗口怎么表达：`per day` / `per month` / `per second` 直接写成秒数（86400 / 2592000 / 1）即可，还是需要「UTC 0:00 重置」的固定窗口语义？后者是 [限流器形态与共享边界](06-limiter-shape.md) 的滑动窗口表达不了的，解本工单时若 06 已 resolved 则 zoom 它。
4. REST 与 WS 共享限额要不要在本表体现，还是明确留给 WS effort（地图 Out of scope 已把 WS 限速排除）？
5. 升级是否构成公开面变化（`RATE_LIMITS` 是 `okx.consts` 下可导入的常量），要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`？

只决策条目形状，不改 `okx/consts/rate_limits.py` / `okx/rate_limit.py`。

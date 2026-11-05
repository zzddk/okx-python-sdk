# 06 · 限流器形态与共享边界

Type: grilling
Status: open
Blocked by: 02

## Question

`okx/rate_limit.py` 的 `RateLimiter` 是 per-path 独立滑动窗口、`time.sleep` 阻塞调用线程、`Transport` 自带一个实例（多个 API 类共享同一 `Transport` 就共享同一 limiter）。在 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 的窗口口径下拍板：

1. 「同一路径跨多个 `Transport` 实例」要不要共享限流状态？现状是各算各的——若用户建两个 Transport 打同一账户，会不会超额？
2. `sleep` 阻塞是否可接受？要不要注入异步等待 / 让调用方自己选？注意 `Transport` 用的是同步 httpx 客户端。
3. 窗口边界要与 OKX 的窗口对齐（固定窗口）还是保持滑动窗口？两者在突发流量下的行为差别要不要写进决策。
4. limiter 是否需要可观测（当前用量、被拒次数）？还是保持纯数据、不引入状态查询接口。

只决策形态，不改 `okx/rate_limit.py`。

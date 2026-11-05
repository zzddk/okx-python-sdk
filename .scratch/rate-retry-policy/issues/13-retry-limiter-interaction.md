# 13 · 重试与限流器的交互要不要改

Type: grilling
Status: open
Blocked by: 06

## Question

由地图 Not yet specified 的「限流与重试的相互作用」graduate 而来（2026-11-06）。[重试判定是否改动](04-retry-judgement.md) 的代码核查给出**现状**：`okx/transport.py:113-114` 的 `while True` 里每次尝试都 `self._limiter.acquire(path)`，即每次重试都占一个限流配额；429 走 `_backoff` 的固定指数退避（`okx/transport.py:180-183`），不与 limiter 联动。[限流器形态与共享边界](06-limiter-shape.md) 已定「保持 per-Transport、per-path 滑动窗口、同步阻塞、纯数据」的形态，形态不再变动，所以「交互要不要改」现在可以单独拍了。

要拍板：

1. 重试的那一次尝试**是否应该再占一个限流配额**？现状「占」。论证角度：官方按「请求数 / 时间窗」计数，重试确实是一次真实请求，占配额与官方一致；但调用方感知到的「一次逻辑调用」可能连发 N 次，是否需要按逻辑调用计？注意 06 已把「分页计量单位」定为按 HTTP 请求计，两处口径要不要一致。
2. 服务端 429 触发时，`_backoff` 的固定指数退避要不要与 limiter **联动**（例如把 429 当作「窗口已满」信号、提前让后续请求等待）？还是维持两者互不感知？
3. 若改，是否构成公开面变化、要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`——由 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 统一判断归属。
4. 保持现状也是一个答案，但要写明理由，别让它悬着。

解本工单时先 zoom 04 与 06 的 Answer。只决策，不改 `okx/transport.py` / `okx/rate_limit.py`。

> **来自 07 的输入（2026-11-06）**：[文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 定了 ADR / Migration 判据：本图不新建 0018、不写 `### Migration` 行；若本工单决定改「重试是否占配额 / 429 退避联动」，届时按 `/domain-modeling` 三判据重新判断归属，不重开 07。

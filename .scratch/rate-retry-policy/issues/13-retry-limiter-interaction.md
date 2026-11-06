# 13 · 重试与限流器的交互要不要改

Type: grilling
Status: resolved
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

## Answer

重试与限流器的交互已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：全部维持现状——每次重试仍占一个配额、429 走固定退避且不与 limiter 显式联动；13 无公开面变化。**

**代码事实基线**：
- `okx/transport.py:111-124`：`while True` 每轮先 `_limiter.acquire(path)` 再 `_send`；异常时 `attempt += 1` + `_backoff(attempt)`——每次尝试（含重试）都占一个配额。
- `okx/transport.py:180-183` `_backoff` = `retry_backoff * 2 ** (attempt - 1)` + `time.sleep`（固定指数退避）；429 经 `_is_transient`（`:174-178`）判为可重试 → 退避 → 下一轮重新 `acquire`。**429 与 limiter 已通过「重试前的延迟」间接配合**。
- `okx/rate_limit.py:23-39` `acquire`：锁外 `sleep`、per-path 滑动窗口、**纯数据**（无状态查询接口）。
- 测试 `test/unit/okx/test_retry.py:93/102/132/154/169` 覆盖 429 重试、退避翻倍、超限等待。
- 06 定「分页计量单位按 HTTP 请求计」「limiter 纯数据、不加可观测接口」「滑动窗口不改算法」；Out of scope 有「限流算法重写不动」。04 定「429/5xx 优先、`raise_on_error=False` 永不重试」；05 定默认 off；07 定「不建 0018、不写 Migration 行；13 若改动按三判据重判、不重开 07」。

1. **重试是否再占一个配额**：**保持「占」**。理由：① 官方按「请求数 / 时间窗」计数，重试是一次真实 HTTP 请求，占配额与官方一致；② 06 已把「分页计量单位」定为按 HTTP 请求计，两处口径一致；③ 改成「按逻辑调用计」会让一次逻辑调用连发 N 次真实请求却只记 1 次，可能超官方限额；④ 05 定默认 off，`rate_limit=True` 是用户显式选择、接受这个语义。场景：`max_retries=2` 时一次 GET 最多 3 次真实请求，本地窗口记 3 次，与官方 `N requests per window` 对齐。
2. **429 退避要不要与 limiter 显式联动**：**维持互不感知、不联动**。理由：① 现状已有隐式配合（429 → 退避 1s/2s/4s → 下一轮 `acquire` 重新检查本地窗口），不必显式耦合；② 显式联动需要 limiter 接受外部信号或暴露状态，违反 06「纯数据、不加可观测接口」，也落在 Out of scope「算法重写不动」里；③ 429 是服务端「已超额」信号、本地滑动窗口是客户端预估，语义不同，混在一起会把 limiter 变成自适应；④ 06 已定 limiter 形态不再变动。
3. **公开面与 ADR**：Q1/Q2 都不改 → **13 无公开面变化、不建 0018、不写 `### Migration` 行**（与 07 一致）；07 留给本工单的「若决定改动则按三判据重判」触发条件**未触发**，不重开 07。
4. **「保持现状」的理由与文档落点**：理由见 Q1/Q2；两条现状（「每次重试占一个配额」「429 走固定退避、不与 limiter 联动」）写进 **07 的 spec 骨架第 ⑤ 节「重试判定与默认值」**，作为施工/交接时的已知行为；**不进 README 用户文档**（07 已定 README 段结构，不加这一条）。
5. **术语磨尖（`/domain-modeling`）**：「联动」分立为 **显式信号**（把 429 传给 limiter）与 **隐式配合**（退避延迟后重新 `acquire`）；现状是后者，13 的 Q2 问的是要不要升级成前者，答案是不升级。

## 边界

- **13 自身无公开面变化**：不建 ADR、不写 `### Migration` 行、不新增 CHANGELOG 段；与 04/06/07 一致、未 invalidate 任何已 resolved 工单，也不重开 07。
- **阶段性状态**：13 resolved 后，**所有无阻塞的 HITL 决策工单都解完了**；open 的只剩 09、11（两张 AFK research）与 12（`grilling`，被 11 阻塞）。但按地图收图判据（「research 的事实已查回、spec 能直接交接」），09/11 尚未解、12 仍被阻塞，所以 **13 不代解、不收图、不触发子代理**。下次不带工单按编号会先取 09（AFK，解时触发 research 子代理）；09/11/12 全部解完才到收图。
- 本图只决策，不改 `okx/transport.py` / `okx/rate_limit.py`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理、未新建工单）。

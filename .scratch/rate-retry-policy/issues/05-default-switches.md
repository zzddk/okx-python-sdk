# 05 · 两个默认开关是否从 off 改 on

Type: grilling
Status: resolved
Blocked by: 02, 03

## Question

`rate_limit=False`（`okx/transport.py:46`）与 `max_retries=0`（同文件 :45）现在都默认关闭，README.md:101 说「passing the new arguments is the only way to turn them on」。拍板：

1. 改还是不改？两个一起改、只改一个、还是都保持 off？
2. 关键取舍：在表只有 8 条端点（[表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 定下覆盖前尤其如此）时打开 `rate_limit`，实际只对 8 个路径生效——会不会给用户「已经全局限流」的错觉？打开 `max_retries` 则在 ADR-0003 的约束下只对 GET 与带幂等键的 POST 生效。
3. 若改：属于公开面变化，按 ADR-0004 要成批发版，进哪个 minor？CHANGELOG 的 `### Migration` 表要写哪几行？

> **不适用（2026-11-06）**：本工单决定维持 off，不存在「进哪个 minor / Migration 写哪几行」；07 也不为此写 `### Migration` 行。

4. 若只改一个或不改：理由写清楚，README 的「默认关闭」说明要不要同步调整措辞。

依赖 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 与 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)，因为默认打开后的实际收益与风险取决于表覆盖到什么程度。

> **来自 03 的输入（2026-11-06）**：03 已把覆盖验收线定为「官方已公布限额且与项目路径常量对应的端点」，但表仍是 8 条——补全属图外施工，spec 不承诺补全进度。因此本工单「表只有 8 条端点」的前提不变，讨论默认值时按 8 条算；[官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的清单回来后，若施工已把表补全，需重新评估本工单的收益判断。

> **来自 04 的输入（2026-11-06）**：[重试判定是否改动](04-retry-judgement.md) 决定维持 ADR-0003 三条原状（GET 一律可重试、POST 仅带 `clOrdId` / `algoClOrdId` / `reqId` 可重试、只对瞬时故障重试），本工单「打开 `max_retries` 只对 GET 与带幂等键的 POST 生效」的前提不变；`replayable=True` 显式覆盖入口仍存在，讨论默认值时不要假设「开了就万事大吉」。

## Answer

默认开关已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：`rate_limit` 与 `max_retries` 都保持 off，一个都不翻。**

**代码事实基线**：
- `okx/transport.py:45-46`：`max_retries=0`、`rate_limit=False`；`:58` 是 `RateLimiter(RATE_LIMITS) if rate_limit else None`——默认 False 时连 limiter 都不建；`:171` 的 `_retry_allowed = replayable and attempt < max_retries` 在 0 时恒 False。
- `test/unit/okx/test_retry.py:44` 有 `test_retries_are_off_by_default` 锁住默认关闭。
- `okx/rate_limit.py:36` 的 `RateLimiter.acquire` 用阻塞 `time.sleep`；CHANGELOG.md:322 记 `paginate()` 每页都走 retry/rate-limit 路径。
- 03 定「表仍是 8 条、补全属图外施工、spec 不承诺进度」；04 定「ADR-0003 判定原状 + `raise_on_error=False` 永不重试 + `replayable` 逃生口」。05 的两个前提都不变。
- ADR-0004：「后续若出现小的破坏性需求，先攒着，不要为它单独发一个 minor」，裁量标准「能否写进同一段迁移说明」。当前 `__version__ = 0.15.0`、tag `v0.15.0` 已本地打、领先 origin 77 个提交；地图 Out of scope 已排除发版。
- 0.15.0 的 `### Migration` 是 `| Before | After |` 两列表；README.md:101 与 CHANGELOG.md:329 的「默认关闭」措辞与代码一致。

1. **三选一取「都保持 off」**（三个候选：都保持 off / 只翻 `max_retries` / 两个都翻）。理由：
   - ① 表只有 8 条（03 定补全属施工），打开 `rate_limit` 后约 266 个路径仍不限流，会给「已经全局限流」的错觉，且把阻塞 `sleep` 变成所有表内调用的默认行为；
   - ② 04 定判定原状 + `raise_on_error=False` 永不重试，打开 `max_retries` 后「什么时候会重试」对用户不透明；交易 SDK 里默认改变所有 GET 的失败语义（延迟、重复请求）风险更大；
   - ③ 改默认值是破坏性改动，按 ADR-0004 属「小的破坏性需求」应攒着；本图又不发版，「改」会让 spec 悬着。
   - **反面（如实记录）**：默认 off 意味着这两个能力几乎没人用，收益确实低；这是本次取舍付出的代价，不掩饰。
   - 场景：`rate_limit=True` 下高频调 `/api/v5/account/bills`（表外）完全不限流；`max_retries=2` 且 `raise_on_error=False` 收到 429 一次都不重试。
2. **ADR-0004 判据**：确认「改默认值 = 破坏性改动，且属于 ADR-0004 说的『小的破坏性需求』，应攒到下一批以迁移故事为主题的 minor、不单独发一个版本」；当前没有可搭的同批，地图 Out of scope 已排除发版。这是支撑上一条的判据，不是新决策。
3. **文档与 Migration 落点**：Question 第 3 点**不适用**——07 不为此写 `### Migration` 行；README.md:101 与 CHANGELOG.md:329 的「默认关闭」措辞与代码一致、**不改**；「为什么默认关 + 怎么显式打开」的补偿说明归 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md)。
4. **README 补偿说明的力度**：07 里明确要求「Retries and rate limiting」段写出三件事——① 两个开关各自的实际生效范围；② 默认关闭的理由；③ 显式打开的代码示例（README.md:105-109 已有）。05 只定方向，不写正文。
5. **语义磨尖（`/domain-modeling`）**：README 的「turn them on」把两个开关的语义抹平了。本图统一写死：`rate_limit=True` 不是「全局限流」，只是「表内 8 条路径的阻塞式滑动窗口」；`max_retries=N` 不是「所有请求重试 N 次」，只是「对 `replayable ∩ transient` 的失败最多重发 N 次，且 `raise_on_error=False` 时不重试」。
6. **重开条件与公开面**：等 [官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 回来、且施工把表补全到 03 的验收线后，可在**新的破坏性批次**重新评估；按「一个决策只住一处」不重开 05，另立 effort、本图不处理（写进地图 Out of scope，不进 fog）。05 维持 off → **无公开面变化、不新建 ADR**（按 `/domain-modeling` 三判据），ADR 归属由 07 统一判断。

## 边界

- `retry_backoff=1.0`（`okx/transport.py:45`）也是默认值，但 `max_retries=0` 时不重试就不退避，**05 不管它**；将来要调属 [限流器形态与共享边界](06-limiter-shape.md) 或施工范围。
- fog 两条（限流与重试的相互作用、分页计量单位）仍分别依赖 06，本工单未改变其形状，不 graduate。
- 07 的 `Blocked by` 已含 05，解完 05 仍被 06 阻塞。
- 本图只决策，不改 `okx/transport.py` / `okx/rate_limit.py`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理）。

# 04 · 重试判定是否改动

Type: grilling
Status: resolved
Blocked by: —

## Question

ADR-0003 锁了三条：GET 一律可重试；POST 仅在带 `clOrdId` / `algoClOrdId` / `reqId` 时可重试；只对瞬时故障（`httpx.TransportError`、HTTP 429/5xx、业务码 50001/50004/50011/50013）重试，每次重试重新生成时间戳与签名。逐项拍板是否改动：

1. 幂等键集合 `_IDEMPOTENCY_KEYS`（`okx/transport.py:29`）要不要扩充？依据是什么——OKX 官方文档还公布哪些幂等键？
2. `_RETRYABLE_CODES`（`okx/transport.py:25`）要不要增删？判据是什么（例如 429 与业务码重叠时的优先级）？
3. 「GET 全可重试」是否保持？有没有 GET 端点其实带副作用？
4. 要不要引入「按端点白名单」的补充判定？ADR-0003 明确否过这条路，若翻案要说明为什么现在条件变了。
5. 每一处改动是否构成公开面变化、要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`。

保持原状也是一个答案，但要写明「不改」的理由，别让它悬着。

> **前提修正（2026-11-06）**：代码核查发现 04 的 Question 漏了 `replayable` 显式覆盖入口（`okx/transport.py:78`、`okx/okxclient.py:31,38`），且第 2 点问的「429 与业务码重叠时的优先级」在 `okx/transport.py:174-178` 已有答案（status 429/5xx 先判、优先于业务码）。术语上把「能不能发第二次」= `replayable` 与「这次失败值不值得重发」= `transient` 分立，不再笼统叫「重试判定」。

## Answer

重试判定已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：ADR-0003 的三条全部维持原状，不改动。**

**代码事实基线**：
- `okx/transport.py:164-168` `_is_replayable`：GET 恒 True；POST 要求 `any(params.get(key) for key in _IDEMPOTENCY_KEYS)` 真值判断（空串 / 0 不算），已有 `test_empty_idempotency_key_does_not_count`。
- `okx/transport.py:174-178` `_is_transient`：先判 `status == 429 or status >= 500` 才看业务码；`httpx.TransportError` 在 `request` 的 except 里单独走 `_retry_allowed`，不经过 `_is_transient`。
- `okx/transport.py:113-114,180-183`：循环内每次尝试都 `_limiter.acquire(path)`；`_backoff` 为 `retry_backoff * 2 ** (attempt - 1)` 固定指数退避。
- `replayable` 显式覆盖：`okx/transport.py:78`、`okx/okxclient.py:31,38`（「overrides the derived retry safety for one call」），测试 `test/unit/okx/test_retry.py:132`、`test/unit/okx/test_okxclient.py:73`。
- `raise_on_error=False` 时永不重试（`test_raise_on_error_false_never_retries`），README.md:111 与 CHANGELOG.md:330 未说明。

1. **三条判定维持原状**：不扩充 `_IDEMPOTENCY_KEYS`（`clOrdId` / `algoClOrdId` / `reqId`），不增删 `_RETRYABLE_CODES`（50001 / 50004 / 50011 / 50013），保持 GET 一律 replayable。理由：① ADR-0003 的取舍仍成立——幂等键是调用方本来就要传的，比按端点分类便宜且不随端点增长腐化；② `replayable=True` 逃生口已能覆盖「官方公布了新幂等键、但集合没加」的例外，调用方可显式声明可重放；③ [表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 刚查清官方约 135 个端点 / 项目 274 个路径，改集合是公开面变化，没有确凿官方依据不动。场景：不带 `clOrdId` 的下单超时仍只发一次；带 `clOrdId` 的照常重发并重新签名。
2. **`replayable` 逃生口**：保留作为判据之外的显式覆盖，写进 README（归 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md)）；不因为有它就反过来扩充幂等键集合；ADR-0003 要不要补一句说明由 07 统一判断（沿用 02/03 的归属）。
3. **不翻「按端点白名单」**：ADR-0003 否过它，理由是「随新端点增长必然腐化」；03 的 274/135 事实反而加强了这个判断。条件没有变化，不翻案。
4. **代码已定的三条边界，本工单不改**：429/5xx 优先于业务码；`httpx.TransportError` 不走 `_is_transient`；`raise_on_error=False` 永不重试。04 只管判定逻辑，后两条是既有行为；`raise_on_error=False` 的说明归 07。场景：`raise_on_error=False` 下收到 429 且 body 是 JSON，直接返回 payload、一次都不重试，与 README 给人的印象不同。
5. **术语分立**：`replayable`（能不能发第二次）与 `transient`（这次失败值不值得重发）是两个判定，不再笼统叫「重试判定」；写进 map Notes 的术语行。
6. **外部事实缺口**：官方还有哪些幂等键、50001/50004/50011/50013 各自含义与是否还有别的瞬时码、有没有 GET 端点带副作用——01 的 findings 未覆盖，README.md:111 / CHANGELOG.md:330 也未给出处。按 Notes 的「事实与决策分工」，新开 [OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](11-idempotency-and-error-codes.md)（AFK research，无阻塞），本会话不解、不触发子代理。若它查出确凿遗漏，由 [11 的事实要不要改重试判定](12-retry-facts-followup.md) 承接，不重开 04。

## 边界

- 04 全维持原状 → **没有产生公开面变化**：不新建 ADR、不写 CHANGELOG 的 `### Migration` 行（按 `/domain-modeling` 三判据，这里没有「难回退 + 真取舍」的新决定）。若 11 查出确凿遗漏，才由 07 判断 ADR 归属。
- **限流与重试的相互作用**：现状是「每次重试都占一个限流配额」（`okx/transport.py:113-114`）、429 走固定指数退避；「占不占配额 / 退避要不要与限流器联动」从未被决策过，仍属地图 Not yet specified，待 [限流器形态与共享边界](06-limiter-shape.md) 定了形态后才拍要不要改。本工单维持判定原状，未改变其形状。
- `raise_on_error=False` 与 `replayable` 的文档说明归 07；本图只决策，不改 `okx/transport.py` / `okx/okxclient.py`。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理）。

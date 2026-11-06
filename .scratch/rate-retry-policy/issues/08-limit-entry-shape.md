# 08 · 限额表条目要不要容纳计数维度与任意窗口

Type: grilling
Status: resolved
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

> **来自 06 的输入（2026-11-06）**：[限流器形态与共享边界](06-limiter-shape.md) 已定「保持 per-Transport、per-path 滑动窗口、同步阻塞、纯数据」；06 只管**当前二元组 + per-path 计数**下的形态。本工单可自由定表的 value 形状，但若决定**让计数维度参与计数**或改用 **UTC 0:00 固定窗口**，那属于 limiter 形态变更，需新开工单重审、不由 08 顺带替 06 拍。另：把 `per day` 写成 86400 秒滑动窗口并不等价于「UTC 0:00 重置」（06 的 Known limitation）。解本工单时先 zoom 06 的 Answer。

## Answer

限额表条目形状已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：全部维持现状——保持二元组 `(requests, window_seconds)` + `path` 单键，不升级 value、不改 key、不引入固定窗口、不体现 REST/WS 共享；官方维度 / 窗口语义 / 多方法 / 共享等事实交给 09 的清单与 spec 的判定规则文档承载。**

**代码事实基线**：
- `okx/rate_limit.py:28` `count, window = limit` **硬解包二元组**；`okx/transport.py:17,58` 把 `RATE_LIMITS` 直接喂给 `RateLimiter`；`test/unit/okx/test_retry.py:165,171` 也用二元组构造。value 升级成三元组会让 limiter 立即抛 `ValueError`。
- `okx/consts/rate_limits.py` 的 `RATE_LIMITS` 是 `okx.consts` 下可导入常量（公开面），8 条全是 `(n, 2)`。
- `okx/consts/endpoints/trade.py:3,10`：`PLACE_ORDER` 与 `ORDER_INFO` 两个名字共用 `/api/v5/trade/order` 同一 path。
- 01 findings 第 123/125/144 行：trade 三条按 `User ID + Instrument ID`（按 instrument）计、market 按 `IP`、account 按 `User ID`；REST 与 WS 共享限额、place/amend/cancel 独立、批量与单笔独立；同路径多方法区分不在现有二元组里。第 48-59 行：官方一条限额是 `(请求数, 时间窗, 计数维度)`，窗口有 per second / 2s / 5s / 10s / day / month，部分 UTC 0:00 重置。
- [限流器形态与共享边界](06-limiter-shape.md) 已 resolved 并划死边界：若 08 让计数维度参与计数或改用 UTC 0:00 固定窗口 → 属 limiter 形态变更，需新开工单重审、不由 08 代拍；06 的 Known limitation「86400 秒滑动 ≠ UTC 0:00 重置」指向本工单。
- 03 定「spec 只给判定规则 + 取数方法、不列最终表」；07 定「不建 0018、不写 Migration 行」，spec 七节骨架第 ② 节为覆盖验收线与判定规则；Out of scope 已排除 WS 限速与算法重写。
- 09（AFK research）仍 `open`，其清单会逐条给出「路径 + 数值 + 窗口 + 计数维度 + 来源页」。

1. **value 形状**：保持 **二元组 `(requests, window_seconds)`，不升级**；计数维度 / 窗口语义 / 多方法 / REST-WS 共享这些官方事实交给 09 的清单 + spec 的判定规则文档承载。理由：① 代码硬解包，升级会让 limiter 立即崩，而 06 已定 limiter 形态不变、且明确这要新开工单重审——08 若升级会同时违反 06 边界并制造一张必须立刻解的新工单；② 03 定 spec 不列最终表，条目形状属施工细节，当前 8 条都是 `per 2 seconds`，二元组够用；③ 07 定本图不建 0018 / 不写 Migration，升级 `RATE_LIMITS` 是公开面变化、按 ADR-0004 应攒着。
   - **代价（如实记录）**：现有 8 条里 trade 三条的 60/2 官方按 instrument 计、limiter 按 path 全局计，语义偏差；08 不修（属 06 边界 / 新 effort）。
2. **key 形状**：保持 **`path` 单键**，不改成 `(method, path)`。理由：改 key 会牵动 `Transport.request` 的 `acquire(path)` 调用点、`RateLimiter._calls` 的 key 与全部相关测试，属 06 划出的 limiter 形态变更；且 09 清单回来前并不知道同路径两方法的限额是否真的不同（findings 只说官方「区分」）。**触发条件**：09 若查出同路径多方法限额不同，另开新工单处理，不重开 08。
3. **非 2 秒窗口**：补全表时**按秒数记**（`per day`→86400、`per month`→2592000、`per second`→1），**不引入 UTC 0:00 固定窗口语义**；spec 里注明「86400 秒滑动 ≠ UTC 0:00 重置」（沿用 06 的 Known limitation）。理由：固定窗口是 limiter 算法变更，落在 06 边界与 Out of scope「算法重写不动」里。场景：补全 `/api/v5/account/bills-history-archive` = 12/day 时写 `(12, 86400)`，跨 UTC 0:00 后滑动窗口仍允许请求，与官方重置语义不同——如实记录、不在本图修。这条记法规则写进 07 的 spec 骨架第 ② 节。
4. **REST / WS 共享**：**不在本表体现**，明确留给 WS effort（Out of scope 已排除 WS 限速）；findings 第 125 行「REST 与 WS 共享限额、下单/改单/撤单相互独立、批量与单笔独立」写进 spec 的「已知差异」清单，由 09 清单承载。
5. **公开面与 ADR**：不升级 → **08 无公开面变化、不建 0018、不写 `### Migration` 行**（与 07 一致）。判据写明：**升级 `RATE_LIMITS`（`okx.consts` 可导入常量）才是公开面变化**，按 ADR-0004 攒到下一批、本图不发版。
6. **术语磨尖（`/domain-modeling`）**：「升级」分立为 **value 升级**（二元组 → 含维度/窗口语义）与 **key 升级**（`path` → `(method, path)`），Q1/Q2 各管一件。

## 边界

- **三条 Known limitation**（不升级所付的代价，如实记录）：① trade 三条 60/2 官方按 `User ID + Instrument ID`（按 instrument）计，limiter 按 path 全局计；② `/api/v5/trade/order` 同路径 POST + GET 现状共用一个配额，官方区分两方法；③ 86400 秒滑动窗口 ≠ UTC 0:00 重置（引用 06）。三者均不在本图修。
- **事实载体**：[官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的清单是这些官方事实的**唯一载体**；08 已定表不承载维度 / 窗口语义 / 多方法 / REST-WS 共享，解 09 时把这些字段列全。
- **触发条件**：09 若查出同路径多方法限额不同 → 新开工单、不重开 08；将来若要升级表条目（value 三元组 / key `(method,path)` / UTC 固定窗口 / 按计数维度计数）→ 属新 effort，并需新开工单重审 limiter 形态（06 边界）。**08 未触发 06 的边界条件，本次不新开任何工单**。
- **不收图**：08 resolved 后还有 09/10/11/12/13 五张 open（12 被 11 阻塞），frontier 剩 09/10/11/13；08 不代解、不收图、不触发子代理（09/11 是 AFK，仍留在 frontier）。
- 本图只决策，不改 `okx/consts/rate_limits.py` / `okx/rate_limit.py`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理、未新建工单）。

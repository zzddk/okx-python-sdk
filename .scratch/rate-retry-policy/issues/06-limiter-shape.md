# 06 · 限流器形态与共享边界

Type: grilling
Status: resolved
Blocked by: 02

## Question

`okx/rate_limit.py` 的 `RateLimiter` 是 per-path 独立滑动窗口、`time.sleep` 阻塞调用线程、`Transport` 自带一个实例（多个 API 类共享同一 `Transport` 就共享同一 limiter）。在 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 的窗口口径下拍板：

1. 「同一路径跨多个 `Transport` 实例」要不要共享限流状态？现状是各算各的——若用户建两个 Transport 打同一账户，会不会超额？
2. `sleep` 阻塞是否可接受？要不要注入异步等待 / 让调用方自己选？注意 `Transport` 用的是同步 httpx 客户端。
3. 窗口边界要与 OKX 的窗口对齐（固定窗口）还是保持滑动窗口？两者在突发流量下的行为差别要不要写进决策。
4. limiter 是否需要可观测（当前用量、被拒次数）？还是保持纯数据、不引入状态查询接口。

只决策形态，不改 `okx/rate_limit.py`。

> **前提修正（2026-11-06）**：02 定的是「数值来源」（取官方端点详情页固定值），并未定「窗口口径」；01 的 findings 恰恰说明窗口长度由各端点详情各自给出、不统一（1s/2s/5s/10s/day/month，还有 UTC 0:00 重置）。06 要在这个事实下拍，不是在某个统一窗口下拍。

## Answer

限流器形态已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：四问全部维持现状，一个都不改。**

**代码事实基线**：
- `okx/rate_limit.py:12-39`：per-path 的 monotonic 时间戳列表 + `threading.Lock`，**在锁外 `sleep`**（不同 path 互不阻塞），`_sleep` 可注入；`test/unit/okx/test_retry.py:162-179` 靠注入单测，`test_client_shares_the_limiter` 验证「共享同一 Transport = 共享同一 limiter 实例」。
- `okx/transport.py:58` 每个 `Transport` 实例建一个 `RateLimiter`；`:113-114` 每次尝试（含重试）都 `acquire`。
- `okx/pagination.py:104-110` `_walk` 每页 `fetch(...)` = 一次 `Transport.request` = 一次 `acquire`。
- 01 findings 第 44-66 行：窗口不统一（1s/2s/5s/10s/day/month）、有 `resets at UTC 0:00` 的固定窗口；项目表 8 条恰好都是 2s，不是官方统一窗口；计数维度多种（User ID 90 / IP 27 / IP+Instrument ID 4 / User ID+Instrument ID 3 …），而 limiter 只按 `path` 计数。
- 05 定默认 off、03 定表仅 8 条；地图 Out of scope 已有「限流算法重写（滑动窗口 → 令牌桶 / 并发控制）除非图内决策明确要求否则不动」。

1. **跨 Transport 共享**：保持 **per-Transport、不共享计数**。三个候选（保持 per-Transport / 进程级共享 / `Transport` 接受可选外部 limiter 显式共享）取第一个。理由：① 官方按「计数维度」（User ID / IP）计，与「Transport 实例」本就不对应，真正正确的共享得按 User ID 重做，那是 [限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 的条目形状问题；② 进程级全局状态会破坏 `RateLimiter` 的可单测性，且多账户不能共用；③ 显式注入是公开面变化，按 ADR-0004 应攒着。
   - **Known limitation（如实记录）**：用户建两个 `Transport` 打同一账户，两边各自按 60/2s 计、合起来可能超官方限额。跨实例共享计数属新 effort，写进地图 Out of scope。
2. **`sleep` 阻塞**：保持**同步阻塞 + `_sleep` 注入点，不引入异步等待**。理由：`Transport` 用的是同步 `httpx.Client`，异步等待无处安放；锁外 `sleep`（`okx/rate_limit.py:38-39`）已保证「一个 path 等待不阻塞其它 path」；`_sleep` 已让调用方/测试可注入；05 定默认 off，`rate_limit=True` 是用户显式选择、接受阻塞。场景：多线程共享一个 Transport、某 path 触发等待时，其它 path 的调用仍能继续。
3. **窗口边界**：保持**滑动窗口、不改算法**。理由：① 现有 8 条官方都是 `per 2 seconds`，滑动窗口与之相符；② 非 2 秒窗口与 UTC 0:00 重置怎么表达，要等 [官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的清单与 08 的条目形状定了才有输入，现在拍「改算法」是空转；③ 也落在 Out of scope 的「算法重写不动」里。
   - **行为差别（写进理由）**：滑动窗口不会在窗口边界放行 2×count，固定窗口会；这是保持滑动窗口的正面理由。
   - **Known limitation**：把 `per day` 写成 86400 秒滑动窗口 **不等价于**「UTC 0:00 重置」，指向 08。
4. **可观测**：保持**纯数据、不引入状态查询接口**（当前用量 / 被拒次数）。理由：`RateLimiter` 现在只有 `_limits`/`_calls`/`_lock`/`_sleep`，加接口会扩大 `okx.rate_limit` 的公开面、牵动 `test_retry.py` 的注入式单测；05 定默认 off，观测需求不紧迫；真要排查用 `logging` 即可（`okx/transport.py:20` 已有 `logger`）。
5. **术语磨尖（`/domain-modeling`）**：「共享限流状态」分立为「共享 limiter **实例**」（现状：同一 Transport 内，`test_client_shares_the_limiter`）与「共享**计数**」（不同 Transport 之间按 User ID 合并）；06 的 Q1 问的是后者。

## 边界（由 06 的形态推定的结论）

- **限流与重试的相互作用**：现状「每次重试都占一个配额、429 走固定指数退避不与 limiter 联动」已由 04 的代码核查明确；「占不占配额 / 退避要不要联动」仍是未决策项，已 graduate 成 [重试与限流器的交互要不要改](13-retry-limiter-interaction.md)（blocked by 06），06 不代拍。
- **分页 / 批量调用的计量单位**：每页 = 一次 `Transport.request` = 一次 `acquire`，即**按 HTTP 请求计**；官方是 `N requests per window`，按请求计才正确，改成「整个 walk 算一次」反而绕过限额。这条 fog 的答案已清楚，**保持按 HTTP 请求计、不改**，不另开工单；原 fog 条目从地图 Not yet specified 移除。
- **06 与 08 的形态边界**：06 定的是「**当前二元组 + per-path 计数**」下的形态；08 可自由定表条目形状。若 08 决定让**计数维度参与计数**或改用 **UTC 0:00 固定窗口**，那属于 limiter 形态变更，需**新开工单重审**，不重开 06、也不由 08 顺带替 06 拍。
- `retry_backoff=1.0`（`okx/transport.py:45`）是重试退避、不是限流器形态，05 曾说「将来要调属 06 或施工范围」——06 明确**划出**，归施工/新 effort。
- 06 四问全维持 → **无公开面变化、不新建 ADR**（`/domain-modeling` 三判据）；CHANGELOG.md:336 仍写「Passing `client=` copies … including the shared limiter」，但 `okx/okxclient.py:16-19` 现在只接受 `Transport`、没有 `client=`，属**过期文档**，订正归 07。
- 07 的 `Blocked by` 是 03/04/05/06，06 resolved 后 **07 解锁**。
- 本图只决策，不改 `okx/rate_limit.py` / `okx/transport.py` / `okx/pagination.py`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理）。

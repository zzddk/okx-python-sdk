# 限流与重试策略 spec

> 状态：决策已完成（wayfinder 地图 `.scratch/rate-retry-policy/map.md`，2026-11-06 已收图，14 张决策工单全部 resolved）。
> 性质：handoff 交付物，把决策整理成施工方能直接执行的规格；本图本身不改代码、不发版。
> 范围：REST 传输层限流（`okx/consts/rate_limits.py`、`okx/rate_limit.py`）与重试（`okx/transport.py`）。WS 层限速不在内。

## 1. 数值口径与快照

**决策**：表内数值一律取 OKX 官方各端点详情页公布的固定值，不按账户 / VIP 等级调整。

- 来源口径：`www.okx.com/docs-v5/en` 完整版（不是 `app.okx.com` 的子集页）。01 的 `137/141/135` 是子集口径；完整版是 **395 个 REST 声明 / 386 个 distinct 路径 / 16 个业务段**。施工取数以完整版为准。
- 快照：本次口径快照日期 **2026-11-06**；`rate_limits.py` 模块注释里的日期语义改为「最近一次核对日期」，每次同步时更新。
- 官方对普通端点不分 VIP 层级；`rate_limits.py` 里「higher VIP levels / treat these numbers as a floor」的说法无官方依据，删掉；「published limits are stable」也不成立（Change Log 有 2026-05-08、2026-06-11 两次变更），改成「数值来自各端点详情页，随官方 Change Log 变动」。
- 明确排除：colocation / 做市商议价额度 / 订单类 VIP5+ 子账户 fill-ratio 例外；本表不表达，也不替用户推断适用等级。

**验收**：`rate_limits.py` 模块注释能说明「数值来源、快照日期语义、未收录端点的定义」，且不再出现 floor / stable / VIP 分级的错误说法。

## 2. 覆盖验收线与判定规则

**决策**：覆盖验收线 = **官方已公布限额、且与项目路径常量对应的端点**；不以项目 274 个路径常量为分母。

**判定规则（施工时照此取数）**：

1. 只在 S1 完整版端点详情里出现 `Rate Limit:` 行的端点才进表；项目路径常量里没有对应端点的（S1 口径 **33 个**）不进表，按「未收录端点」维持不限流——这是「项目没有这个路径」，不是豁免。
2. **同路径多方法**：按**项目实际暴露的 HTTP 方法**取值，不取严、不取松。当前 5 个 POST / GET 值不同的路径里，4 个不在项目里（`account/mmp-config`、`asset/monthly-statement`、`rfq/mmp-config`、`users/subaccount/apikey`），唯一两侧都有的 `bills-history-archive` 项目只暴露 POST，取 `12 requests per day`。若将来出现「项目同时暴露两方法、官方值不同」，该路径不进表并列入已知差异（`(method, path)` 升级属新 effort）。
3. **非 2 秒窗口**：按秒数记（`per second`→1、`per day`→86400、`per month`→2592000），并注明「滑动窗口语义不等价于 UTC 0:00 重置」。
4. 表覆盖的规模（S1 口径）：两侧都有 **241** / 仅官方 145 / 仅项目 33。
5. 补全表属**施工**，本 spec 不承诺补全进度；本文件只给规则与取数方法，不列最终表。

**已知差异（写进 spec / 注释，不在表里表达）**：

- 计数维度（`Rate limit rule`）多样（User ID / IP / +Instrument ID / +Instrument Family …），表不承载。
- REST 与 WS 共享下单限额；place / amend / cancel 相互独立；批量与单笔独立。
- `trade/order-algo` 两方法数值相同（20/2s）但计数维度不同。
- `GET /api/v5/asset/deposit-address` 可能创建地址，属从错误码 58310 反推的推断，官方未明示。
- `POST /api/v5/account/bills-history-archive`：主文档 12/day，Change Log 2026-06-11 称改为 1/10s，两者冲突；按主文档原文取 12/day，维护时重新取证。
- 12 个端点用 `Rate limit:` / 全角 `Rate limit：` 变体写法；`/api/v5/system/status` 无 `Rate limit rule` 行。
- 09 的完整清单在 `research/official-limit-endpoint-list` 分支（commit `805528e`，永不合并、不 push）；施工需要时用 `git show` 取读，**不要把该分支合并进 master**。

## 3. 表条目形状

**决策**：`RATE_LIMITS` 保持 **二元组 `(requests, window_seconds)` + `path` 单键**，不升级。

- 不升级 value（不塞计数维度 / 窗口语义）；不把 key 改成 `(method, path)`（`okx/rate_limit.py:28` 是 `count, window = limit` 硬解包，且 key 升级会牵动 limiter 形态）。
- 不引入 UTC 0:00 固定窗口；不体现 REST-WS 共享。
- 计数维度、窗口语义、多方法、共享等事实由本 spec 与清单承载，不进表。

**Known limitation**：

- trade 三条（`/api/v5/trade/order`、`cancel-order`、`amend-order`）官方按 `User ID + Instrument ID` 计（按 instrument 分桶），而 limiter 按 path 全局计——语义偏差，本 spec 不修。
- 跨 `Transport` 实例不共享计数（见第 4 节）。
- 86400 秒滑动窗口 ≠ UTC 0:00 重置。

## 4. 限流器形态

**决策**：四问全部维持现状。

- **共享**：per-Transport（同一 `Transport` 内共享一个 limiter 实例；不同 `Transport` 不共享计数）。跨实例共享计数属新 effort。
- **阻塞**：同步阻塞 + `_sleep` 注入点，不引入异步等待（`Transport` 用同步 httpx）。
- **窗口**：滑动窗口，不改算法（令牌桶 / 并发控制属 Out of scope）。
- **可观测**：纯数据，不加状态查询接口；排查用 `logging`。
- **计量单位**：每页 / 每次尝试都算一次 HTTP 请求（`paginate` 每页 = 一次 `acquire`；重试每一次都 `acquire`），与官方「N requests per window」一致。

## 5. 重试判定与默认值

**决策**：只自动重放「官方建议稍后重试」的错误；结果未知的错误不自动重放。

**三分类**：

| 类别 | 码 | 官方措辞 | 处理 |
|---|---|---|---|
| 处理前失败 | 50001 / 50011 / 50013 | 「try again later」/「throttle」/「try again later」 | 可重试（受 `replayable` 约束） |
| 结果未知 | 50004 / 51149 | 「does not mean success or failure, please check the request result」 | **不自动重试** |
| 确定性拒绝 | 参数错误等 | 参数 / 余额类 | 不重试 |

**代码改动（施工）**：

- `_RETRYABLE_CODES` 移除 `50004`，保留 `50001` / `50011` / `50013`。
- 新增 `_OUTCOME_UNKNOWN_CODES = {"50004", "51149"}`，在 `_is_transient` 里**先于** `status >= 500` 判断，命中一律不重试（51149 是 HTTP 500，现状会被 5xx 规则重试）。
- 改写 `okx/transport.py:22-24` 的注释：说明 50001 / 50011 / 50013 是官方建议稍后重试的处理前失败；50004 / 51149 是结果未知，调用方应先查请求结果。
- 不新增 50026 / 51054 / 52910 / 52911 / 52912 到 code 白名单（HTTP 5xx 已被 `status >= 500` 覆盖）。

**幂等键**：`_IDEMPOTENCY_KEYS` 不扩充（仍 `clOrdId` / `algoClOrdId` / `reqId`）。官方没有幂等键清单；`attachAlgoClOrdId` / `clientId` / `clRfqId` / `clQuoteId` 不声明去重。术语：「幂等键」= 服务端在 **pending** 期间据此拒绝重复，**不是 exactly-once**；`clOrdId` 终态可复用。

**GET**：保持「GET 一律 replayable」。255 个 GET 无一条被官方描述为改状态；`replayable=False` 可反向覆盖。

**`replayable` 逃生口**：`Transport.request` / `OkxClient.request` 的 `replayable=` 保留，写进 README。

**默认值**：`rate_limit=False`、`max_retries=0` 都保持 off。语义写死：`rate_limit=True` 只作用于表内 8 条路径；`max_retries=N` 只对 `replayable ∩ transient` 生效，且 `raise_on_error=False` 时不重试。默认值重开条件：表补全到验收线后的新破坏性批次，另立 effort。

**与 limiter 的交互**：重试的每次尝试都占一个限流配额；429 走固定指数退避，不与 limiter 显式联动（隐式配合已够）。

**已知边界（不改）**：429/5xx 优先于业务码；`httpx.TransportError` 不走 `_is_transient`；`raise_on_error=False` 永不重试。

## 6. 文档与迁移清单

- README `### Retries and rate limiting`（`:99-113`）：改 `:113` 免责声明措辞（「这是 SDK 表的覆盖范围，不是官方没有限额」）；补三组说明——两个开关的实际生效范围、默认关闭的理由、`replayable=True` 与 `raise_on_error=False` 两处；保留 `:105-109` 示例；不动 `:101`。另补：超时类错误不自动重试、先查结果。
- CHANGELOG：本图不新增版本段、不写 `### Migration` 行；只订正 `:336` 的过期 Notes（`client=` 说法与 `okx/okxclient.py:16-19` 矛盾）。本次重试行为变化进下一个版本的 `### Changed`（施工时写）。
- ADR：`docs/adr/0018-outcome-unknown-not-retried.md`（本 spec 同批产出）；ADR-0003 原文不改。
- 数值变更（未来）：进下一个版本 `### Changed`，不写 Migration；快照日期更新为「最近一次核对日期」。

## 7. 施工项清单与第一步

**第一步（无行为风险、可独立验收）**：

1. 改写 `okx/consts/rate_limits.py:5-7` 模块注释（数值来源、快照语义、未收录端点定义、删 floor / stable / VIP 错误说法）。
2. 改 README `:113` 免责声明措辞。

**随后**：

3. 重试三分类落地：移除 50004、加 `_OUTCOME_UNKNOWN_CODES`、改注释、改 README 重试段。
4. README 补三组说明（05 / 04）。
5. CHANGELOG `:336` 订正；下一个版本 `### Changed` 记录重试行为变化。
6. 表覆盖断言：口径是「验收线集合」。09 的清单在 throwaway 分支、不合并，所以施工时要把验收线集合**固化进测试**（字面量或 fixture），不能引用该分支；补全表本身属施工（规则见第 2 节）。

**不在本 spec 范围**：WS 层限速与重连退避；限流算法重写（令牌桶 / 并发控制）；按 VIP / 账户层级运行时拉限额；全量补全 274 个端点本身；发版与 push；跨 `Transport` 共享计数；表条目升级（value 三元组 / key `(method, path)` / UTC 固定窗口 / 按维度计数）。

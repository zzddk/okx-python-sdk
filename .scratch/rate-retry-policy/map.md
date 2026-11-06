# 地图：限流与重试策略（rate-retry-policy）

> **已收图（2026-11-06）**：14 张决策工单全部 resolved；fog 已清空；`spec.md` 与 `ADR-0018` 属 handoff 交付物（07 约定本图不落文件）。

Labels: wayfinder:map

## Destination

一份可交接的《限流与重试策略 spec》+ 一组已锁定的决策：端点限额表怎么覆盖、重试判定是否改动、两个默认开关是否翻、限流器形态、文档与迁移说明怎么落。本图**规划不做**——不改代码、不发版、不把积压提交推到 origin；「把约 274 个端点补全进 `RATE_LIMITS`」是图外施工。收图时路要清到施工方照着 spec 就能动手。

## Notes

- 领域：REST 传输层限流（`okx/consts/rate_limits.py`、`okx/rate_limit.py`）与重试（`okx/transport.py`、ADR-0003）。当前表只有 8 条路径、表外端点不限流；`rate_limit=False`、`max_retries=0` 均默认关闭。
- **取证口径修正（09 查回）**：01 的 `137 / 141 / 135` 是 `app.okx.com/docs-v5/en` **子集口径**（10 业务段）；完整版 `www.okx.com/docs-v5/en` 为 **395 声明 / 386 distinct REST 路径 / 16 业务段**。S3 的 135 路径全部落在 S1 内且共同路径数值零差异，故 01/03 的定性结论仍成立；**spec 施工取数以 S1 完整版为准**，两侧都有 241 / 仅官方 145 / 仅项目 33。
- **重试事实修正（11 查回）**：50004 是接口超时、官方明说「不代表请求成功或失败」；`okx/transport.py:22-24` 的「rejected before it could be matched」不是官方说法，对 50004 相反。`clOrdId` 只在 pending 内唯一、终态可复用，不保证去重；官方没有可重试分类与 429 优先级说明。**12 必须重评 50004 是否仍可重试**。
- **重试三分类（12 定稿）**：处理前失败（50001 / 50011 / 50013，官方说 try again / throttle）→ 可重试；**结果未知（50004 / 51149，官方说 check result）→ 不自动重试**；确定性拒绝（参数错误）→ 不重试。实现上 `_OUTCOME_UNKNOWN_CODES` 先于 `status >= 500` 判断。
- 术语（Q2 已定，02、04、05、06 的 Answer 增补）：「覆盖」只指**端点路径是否进 `RATE_LIMITS` 表**；「重试判定」再分立为 `replayable`（能不能发第二次）与 `transient`（这次失败值不值得重发）；「账户层级口径」不再指 VIP 分级、改指「数值来源口径」；「表外端点」定名为「未收录端点」（项目未收录，非官方未公布）。`rate_limit=True` 只指「表内 8 条路径的阻塞式滑动窗口」、`max_retries=N` 只指「对 `replayable ∩ transient` 的失败最多重发 N 次」，均非「全局限流 / 所有请求重试」。「共享限流状态」分立为「共享 limiter 实例」（同一 Transport 内）与「共享计数」（跨 Transport 按 User ID 合并）。08 另分立「value 升级」与「key 升级」，10 另分立「取证来源清单」与「端点事实清单」、「数值同步」与「表范围扩充」，13 另分立「显式信号」与「隐式配合」。07 另澄清：Destination 的「spec」是 handoff 交付物、不在本图产出。本轮不新建 `GLOSSARY.md`（`docs/agents/domain.md` 要求缺失时静默略过）。
- 事实与决策分工（Q3 已定）：口径（目标账户层级、文档快照日期、表外端点默认处置）由人在 HITL 工单拍板；外部文档事实由 `research`（AFK）工单查回；「查文档」本身不算决策工单。work-through 阶段新建的 research 工单创建后留在 frontier、不主动 fire 子代理；**由人指定解某张 research 工单时，才 fire fresh-context 子代理调用 `/research`**（09 即如此，findings 落 throwaway 分支、本地保留不 push）。
- 顺序细化：[OKX 官方限流文档的事实结构](issues/01-okx-rate-limit-docs.md) 先铺事实、[采用哪个账户层级口径与文档快照](issues/02-limit-scope.md) 基于事实拍板，故后者 blocked by 前者。这样 charting 阶段能立刻 fire AFK research，口径也不至于凭空定；Q3 的分工不变。
- 工单格式：本地 tracker，见 `docs/agents/issue-tracker.md` 的「Wayfinding operations」。`Type:` 行表达 `wayfinder:<type>` 标签；`Status: open` = 未认领，认领改 `claimed`，解完改 `resolved`；`Blocked by:` 写编号，无阻塞写 `—`。
- 默认工单类型 `grilling`（HITL，配 `/grilling` + `/domain-modeling`）；`research` 为 AFK，可并行。每会话只解一张（research 例外）。
- 凡动公共契约的决策补 `docs/adr/`（当前最大 0017，下一张 0018）。
- 语言：中文。图内不改代码、不发版、不 push。

## Decisions so far

- [OKX 官方限流文档的事实结构](issues/01-okx-rate-limit-docs.md)：官方无集中限额表，数值分散在各端点详情；窗口不统一、普通端点不按 VIP 分层、表外端点无通用政策表述；现有 8 条数值全部对得上，但官方还带计数维度与 REST/WS 共享等信息。全文在 `research/okx-rate-limit-docs` 分支（永不合并）。09 补注：其 135 为子集口径，完整版见 Notes。
- [采用哪个账户层级口径与文档快照](issues/02-limit-scope.md)：数值取官方端点详情页固定值、不按 VIP 分级，删 `rate_limits.py` 的 floor / stable 注释；「表外」定名「未收录端点」并维持不限流、不兜底；快照 2026-11-06；口径落注释 + README、不新建 ADR；覆盖目标移到 03。
- [表外端点怎么处置、表要不要全量补全](issues/03-table-coverage.md)：覆盖验收线定为「官方已公布限额且与项目路径常量对应的端点」，不以 274 为分母；spec 只给判定规则与取数方法、不列最终表；未收录端点维持不限流 / 不兜底（归 02）；断言按验收线集合、实现依赖 09；条目形状归 08。09 补注：按 S1 完整版，两侧都有 241。
- [重试判定是否改动](issues/04-retry-judgement.md)：ADR-0003 三条全维持（幂等键集合、可重试码、GET 一律 replayable 都不动）；`replayable=True` 逃生口保留并写进文档、不翻按端点白名单；429/5xx 优先、TransportError 不走 `_is_transient`、`raise_on_error=False` 永不重试按现状记录；无公开面变化、不建 ADR 不写 Migration；外部事实缺口开 11，后续由 12 承接。 11 复核：50004 是超时 / 结果未知，注释「rejected before it could be matched」无官方依据且对 50004 相反 → 12 已改：50004 移除、51149 拒重试、注释改写。
- [两个默认开关是否从 off 改 on](issues/05-default-switches.md)：`rate_limit` 与 `max_retries` 都保持 off（三选一取「都不翻」）；理由为表仅 8 条、判定原状下重试不透明、ADR-0004 要求小破坏性需求攒着；无公开面变化、不建 ADR、不写 Migration 行、不改现有措辞；README 补偿说明归 07；重开条件写 Out of scope。
- [限流器形态与共享边界](issues/06-limiter-shape.md)：四问全维持现状——per-Transport 不共享计数、同步阻塞 + `_sleep` 注入、滑动窗口不改算法、纯数据不加可观测接口；记录两条 Known limitation（跨 Transport 可能超额、86400 秒滑动 ≠ UTC 0:00 重置）；分页计量单位定为按 HTTP 请求计；与 08 划清形态边界；无公开面变化、不建 ADR；07 随之解锁。
- [文档、CHANGELOG 与 ADR 怎么落](issues/07-docs-and-adr.md)：README「Retries and rate limiting」段改 `:113` 免责声明措辞、补三组说明（生效范围 / 默认关闭理由 / `replayable` 与 `raise_on_error` 两处）、不动 `:101`；CHANGELOG 不新增段 / 不写 Migration 行，只订正 `:336` 过期 Notes，并预留 10/12/13 位置；不建 0018、不动 ADR-0003；spec 七节骨架按施工阅读顺序排、第一步为模块注释与免责声明；`spec.md` 属 handoff 不在本图产出；07 不收图。12 重判后：因重试行为变化**需要 ADR-0018**（要点在 12 的 Answer）。
- [限额表条目要不要容纳计数维度与任意窗口](issues/08-limit-entry-shape.md)：保持二元组 `(requests, window_seconds)` + `path` 单键，不升级 value / 不改 key / 不引入 UTC 固定窗口 / 不体现 REST-WS 共享；官方维度与窗口语义差异交给 09 清单与 spec 判定规则承载；补全时非 2 秒窗口按秒数记并注明语义不等价；三条 Known limitation（按 instrument 计、同路径多方法、86400 秒滑动 ≠ UTC 重置）；无公开面变化、不建 0018、不写 Migration；08 未触发 06 边界、不新开工单。**09 补注**：特指的 `trade/order` POST+GET 数值相同，但 9 个多方法路径里 5 个数值不同，08 的泛指触发条件成立 → 14。
- [官方已公布限额的端点清单与 274/135 差异核对](issues/09-official-limit-endpoint-list.md)：AFK research 已解。01 取证的 `app.okx.com` 只是子集（135 路径 / 10 段），完整版 `www.okx.com` 为 395 声明 / 386 路径 / 16 段，S3 的 135 全部在 S1 内且数值零差异 → 01 结论成立但「135」是子集口径。S1 清单 395 行 100% 逐一绑定（数值 / 窗口 / 维度 / 多方法 / 来源锚点），中文 S2 交叉验证；对齐得两侧都有 241 / 仅官方 145 / 仅项目 33；逐一核验 0 个 REST 端点缺限额行（12 个用变体写法）；33 个仅项目有的按 03 归「未收录端点」；`bills-history-archive` 主文档与 Change Log 数值冲突未判定（按 10 流程重新取证）。findings 在 `research/official-limit-endpoint-list` @ `805528e`（永不合并、不 push）；无公开面变化、不建 ADR。
- [官方 Change Log 变更时表怎么同步](issues/10-changelog-sync.md)：维护流程定为随 SDK 端点更新顺带查 + 发版前复核 Change Log；只改表内已有条目的数值、新增端点按 03 验收线判定（施工）；数值变更进下一个版本 `### Changed`、不写 Migration 行不建 0018；快照日期语义改「最近一次核对日期」、每次同步更新；09 清单是一次性输入、不长期维护，长期来源以官方 Change Log + 端点详情页为准；10 无公开面变化、不收图。
- [重试与限流器的交互要不要改](issues/13-retry-limiter-interaction.md)：保持现状——每次重试仍占一个限流配额（与 06 的按 HTTP 请求计口径一致）、429 走固定指数退避且不与 limiter 显式联动（现有隐式配合已够，联动违反 06 的纯数据 + Out of scope 算法重写不动）；无公开面变化、不建 0018、不写 Migration，07 的触发条件未触发；两条现状写进 spec 第 ⑤ 节、不进 README；13 无公开面变化、不收图。
- [同路径多方法限额不同怎么处理](issues/14-multi-method-limits.md)：规则定为「按项目实际暴露的 HTTP 方法取值」，不取严、不取松；5 个值不同的路径里 4 个是「仅官方有」（`account/mmp-config`、`asset/monthly-statement`、`rfq/mmp-config`、`users/subaccount/apikey`）不进表、不是豁免；唯一两侧都有的 `bills-history-archive` 项目只调 POST，取 `12 requests per day`（主文档与 Change Log 2026-06-11 冲突，按 02 取原文、按 10 流程重新取证）；`order-algo` 值同（20/2s）只记数值、维度差异进 spec 已知差异；规则写进 spec §②；无公开面变化、不建 0018、不写 Migration。
- [OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](issues/11-idempotency-and-error-codes.md)：AFK research 已解。官方**没有**幂等键完整清单、没有「可重试 / 不可重试」分类、也没有 429 与业务码的优先级说明；`idempotency` 只在 flexible-loan 与 OKUSD 出现；`clOrdId` 等只保证 pending 内唯一、终态可复用，不保证去重。**50004 是超时 / 结果未知（官方明说「不代表成功或失败」），`okx/transport.py:22-24` 的注释无官方依据且对 50004 相反**；50001 = 服务不可用、50011 = 限流、50013 = 系统繁忙；另有 6 个 5xx 与大量「稍后重试」类 200 码。255 个 GET 无一条被官方描述为改状态，但也未声明无副作用。findings 在 `research/idempotency-and-error-codes` @ `09aac54`（永不合并、不 push）；无公开面变化、不建 ADR；12 随之解锁。
- [11 的事实要不要改重试判定](issues/12-retry-facts-followup.md)：把「可重试」拆三类，只对「处理前失败」（50001 / 50011 / 50013，官方说 try again / throttle）自动重试；**结果未知（50004 / 51149，官方说 check result）一律不自动重试**，新增 `_OUTCOME_UNKNOWN_CODES` 先于 5xx 判断；`_IDEMPOTENCY_KEYS` 不扩充（clOrdId 非 exactly-once）；GET 判定不收紧；注释改写；行为变化进 CHANGELOG `### Changed`、不写 Migration；**需要 ADR-0018**（要点入 12 的 Answer、handoff 落盘）；部分修订 04 的「可重试码」结论，不重开 04。**12 是最后一张工单，至此收图。**

## Not yet specified

（无——两条 fog 已在 [限流器形态与共享边界](issues/06-limiter-shape.md) 处置：「限流与重试的相互作用」graduate 成 [重试与限流器的交互要不要改](issues/13-retry-limiter-interaction.md)，「分页计量单位」的答案并入 06 的 Answer。）

## Out of scope

- WS 层限速与重连退避：归 ADR-0005 / ADR-0016 的连接监督者，属别的 effort。
- 限流算法重写（滑动窗口 → 令牌桶 / 并发控制）：除非图内某张决策明确要求，否则不动。
- 按 VIP / 账户层级在运行时动态拉取限额：需要运行时账户信息，且缺稳定外部来源。
- 把策略落成代码、发版，以及把本地积压提交推到 origin。
- 新建 `GLOSSARY.md`：两轮评审都记过，属 E 类小任务；本图不产该文件。
- 把端点表补全到验收线（官方已公布限额的端点）是施工，不是决策。
- 在表补全到 03 的验收线后重新评估两个默认开关是否翻：属新的破坏性批次 / 新 effort，本图不处理（触发条件见 [两个默认开关是否从 off 改 on](issues/05-default-switches.md) 的 Answer）。
- 跨 `Transport` 实例的限流计数共享（按 User ID 等计数维度合并）：属新 effort，本图不处理（Known limitation 见 [限流器形态与共享边界](issues/06-limiter-shape.md) 的 Answer）。
- 表条目升级（value 三元组 / key `(method, path)` / UTC 0:00 固定窗口 / 按计数维度计数）：属新 effort，并需重审 limiter 形态（06 边界），本图不处理（触发条件见 [限额表条目要不要容纳计数维度与任意窗口](issues/08-limit-entry-shape.md) 的 Answer）。

# 地图：限流与重试策略（rate-retry-policy）

Labels: wayfinder:map

## Destination

一份可交接的《限流与重试策略 spec》+ 一组已锁定的决策：端点限额表怎么覆盖、重试判定是否改动、两个默认开关是否翻、限流器形态、文档与迁移说明怎么落。本图**规划不做**——不改代码、不发版、不把积压提交推到 origin；「把约 274 个端点补全进 `RATE_LIMITS`」是图外施工。收图时路要清到施工方照着 spec 就能动手。

## Notes

- 领域：REST 传输层限流（`okx/consts/rate_limits.py`、`okx/rate_limit.py`）与重试（`okx/transport.py`、ADR-0003）。当前表只有 8 条路径、表外端点不限流；`rate_limit=False`、`max_retries=0` 均默认关闭。
- 术语（Q2 已定，02、04、05、06 的 Answer 增补）：「覆盖」只指**端点路径是否进 `RATE_LIMITS` 表**；「重试判定」再分立为 `replayable`（能不能发第二次）与 `transient`（这次失败值不值得重发）；「账户层级口径」不再指 VIP 分级、改指「数值来源口径」；「表外端点」定名为「未收录端点」（项目未收录，非官方未公布）。`rate_limit=True` 只指「表内 8 条路径的阻塞式滑动窗口」、`max_retries=N` 只指「对 `replayable ∩ transient` 的失败最多重发 N 次」，均非「全局限流 / 所有请求重试」。「共享限流状态」分立为「共享 limiter 实例」（同一 Transport 内）与「共享计数」（跨 Transport 按 User ID 合并）。07 另澄清：Destination 的「spec」是 handoff 交付物、不在本图产出。本轮不新建 `GLOSSARY.md`（`docs/agents/domain.md` 要求缺失时静默略过）。
- 事实与决策分工（Q3 已定）：口径（目标账户层级、文档快照日期、表外端点默认处置）由人在 HITL 工单拍板；外部文档事实由 `research`（AFK）工单查回；「查文档」本身不算决策工单。work-through 阶段新建的 research 工单创建后留在 frontier、不主动 fire 子代理（charting 步骤 5 才 fire）。
- 顺序细化：[OKX 官方限流文档的事实结构](issues/01-okx-rate-limit-docs.md) 先铺事实、[采用哪个账户层级口径与文档快照](issues/02-limit-scope.md) 基于事实拍板，故后者 blocked by 前者。这样 charting 阶段能立刻 fire AFK research，口径也不至于凭空定；Q3 的分工不变。
- 工单格式：本地 tracker，见 `docs/agents/issue-tracker.md` 的「Wayfinding operations」。`Type:` 行表达 `wayfinder:<type>` 标签；`Status: open` = 未认领，认领改 `claimed`，解完改 `resolved`；`Blocked by:` 写编号，无阻塞写 `—`。
- 默认工单类型 `grilling`（HITL，配 `/grilling` + `/domain-modeling`）；`research` 为 AFK，可并行。每会话只解一张（research 例外）。
- 凡动公共契约的决策补 `docs/adr/`（当前最大 0017，下一张 0018）。
- 语言：中文。图内不改代码、不发版、不 push。

## Decisions so far

- [OKX 官方限流文档的事实结构](issues/01-okx-rate-limit-docs.md)：官方无集中限额表，数值分散在各端点详情；窗口不统一、普通端点不按 VIP 分层、表外端点无通用政策表述；现有 8 条数值全部对得上，但官方还带计数维度与 REST/WS 共享等信息。全文在 `research/okx-rate-limit-docs` 分支（永不合并）。
- [采用哪个账户层级口径与文档快照](issues/02-limit-scope.md)：数值取官方端点详情页固定值、不按 VIP 分级，删 `rate_limits.py` 的 floor / stable 注释；「表外」定名「未收录端点」并维持不限流、不兜底；快照 2026-11-06；口径落注释 + README、不新建 ADR；覆盖目标移到 03。
- [表外端点怎么处置、表要不要全量补全](issues/03-table-coverage.md)：覆盖验收线定为「官方已公布限额且与项目路径常量对应的端点」，不以 274 为分母；spec 只给判定规则与取数方法、不列最终表；未收录端点维持不限流 / 不兜底（归 02）；断言按验收线集合、实现依赖 09；条目形状归 08。
- [重试判定是否改动](issues/04-retry-judgement.md)：ADR-0003 三条全维持（幂等键集合、可重试码、GET 一律 replayable 都不动）；`replayable=True` 逃生口保留并写进文档、不翻按端点白名单；429/5xx 优先、TransportError 不走 `_is_transient`、`raise_on_error=False` 永不重试按现状记录；无公开面变化、不建 ADR 不写 Migration；外部事实缺口开 11，后续由 12 承接。
- [两个默认开关是否从 off 改 on](issues/05-default-switches.md)：`rate_limit` 与 `max_retries` 都保持 off（三选一取「都不翻」）；理由为表仅 8 条、判定原状下重试不透明、ADR-0004 要求小破坏性需求攒着；无公开面变化、不建 ADR、不写 Migration 行、不改现有措辞；README 补偿说明归 07；重开条件写 Out of scope。
- [限流器形态与共享边界](issues/06-limiter-shape.md)：四问全维持现状——per-Transport 不共享计数、同步阻塞 + `_sleep` 注入、滑动窗口不改算法、纯数据不加可观测接口；记录两条 Known limitation（跨 Transport 可能超额、86400 秒滑动 ≠ UTC 0:00 重置）；分页计量单位定为按 HTTP 请求计；与 08 划清形态边界；无公开面变化、不建 ADR；07 随之解锁。
- [文档、CHANGELOG 与 ADR 怎么落](issues/07-docs-and-adr.md)：README「Retries and rate limiting」段改 `:113` 免责声明措辞、补三组说明（生效范围 / 默认关闭理由 / `replayable` 与 `raise_on_error` 两处）、不动 `:101`；CHANGELOG 不新增段 / 不写 Migration 行，只订正 `:336` 过期 Notes，并预留 10/12/13 位置；不建 0018、不动 ADR-0003；spec 七节骨架按施工阅读顺序排、第一步为模块注释与免责声明；`spec.md` 属 handoff 不在本图产出；07 不收图。

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

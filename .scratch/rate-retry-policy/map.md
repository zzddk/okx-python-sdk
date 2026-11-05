# 地图：限流与重试策略（rate-retry-policy）

Labels: wayfinder:map

## Destination

一份可交接的《限流与重试策略 spec》+ 一组已锁定的决策：端点限额表怎么覆盖、重试判定是否改动、两个默认开关是否翻、限流器形态、文档与迁移说明怎么落。本图**规划不做**——不改代码、不发版、不把积压提交推到 origin；「把约 274 个端点补全进 `RATE_LIMITS`」是图外施工。收图时路要清到施工方照着 spec 就能动手。

## Notes

- 领域：REST 传输层限流（`okx/consts/rate_limits.py`、`okx/rate_limit.py`）与重试（`okx/transport.py`、ADR-0003）。当前表只有 8 条路径、表外端点不限流；`rate_limit=False`、`max_retries=0` 均默认关闭。
- 术语（Q2 已定）：「覆盖」只指**端点路径是否进 `RATE_LIMITS` 表**；另两件分别叫「重试判定」「账户层级口径」，不混用。本轮不新建 `GLOSSARY.md`（`docs/agents/domain.md` 要求缺失时静默略过）。
- 事实与决策分工（Q3 已定）：口径（目标账户层级、文档快照日期、表外端点默认处置）由人在 HITL 工单拍板；外部文档事实由 `research`（AFK）工单查回；「查文档」本身不算决策工单。
- 顺序细化：[OKX 官方限流文档的事实结构](issues/01-okx-rate-limit-docs.md) 先铺事实、[采用哪个账户层级口径与文档快照](issues/02-limit-scope.md) 基于事实拍板，故后者 blocked by 前者。这样 charting 阶段能立刻 fire AFK research，口径也不至于凭空定；Q3 的分工不变。
- 工单格式：本地 tracker，见 `docs/agents/issue-tracker.md` 的「Wayfinding operations」。`Type:` 行表达 `wayfinder:<type>` 标签；`Status: open` = 未认领，认领改 `claimed`，解完改 `resolved`；`Blocked by:` 写编号，无阻塞写 `—`。
- 默认工单类型 `grilling`（HITL，配 `/grilling` + `/domain-modeling`）；`research` 为 AFK，可并行。每会话只解一张（research 例外）。
- 凡动公共契约的决策补 `docs/adr/`（当前最大 0017，下一张 0018）。
- 语言：中文。图内不改代码、不发版、不 push。

## Decisions so far

（空——charting 不 hand-resolve 任何工单。每解一张，在此追加一行「工单名：一句话答案」并链到工单。）

## Not yet specified

- **限流与重试的相互作用**：重试的那一次尝试是否再占一个限流配额、服务端 429 是否触发自适应退避。现在只能看出「这里有个交互问题」，要等 [重试判定是否改动](issues/04-retry-judgement.md) 与 [限流器形态与共享边界](issues/06-limiter-shape.md) 的答案才能拆成能拍板的决策。
- **分页 / 批量调用下限额的计量单位**：`paginate()` 每页都走同一路径，限流按 HTTP 请求计还是按一次逻辑操作计。要等 [表外端点怎么处置、表要不要全量补全](issues/03-table-coverage.md) 与 [限流器形态与共享边界](issues/06-limiter-shape.md) 定了才问得准。
- **若决定全量补全端点表，之后的维护机制**：谁核对官方更新、按什么节奏、数值变更如何进 CHANGELOG。依赖 [表外端点怎么处置、表要不要全量补全](issues/03-table-coverage.md) 的答案，现在还问不出形状。

## Out of scope

- WS 层限速与重连退避：归 ADR-0005 / ADR-0016 的连接监督者，属别的 effort。
- 限流算法重写（滑动窗口 → 令牌桶 / 并发控制）：除非图内某张决策明确要求，否则不动。
- 按 VIP / 账户层级在运行时动态拉取限额：需要运行时账户信息，且缺稳定外部来源。
- 把策略落成代码、发版，以及把 72 个本地积压提交推到 origin。
- 新建 `GLOSSARY.md`：两轮评审都记过，属 E 类小任务；本图不产该文件。
- 把约 274 个端点全量查全填进 `RATE_LIMITS`：是施工，不是决策。

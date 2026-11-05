# 07 · 文档、CHANGELOG 与 ADR 怎么落

Type: grilling
Status: resolved
Blocked by: 03, 04, 05, 06

## Question

前面几张定完之后，拍板「spec 怎么交接、公开面变化怎么记录」：

1. README 的「Retries and rate limiting」段（README.md:99–113）怎么写？特别是「表外端点不限流」这句免责声明在 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 之后还留不留。
2. CHANGELOG 的哪一段承接？`### Migration` 表要覆盖哪些公开面变化（默认值、幂等键集合、可重试错误码、表覆盖）？
3. 需要补哪些 ADR？从 0018 起编号：哪些决策是「难回退 + 不看上下文会奇怪 + 真有取舍」的（按 `/domain-modeling` 的三条判据），哪些只进 spec / CHANGELOG 就够。
4. spec 本身的骨架：按什么顺序呈现这些决策，施工方拿到后第一步做什么。

依赖 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)、[重试判定是否改动](04-retry-judgement.md)、[两个默认开关是否从 off 改 on](05-default-switches.md)、[限流器形态与共享边界](06-limiter-shape.md)，因为要等所有决策定了才知道要写什么。本工单只定「文档结构与归属」，不写正文、不改文件。

> **来自 02 / 03 / 10 的输入（2026-11-06）**：02 定下 README.md:113 免责声明「保留为行为描述，但不再被读成官方没给值」，03 把具体行文归本工单；03 另把表覆盖断言的口径定为「验收线集合」（不是 274 分母），实现归施工。10 会拍板数值变更进 CHANGELOG 的哪一段，本工单定文档结构时预留该位置。

> **来自 04 的输入（2026-11-06）**：04 维持 ADR-0003 三条原状、无公开面变化，因此 **04 不贡献 `### Migration` 行、也不新建 ADR**。但有两处说明需写进文档：① `Transport.request` / `OkxClient.request` 的 `replayable=True` 显式覆盖入口（`okx/transport.py:78`、`okx/okxclient.py:31,38`）；② `raise_on_error=False` 时永不重试（README.md:111 与 CHANGELOG.md:330 目前未说明）。ADR-0003 要不要补一句说明也由本工单统一判断；若 [OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](11-idempotency-and-error-codes.md) 查出确凿遗漏、由 [11 的事实要不要改重试判定](12-retry-facts-followup.md) 决定改动，届时再判断 ADR 与 Migration 归属。

> **来自 05 的输入（2026-11-06）**：[两个默认开关是否从 off 改 on](05-default-switches.md) 决定 `rate_limit` / `max_retries` 都保持 off，因此 **05 不贡献 `### Migration` 行、也不新建 ADR**；README.md:101 与 CHANGELOG.md:329 的「默认关闭」措辞与代码一致，不改。但「Retries and rate limiting」段要写出三件事：① 两个开关各自的实际生效范围（`rate_limit=True` 只作用于表内 8 条路径、非全局限流；`max_retries=N` 只对 `replayable ∩ transient` 生效，且 `raise_on_error=False` 时不重试）；② 默认关闭的理由（表未补全 + ADR-0004 攒着）；③ 显式打开的代码示例（README.md:105-109 已有）。05 只定方向，正文由本工单定结构、施工写。

> **来自 06 的输入（2026-11-06）**：[限流器形态与共享边界](06-limiter-shape.md) 四问全维持现状、无公开面变化，因此 **06 不贡献 `### Migration` 行、也不新建 ADR**；07 随 06 resolved 解锁。但有一处过期文档要订正：CHANGELOG.md:336 仍写「Passing `client=` copies the retry and rate-limit settings from that client, including the shared limiter」，而 `okx/okxclient.py:16-19` 现在只接受 `Transport`、没有 `client=` 参数。另 06 定「limiter 保持纯数据、不加可观测接口，需要时用 `logging`」，若文档要说明排查方式按这个口径写；[重试与限流器的交互要不要改](13-retry-limiter-interaction.md) 若决定改动，再由本工单判断其 ADR / Migration 归属。

## Answer

文档结构与归属已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：本图不新增 CHANGELOG 段、不写 `### Migration` 行、不新建 ADR；07 只定结构，正文属施工。**

**文档现状基线**：
- CHANGELOG 顶部是 `## [0.15.0]`，无 Unreleased 段；段结构 `### Changed` / `### Removed` / `### Migration` / `### Added` / `### Fixed`，`### Migration` 是 `| Before | After |` 两列表（`:61`）。
- `docs/adr/` 最大 0017，无 0018；ADR 格式为中文「背景 → 我们决定：**…** → `## Considered Options` → `## Consequences`」。
- README 的 `### Retries and rate limiting` 在 `:99-113`（`:101` 默认关闭、`:105-109` 示例、`:111` 重试说明、`:113` 免责声明），后接 `### Pagination`(`:115`)。
- 仓库有 `.scratch/<effort>/spec.md` 惯例，本 effort 尚无 spec.md；本工单的 Question 限定「只定文档结构与归属，不写正文、不改文件」。
- 「归 07」的事项共 7 类（免责声明改写 / 04 两处说明 / 05 三件事 / CHANGELOG:336 订正 / ADR-0003 是否补说明 / 10 的段落预留 / 12/13 的 ADR-Migration 归属）。
- **口径澄清**：02 定「口径写进 `okx/consts/rate_limits.py` 模块注释 + README」，而地图 Out of scope 写「图内不改代码」——模块注释改写属**施工项**（无行为变化），不是被排除的「把策略落成代码」。
- 01–06 全部「无公开面变化 / 不建 ADR / 不写 Migration 行」；08/09/10/11/12/13 六张仍未解，07 的 `Blocked by` 不含它们。

1. **README 段结构**：保留 `### Retries and rate limiting`(`:99-113`) 的骨架与位置，**改一处、补三组、保留一处、不动一处**：
   - **改** `:113` 免责声明：保留「未收录端点不限流」为**行为描述**，措辞改成「这是 SDK 表的覆盖范围，不是官方没有限额」（02 定方向、03 归本工单）。
   - **补①** 两个开关各自的实际生效范围（05）：`rate_limit=True` 只作用于表内 8 条路径、非全局限流；`max_retries=N` 只对 `replayable ∩ transient` 生效，且 `raise_on_error=False` 时不重试。
   - **补②** 默认关闭的理由（05）：表未补全 + ADR-0004 攒着。
   - **补③** 04 的两处说明：`Transport.request` / `OkxClient.request` 的 `replayable=True` 显式覆盖入口（`okx/transport.py:78`、`okx/okxclient.py:31,38`）；`raise_on_error=False` 时永不重试。
   - **保留** 显式打开示例 `:105-109`；**不动** `:101` 的「默认关闭」措辞（05 已确认与代码一致）。
   - 07 只定「哪些段落承载什么」，正文由施工写。
2. **CHANGELOG 与 Migration**：**本图不新增版本段、不写任何 `### Migration` 行**——01–06 全无公开面变化，且地图 Out of scope 排除发版。唯一 CHANGELOG 改动是**订正过期 Notes**：`:336` 的「Passing `client=` copies … including the shared limiter」与 `okx/okxclient.py:16-19`（现在只接受 `Transport`、无 `client=`）矛盾（06 发现）。另**预留两处位置**：10 拍板「数值变更进哪一段」、12/13 若决定改动时的 Migration 行（按 ADR-0004 成批时再写）。
3. **ADR 判断（0018 起）**：**不新建 0018，也不改 ADR-0003 原文**。按 `/domain-modeling` 三判据逐条：01–06 全是「维持现状」或 spec 层规划决策，虽真有取舍，但理由已完整记在各工单 Answer + 地图 Decisions-so-far，未来读者先读地图即可，「不看上下文会奇怪」不成立；且没有落地为代码 / 公开契约的变化。04 的 `replayable` / `raise_on_error` 澄清写进 README 即可。**触发条件**：12/13 若决定改动，届时按三判据重新判断，不重开 07。
4. **spec 骨架与产出边界**：骨架按**施工方阅读顺序**排七节：① 数值口径与快照(02) → ② 覆盖验收线与判定规则(03) → ③ 表条目形状(08，待解) → ④ 限流器形态(06) → ⑤ 重试判定与默认值(04/05) → ⑥ 文档与迁移清单(07) → ⑦ 施工项清单。施工方**第一步**先做 02 的 `rate_limits.py` 模块注释改写 + README.md:113 措辞（无行为风险、可独立验收）。**spec.md 不在本图产出**——它是 handoff 交付物，07 只定骨架与顺序，不写正文、不建文件。
5. **施工项清单与归属**（07 不写正文）：① `okx/consts/rate_limits.py:5-7` 模块注释改写（删 floor / stable 两句，改为「数值来自各端点详情页、随 Change Log 变动」）；② README 段的改一 / 补三；③ CHANGELOG.md:336 过期 Notes 订正；④ 表覆盖断言（口径「验收线集合」、实现依赖 09）；⑤ ADR 与 Migration 行（当前无，按第 3 条触发条件）。

## 边界

- **07 自身无公开面变化**：不建 ADR、不写 `### Migration` 行、不新增 CHANGELOG 段；与 02/03/04/05/06 的「ADR 归属由 07 统一判断」一致收口。
- **术语磨尖（`/domain-modeling`）**：地图 Destination 的「一份可交接的 spec」是**目的地的形态 / handoff 交付物**，不是本图产出物；本图产出的是决策（工单 Answer + 地图 Decisions-so-far）。
- **不收图**：07 的 `Blocked by` 是 03/04/05/06、不含 08/09/10/11/12/13，所以能先解；答案里的「预留 / 待解」是**触发条件**而非待定决策。还有六张未解，07 不代解、不重开；10 拍板段落、12/13 决定改动时按第 2/3 条各自推进，都不回头改 07。
- 本图只决策，不改 README / CHANGELOG / `okx/` 代码、不新建 `spec.md` / ADR；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理）。

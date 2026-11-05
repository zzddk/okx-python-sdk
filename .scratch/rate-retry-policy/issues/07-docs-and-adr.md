# 07 · 文档、CHANGELOG 与 ADR 怎么落

Type: grilling
Status: open
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

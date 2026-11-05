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

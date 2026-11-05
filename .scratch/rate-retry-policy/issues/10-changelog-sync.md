# 10 · 官方 Change Log 变更时表怎么同步

Type: grilling
Status: open
Blocked by: 03

## Question

由地图 Not yet specified 的「维护机制」graduate 而来（2026-11-06）。[采用哪个账户层级口径与文档快照](02-limit-scope.md) 发现官方页没有统一版本号 / last updated，只有按日期倒序的 Change Log，且已有多次限流变更（2026-05-08 `20/2s → 3/second`、2026-06-11 `12/day → 1/10s per user`）；02 把口径定为「快照 2026-11-06 + 来源清单」，[表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 把验收线定为「官方已公布限额的端点」，并明确数值随官方 Change Log 变动。

要拍板的是**维护流程**，不是数值本身：

1. 触发：官方 Change Log 出现限流变更时，靠什么发现——定期核对、随 SDK 端点更新顺带查、还是等用户报障？节奏与责任人写进哪里？
2. 同步：变更一条限额时，改 `RATE_LIMITS` 的判据是什么（只对已在表内的端点，还是同时补新端点）？谁有权改？
3. 记录：数值变更进 CHANGELOG 的哪一段？算不算公开面变化、`### Migration` 要不要一行？要不要 ADR（0018 起，由 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 统一判断归属）？
4. 快照日期怎么处理：每次同步后更新注释里的快照日期，还是改成「最近一次核对日期」？
5. 与 [官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的关系：清单要不要一并维护、由谁维护？

解本工单时若 09 已 resolved 则 zoom 它的清单；维护流程不依赖清单的具体内容。只决策流程，不改 `okx/consts/rate_limits.py` / CHANGELOG。

> **来自 07 的输入（2026-11-06）**：[文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 已定 CHANGELOG 结构——本图不新增版本段、不写 `### Migration` 行，只订正 CHANGELOG.md:336 的过期 Notes；并**预留**了「数值变更进 CHANGELOG 哪一段」的位置，由本工单拍板具体段落。解本工单时先 zoom 07 的 Answer。

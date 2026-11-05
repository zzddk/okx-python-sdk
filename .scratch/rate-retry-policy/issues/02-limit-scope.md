# 02 · 采用哪个账户层级口径与文档快照

Type: grilling
Status: resolved
Blocked by: 01

## Question

在 [OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 铺回的事实之上，定下这张图里所有限额数值的**口径**。要拍板：

1. 目标账户层级：限额按普通用户、还是某个 VIP 等级给？`okx/consts/rate_limits.py` 的模块注释现在写着「treat these numbers as a floor」——继续按最保守的 floor，还是按目标层级？
2. 文档快照：引用哪一天的官方文档作为数值来源？后续官方更新怎么算（重开这张工单、还是另立维护机制）？
3. 表外端点的默认处置口径：继续「查不到就不限流」，还是给一个保守兜底（如统一 N 次 / 2s）？给出兜底值，或者明确「不兜底」。
4. 口径的落点：写进 `rate_limits.py` 的模块注释、README，还是 ADR？

这个口径会决定 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)、[两个默认开关是否从 off 改 on](05-default-switches.md)、[限流器形态与共享边界](06-limiter-shape.md) 的答案尺度，所以先定。

若 [OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 发现官方根本没有全量端点表，还要顺带决定：图内「覆盖」的目标改成什么——是「覆盖官方已公布的」还是「覆盖全部端点」。

> **已迁移（2026-11-06）**：01 确认官方没有全量端点表、数值分散在各端点详情页；且「覆盖目标」与 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 第 3 点重复，违反「一个决策只住一处」。该决策整体移到 03，本工单只定数值口径。

## Answer

口径已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**前提修正**：01 的 findings 推翻了上面 Question 里的两处假设——官方对普通端点不按 VIP 分层；「表外 = 查不到限额」不成立（`/api/v5/account/bills` 不在项目表里，官方仍给 `5 requests per second`）。

1. **数值口径**：表内数值一律取官方各端点详情页公布的固定值，不按账户 / VIP 等级调整。`okx/consts/rate_limits.py:5-7` 两句注释一并改写——删掉「for the account tier you target — higher VIP levels get larger limits, so treat these numbers as a floor」（无官方依据），把「whose published limits are stable」改成「数值来自各端点详情页，随官方 Change Log 变动」（Change Log 有 2026-05-08 `20/2s → 3/second`、2026-06-11 `12/day → 1/10s per user`，stable 不成立）。术语「账户层级口径」在本图不再指 VIP 分级，改指「数值来源口径」。
2. **术语与未收录端点**：「表外端点」定名为**「未收录端点」**——指项目 `RATE_LIMITS` 尚未收录，不是「官方未公布限额」；本图不假设存在官方无限额的端点。未收录端点**维持不限流、不设统一兜底**：兜底值无官方依据，且窗口不统一（`12/day`、`20/month` 会被一个统一 `N 次/2s` 误放）。README.md:113 保留为行为描述，但不再被读成「官方没给值」。补全未收录端点归 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)。
3. **文档快照**：以抓取快照日期 **2026-11-06** 为准，附取证来源与范围清单（完整来源在 01 的 findings；`rate_limits.py` 注释里只写简短一句）。官方页无统一版本号 / last updated，可引用的是 Change Log 日期条目（最新带日期 2026-10-27）。后续官方数值变更的维护机制留在地图 Not yet specified，等 03 定了再 graduate，本工单不定。
4. **口径落点**：写进 `okx/consts/rate_limits.py` 模块注释（数值来源、快照、未收录的定义）+ README 使用说明；**不新建 ADR**——按 `/domain-modeling` 三判据，注释改写不难回退、也非「不看上下文会奇怪」的意外；ADR 归属由 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 统一判断。
5. **排除的官方例外**：口径明写「本表不表达 colocation / 做市商议价额度 / 订单类 VIP5+ 子账户 fill-ratio 例外，也不替用户推断适用等级」；这些是账户侧安排而非端点属性，不另开工单。

## 边界

本口径只管二元组 `(请求数, 窗口秒)` 能表达的部分。以下不在 02 内：计数维度（`Rate limit rule`）、UTC 0:00 重置的固定窗口、REST/WS 共享限额、同路径 POST + GET 两方法、窗口长度不统一。它们由 [限流器形态与共享边界](06-limiter-shape.md)、[限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 与 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 承接。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解）。

# 02 · 采用哪个账户层级口径与文档快照

Type: grilling
Status: open
Blocked by: 01

## Question

在 [OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 铺回的事实之上，定下这张图里所有限额数值的**口径**。要拍板：

1. 目标账户层级：限额按普通用户、还是某个 VIP 等级给？`okx/consts/rate_limits.py` 的模块注释现在写着「treat these numbers as a floor」——继续按最保守的 floor，还是按目标层级？
2. 文档快照：引用哪一天的官方文档作为数值来源？后续官方更新怎么算（重开这张工单、还是另立维护机制）？
3. 表外端点的默认处置口径：继续「查不到就不限流」，还是给一个保守兜底（如统一 N 次 / 2s）？给出兜底值，或者明确「不兜底」。
4. 口径的落点：写进 `rate_limits.py` 的模块注释、README，还是 ADR？

这个口径会决定 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)、[两个默认开关是否从 off 改 on](05-default-switches.md)、[限流器形态与共享边界](06-limiter-shape.md) 的答案尺度，所以先定。

若 [OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 发现官方根本没有全量端点表，还要顺带决定：图内「覆盖」的目标改成什么——是「覆盖官方已公布的」还是「覆盖全部端点」。

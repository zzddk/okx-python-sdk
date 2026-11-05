# 05 · 两个默认开关是否从 off 改 on

Type: grilling
Status: open
Blocked by: 02, 03

## Question

`rate_limit=False`（`okx/transport.py:46`）与 `max_retries=0`（同文件 :45）现在都默认关闭，README.md:101 说「passing the new arguments is the only way to turn them on」。拍板：

1. 改还是不改？两个一起改、只改一个、还是都保持 off？
2. 关键取舍：在表只有 8 条端点（[表外端点怎么处置、表要不要全量补全](03-table-coverage.md) 定下覆盖前尤其如此）时打开 `rate_limit`，实际只对 8 个路径生效——会不会给用户「已经全局限流」的错觉？打开 `max_retries` 则在 ADR-0003 的约束下只对 GET 与带幂等键的 POST 生效。
3. 若改：属于公开面变化，按 ADR-0004 要成批发版，进哪个 minor？CHANGELOG 的 `### Migration` 表要写哪几行？
4. 若只改一个或不改：理由写清楚，README 的「默认关闭」说明要不要同步调整措辞。

依赖 [采用哪个账户层级口径与文档快照](02-limit-scope.md) 与 [表外端点怎么处置、表要不要全量补全](03-table-coverage.md)，因为默认打开后的实际收益与风险取决于表覆盖到什么程度。

> **来自 03 的输入（2026-11-06）**：03 已把覆盖验收线定为「官方已公布限额且与项目路径常量对应的端点」，但表仍是 8 条——补全属图外施工，spec 不承诺补全进度。因此本工单「表只有 8 条端点」的前提不变，讨论默认值时按 8 条算；[官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的清单回来后，若施工已把表补全，需重新评估本工单的收益判断。

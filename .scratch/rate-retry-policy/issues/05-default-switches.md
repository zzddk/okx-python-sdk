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

# 地图：2026-11-06 全项目审查（review-2026-11-r3）

> **状态（2026-11-06）**：评审已出，八张工单已开，全部 `needs-triage`；尚未开工，也没有拍板记录。

## Destination

把 2026-11-06 全项目审查的八个发现推到可施工：三处正确性（01–03）先定口径，签名与测试盲区（04–06）补齐，门禁与债务（07–08）合并批次。地图内不改代码、不发版。

## Notes

- 评审源：仓库根目录 `architecture-review-20261106-202110.html`（本次新增）。
- 基线（2026-11-06 实测）：`pytest` 856 passed / 313 subtests；覆盖率 97%（2023 行，漏 51）；`ruff 0.16.8` 默认规则 `okx/` 525 条、全仓 638 条、115 个文件待格式化；`master` 领先 `origin` 91 个提交，`v0.15.0` 在 `2c721a4`，HEAD `215dba9`。
- 候选编号 01–08 与前两批（`review-2026-11-r2` 的 01–06、更早的 01–06）重名；引用时必须带 effort 名。
- 语言：中文；工单沿用 `.scratch/<effort>/issues/NN-*.md`，Comments 追加在文件末尾。
- 判据优先级：ADR 与工单 Answer > 评审 HTML > README/CHANGELOG 的叙述。本次评审只给证据与建议，未替代任何 ADR。
- 2026-11-06 01 已落地（1469f30）：237 条表 + 37 条豁免 = 274 条已声明路径；新增端点未归类时测试会红。
- 2026-11-06 02 已落地（a37e054）：正常关闭也进 `on_lost`，登录不再空等；`reconnect=False` 仍由 task 抛 `ConnectionClosedOK`。
- 2026-11-06 03 已落地（e7ce80a）：登录被拒是永久错误，重连不再无限循环；task 以 `LoginRejected` 结束。
- 2026-11-06 04 已落地（1439a54）：REST 签名固定向量，GET query 与 POST body 各一条；不改生产代码。
- 2026-11-06 05 已落地（7c3e7f1）：`raise_on_error` 只管错误 payload，不关闭网络重试；三处文档统一。

## Decisions so far

- [01 · 限流覆盖不变量](issues/01-rate-limit-coverage-invariant.md)：豁免进 `okx/consts/rate_limits.py`（`RATE_LIMIT_EXEMPTIONS` + 原因码），可达集由 `test_contract.reachable_paths()` 派生；32 条标 `NOT_IN_OFFICIAL_LIST`，不删端点；逐条定性转 09。Done in 1469f30。
- [02 · 正常关闭不进 on_lost](issues/02-clean-close-on-lost.md)：捕 `ConnectionClosed` 基类；正常关闭也进 `on_lost`；`reconnect=False` 仍由 task 抛 `ConnectionClosedOK`。Done in a37e054。
- [03 · 重连把永久失败当瞬时失败](issues/03-reconnect-permanent-failures.md)：`PermanentConnectionError` + `LoginRejected`；`_reconnect` 遇永久错误直接结束 task，其余无限退避；不加尝试上限。Done in e7ce80a。
- [04 · REST 签名路径没有测试](issues/04-rest-signature-test.md)：测试 patch `okx.utils.get_timestamp` 固定时间；GET query 与 POST body 的签名逐字节断言；不加 clock 参数。Done in 1439a54。
- [05 · raise_on_error=False 的文档与行为相反](issues/05-raise-on-error-docs.md)：以代码为准；只改 README、spec 与 docstring，测试改名并补网络重试用例。Done in 7c3e7f1。

## Not yet specified

1. **33 条官方未收录路径的定性**：已立 research 09（废弃 / 拼错 / 未公开可用）；在 09 出结论前保持豁免，不删端点。
2. **lint 规则集与格式化**：只开 `E4,E7,E9,F`，还是一步到 `I/B/UP`？formatter 做不做？25 个星号导入改不改？影响 07 的规模。

## Out of scope

- 全量补齐 273 条限流值（属持续维护，不在本 effort）。
- 端点返回类型建模（`Dict[str, Any]` → 类型化响应），本评审未展开。
- 0.15.0 的 push：共享状态操作，需单独确认，不随本 effort 进行。
- 0.16.0 的发版节拍：等 01–08 的破坏面清点后再按 ADR-0004 决定。

## 工单索引

- [01 · 限流表的覆盖不变量](issues/01-rate-limit-coverage-invariant.md) — done (1469f30)
- [02 · 正常关闭不进 on_lost](issues/02-clean-close-on-lost.md) — done (a37e054)
- [03 · 重连把永久失败当瞬时失败](issues/03-reconnect-permanent-failures.md) — done (e7ce80a)
- [04 · REST 签名路径没有测试](issues/04-rest-signature-test.md) — done (1439a54)
- [05 · raise_on_error=False 的文档与行为相反](issues/05-raise-on-error-docs.md) — done (7c3e7f1)
- [06 · 限流接线与并发登录](issues/06-limiter-wiring-and-login-race.md) — task
- [07 · lint 门是装饰](issues/07-lint-gate.md) — grilling
- [08 · 清理批次](issues/08-cleanup-batch.md) — task
- [09 · 33 条官方清单未收录路径的逐条定性](issues/09-unlisted-paths-research.md) — research

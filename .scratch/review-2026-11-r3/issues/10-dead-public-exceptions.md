# 10 · 删除两个无引用的公共异常（0.16.0）

Type: task
Status: resolved
Done in: 0.16.0 (6a5fbc3)
Blocked by: —

## Question

`okx/exceptions.py` 里的 `OkxRequestException` 与 `OkxParamsException` 只被定义，仓库内零引用（`grep -rn` 无命中）。删除它们是公共面破坏，按 ADR-0004 必须进 minor；08 决定留到 0.16.0，本单记录施工要求。

## 要求

1. 在 0.16.0 的破坏性批次里删除两个类，CHANGELOG 的 `### Migration` 加一行。
2. 删除前再跑一次全仓 grep（含 docs / examples），确认无引用。
3. 不改 `OkxAPIException`。
4. 若届时已有外部依赖证据，改为先发一版带 `DeprecationWarning` 的过渡。

## Answer

**拍板（2026-11-06）**：现在删除，走 0.16.0 批次；不发 `DeprecationWarning` 过渡。

- 两个类在 SDK 内从未抛出，也没有从 `okx/__init__` 导出；发警告等于警告一个用户永远碰不到的名字，只会制造噪声。
- 删除前全仓 grep：除评审文档与本单外无引用；删除后只剩契约测试里的「必须不存在」列表。
- 变更：`okx/exceptions.py` 删除两个类；CHANGELOG 增加 `### Removed` 与 `### Migration` 两行；`test_naming.py` 增加两个「名字已移除」用例（删除前红、删除后绿）。
- 版本：Unreleased 因此成为破坏性，下一版必须是 0.16.0；与 11 的端点删除/改名共用同一段迁移说明。

**验收对照**：877 passed / 313 subtests；`ruff check okx/` 通过；grep 不再命中库代码。

## Comments

- 2026-11-06 由 08 拆出：08 工单 43f929e 已收口，删除动作等 0.16.0 批次。

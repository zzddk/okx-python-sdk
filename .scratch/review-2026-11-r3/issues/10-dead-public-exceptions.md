# 10 · 删除两个无引用的公共异常（0.16.0）

Type: task
Status: needs-triage
Blocked by: —

## Question

`okx/exceptions.py` 里的 `OkxRequestException` 与 `OkxParamsException` 只被定义，仓库内零引用（`grep -rn` 无命中）。删除它们是公共面破坏，按 ADR-0004 必须进 minor；08 决定留到 0.16.0，本单记录施工要求。

## 要求

1. 在 0.16.0 的破坏性批次里删除两个类，CHANGELOG 的 `### Migration` 加一行。
2. 删除前再跑一次全仓 grep（含 docs / examples），确认无引用。
3. 不改 `OkxAPIException`。
4. 若届时已有外部依赖证据，改为先发一版带 `DeprecationWarning` 的过渡。

## 未决

- 是否先用一个 patch 发出 `DeprecationWarning` 再删？对一个从未被 `okx/__init__` 导出的类，可能不值得。

## Comments

- 2026-11-06 由 08 拆出：08 工单 43f929e 已收口，删除动作等 0.16.0 批次。

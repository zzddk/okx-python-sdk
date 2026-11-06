# 08 · 清理批次

Type: task
Status: resolved
Done in: 43f929e
Blocked by: —

## Question

评审候选 08。以下各条单独都不致命，但合在一起会掩盖真正的信号：

| 项 | 现状 | 处理 |
|---|---|---|
| `okx/utils.py:75` | `utcnow()` 已弃用，整套测试 49 条 warning | 改 `now(timezone.utc)`，输出格式不变 |
| `docs/adr/0003-retry-idempotency.md:5` | 仍把 `50004` 列为可重试，已被 ADR-0018 细化 | 加一行指针/替代说明 |
| `okx/exceptions.py:30-45` | `OkxRequestException` / `OkxParamsException` 零内部引用 | minor 删除，进 Migration 表 |
| `okx/transport.py:192-195` | 退避无 jitter | 可选：加 ±20% 抖动 |
| `okx/pagination.py:101-104` | `max_pages` / `page_size` 无范围校验 | 负值在调用点报错 |

## 验收标准

1. 测试输出 warning 归零（或只剩第三方库的）。
2. ADR-0003 明确指向 ADR-0018 的细化结论。
3. 公共异常的删除有版本策略与 Migration 行；不混进 patch。
4. `pytest test/unit` 全绿。

## Answer

**拍板（2026-11-06）**：做 utcnow、ADR 指针、分页参数校验；死异常留到 0.16.0（转 10）；jitter 暂不做。

- utcnow：改 `datetime.now(timezone.utc)`，用 `.replace("+00:00", "Z")` 保持线上格式；测试断言格式、UTC 偏差 <5s、且不再触发 DeprecationWarning。
- 分页：`page_size <= 0` 与 `max_pages < 0` 在调用点抛 `ValueError`；用例断言 fetch 从未被调用。CHANGELOG 进 `### Changed`。
- ADR-0003：在决定段后加一行指向 ADR-0018（`50004` 已移除，其余不变）。
- 死异常：`OkxRequestException` / `OkxParamsException` 零引用，但删除是公共面破坏；留到 0.16.0，另立 10。
- jitter：可选时序优化，本次不做，不留半成品。

**验收对照**：875 passed / 315 subtests；测试 warning 从 56 降到 12（utcnow 警告消失）；两个分页用例在修复前失败、修复后通过。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 08。
- 2026-11-06 施工完成：43f929e（master）。分页校验、时区时间戳、ADR 指针；死异常转 10。

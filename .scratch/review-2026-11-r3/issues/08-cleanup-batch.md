# 08 · 清理批次

Type: task
Status: needs-triage
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

## 未决

- jitter 与分页参数校验是行为变化，是否需要单独用例与 CHANGELOG 行？建议要。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 08。

# 端点契约表与一次 sweep

Status: resolved
Release: 0.14.0（原定 0.13.0）

## 为什么

见 `spec.md` 与 ADR-0011。279 个端点的 method、path、参数名散在 24 个测试模块里，每个方法一份手写断言；端点方法本身已经退成一行参数清单，测试仍在复述它。

## 做什么

新增 `test/unit/okx/endpoints.py`（279 行表）与 `test/unit/okx/test_endpoint_table.py`（sweep + 完整性检查）；删除被表覆盖的逐方法用例，保留常量、取值语义、签名契约、跨端点对称四类。

## 完成标准

1. 表覆盖全部 279 个公开端点，`test_the_table_covers_every_public_method` 通过。
2. 每个端点的断言只剩「一次调用 + 哨兵值」，不再有手写 params dict。
3. 三次变异（键拼错、签名加参数、path 改错）各自被对应行抓到。
4. `pytest test/unit` 全绿；端点测试代码从 3332 行降到 1980 行（含新表）。
5. `ruff check test/unit` 的错误数不高于改动前。

## Comments

2026-11-05 — 已实现。表由一次性脚本从运行中的端点面导出（sweep 记录 method / path / 参数键），人工复核后提交；`PAYLOAD` 6 行、`[a b c]` 1 行（`grid_stop_order_algo`）。删除 7 个测试文件、113 个用例。`pytest test/unit` 806 passed。

# 01 · 端点模块覆盖的不变量 guard

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: —

## 为什么

`consts/__init__.py` 在两个地方绑定子模块（import 块与 `_MODULES`）。漏改一处已被 ruff F401 或导入期 `NameError` 抓住；漏改两处则新端点模块成为磁盘上的死代码，其常量永远进不了 `vars(consts)`，且无人报错。Q1=A 拍板用一条契约测试封住这最后一个方向，生产代码一点不动。

## 做什么

在 `test/unit/okxsdk/test_contract.py` 复用 `_const_assignments()`，新增 `test_every_declared_constant_is_exported()`：断言每个源文件顶层赋值的名字都在 `vars(consts)`，缺失时列出 `文件:常量名`。不改 `okxsdk/` 下任何文件。

## 完成标准

1. 当前代码下断言即绿（不变量 guard，非红→绿回归）：22 文件 / 274 赋值全已导出。
2. 新增未接线的 `consts/endpoints/*.py` 会让断言报出该文件的常量名。
3. `pytest test/unit` 全绿；`ruff check` 全绿。
4. `okxsdk/consts/__init__.py` 与端点模块一行不改。

## Comments

- 2026-11-07 建单并实现。`missing = []` 已实跑确认；`endpoints/__init__.py` 只有 docstring、endpoints 下无私有常量，无误报。
- 有效性实证：临时新增 `consts/endpoints/_drift_probe.py`（`PROBE_UNWIRED_PATH`），guard 报 `constants declared but never exported: ['_drift_probe.py:PROBE_UNWIRED_PATH']` → `1 failed`；删除探针后 `pytest test/unit` → 865 passed, 336 subtests passed，`ruff check` All checks passed。探针已删除，工作区无残留。

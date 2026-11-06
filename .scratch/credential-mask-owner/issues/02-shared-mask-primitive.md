# 02 · 统一敏感字段清单与共享掩码原语

Type: task
Status: resolved
Done in: b63aa67
Blocked by: 01

## 为什么

REST 侧 `utils.py:13` 用 `_SENSITIVE_HEADER_KEYS`（`OK-ACCESS-*`），WS 侧 `WsBaseAsync.py:295` 用内联字面量元组（`apiKey/passphrase/sign`）——同一策略两种命名、两份清单，且 `send:` 那条路径完全没掩。R3·Q1 拍板收敛成一份清单 + 一个模块级纯函数，零签名变更、不造新模块。

## 做什么

- `utils.py` 定义一份统一敏感字段名清单，收编 `c.OK_ACCESS_KEY` / `c.OK_ACCESS_SIGN` / `c.OK_ACCESS_PASSPHRASE` 与 `apiKey` / `passphrase` / `sign`。
- 新增**模块级**纯函数 `mask_sensitive(value)`（不进 `okxsdk` 包级导出）：递归遍历 dict / list，命中清单的键把值换成 `***`；返回**副本**，不改入参。
- `_masked_header()` 保留为薄包装，内部改调 `mask_sensitive`（`get_header` / `get_header_no_sign` 两处调用不变）。
- 删 `transport.py:157` 的重复 `body:{body}` 行，保留 `utils.py:33`（`pre_hash.debug` 仍有实效、接口不说谎）。
- 三个 `debug` 形参**保留且生效**，不动签名。

## 完成标准

1. `mask_sensitive` 对扁平 header dict 与嵌套 `{"args": [...]}` 都返回脱敏副本，原对象不变。
2. `test_logging.py` 既有 REST 契约用例一行不改即通过。
3. 工单 01 的 `send:` 主回归转绿（需与工单 03 同批落地）。
4. `pytest test/unit` 全绿；`ruff check` 全绿。

## Comments

- 2026-11-07 建单。与 03 同批落地：单独改 utils 不会让 `send:` 路径变绿。
- 2026-11-07 施工：`okxsdk/utils.py` 新增 `_SENSITIVE_FIELDS`（frozenset，收编两种命名）与 `mask_sensitive()`；`_masked_header()` 改为直接 `return mask_sensitive(header)`；`transport.py` 删掉 `:157` 的 `body:{body}` 行。三个 `debug` 形参保留且仍由 `transport.py:150,151,153` 显式传值。与 03 同批，`pytest test/unit` → 864 passed, 336 subtests passed，`ruff check okxsdk/ test/unit/` All checks passed。

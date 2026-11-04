# 修正公共命名缺陷

Status: ready-for-agent
Release: 0.5.0

## 为什么

`get_instruments(ugly=...)` 的 `ugly` 实为 `uly`（`Account.py:104`）；另有 `set_risk_offset_typel`（`Account.py:221`）、`get_VIP_*` 系列、`ACTIVSTE_OPTION`、`INDEX_CANSLES`、`VOLUMNE`、`PLACR_ORDER`。这些错误拼写已经进入公共 kwargs，改与不改都是成本。

## 做什么

按 ADR-0001 直接改名，不留别名；方法名统一 snake_case 且不带大写缩写段。

## 完成标准

CHANGELOG 里有「旧名 → 新名」对照表，覆盖每一处改动。

## Comments

- 2026-11-05: done in 0.5.0. Renamed the listed methods, kwargs and constants with no aliases; the CHANGELOG carries the full old-to-new table. Added `test/unit/okx/test_naming.py` so an accidental alias (or a lost rename) fails the suite.

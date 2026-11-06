# 打包元数据以实际支持面为准

`setup.py:48` 声明 `python_requires=">=3.7"`、classifiers 列 3.7–3.12，`ruff.toml:3` 按 `py37` 检查，而 `.github/workflows/ci.yml:93` 只跑 3.9 与 3.12；`login.py:45` 等处的 `int | None` / `dict[str, Any]` 只因 `from __future__ import annotations` 才在旧版本运行。四处声明互相不一致，且 3.7 / 3.8 从未被验证。构建还会报 `License classifiers are deprecated`（`setup.py:57`）。

我们决定：**把最低版本收敛到 CI 实际验证的下限，让 `python_requires`、classifiers、`ruff target-version`、CI 矩阵四处一致；许可元数据改用 SPDX 表达式，去掉已弃用的 classifier。** 工单 04 已拍板取 **3.9**：`>=3.9`、删 3.7 / 3.8 classifiers、`target-version = "py39"`，CI 矩阵不动。

## Considered Options

- **收窄到 `>=3.9`（拍板采纳）**：删 3.7 / 3.8 classifiers，`target-version = "py39"`，CI 不变。声明与验证一致，改动最小；代价是放弃两个已 EOL 的版本声明。
- **保持 `>=3.7` 并补 CI 作业**：声明最宽，但 3.7 已 EOL、`actions/setup-python` 未必提供，且 `int | None` 的静态检查口径要额外处理。
- **折中 `>=3.8` + CI 加 3.8**：多一个作业，覆盖一个仍有人用的版本。
- **只改文档不改声明**：最省事，但声明悬空的问题没有解决，排除。

## Consequences

- `python_requires` 与 classifiers 是公开的打包元数据：下限提高是否属破坏性、是否要进 minor 批次，按 ADR-0004 另判；CHANGELOG 记一条 Changed。
- `ruff.toml target-version` 变更后需重跑 `ruff check okxsdk/`；许可表达式变更后需重跑 `python -m build --no-isolation` + `twine check`，并确认 wheel 仍含 LICENSE 与 `py.typed`。
- sdist 的 `prune test` 属工单 `review-2026-11-r4/05`，不在本 ADR 范围（不改变公共契约）。
- 对应工单 `review-2026-11-r4/04`（2026-11-06 拍板取 A）。

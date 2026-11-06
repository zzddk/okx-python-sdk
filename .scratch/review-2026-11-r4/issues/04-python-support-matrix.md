# 04 · 声明的 Python 支持面与 CI 对齐

Type: grilling
Status: ready-for-agent
Blocked by: —

## Question

`setup.py` 声明 `>=3.7` 且 classifiers 列到 3.12，`ruff.toml` 按 `py37` 检查，但 CI 只跑 3.9 / 3.12。要定下**真正支持的最低版本**，并让四处声明（`python_requires`、classifiers、`target-version`、CI 矩阵）一致。本单改的是公开打包元数据，按惯例配 `docs/adr/0021-packaging-metadata-truthfulness.md`（已定稿生效）。

## 证据

- `setup.py:48` `python_requires=">=3.7"`；classifiers 含 3.7 / 3.8 / 3.9 / 3.10 / 3.11 / 3.12。
- `.github/workflows/ci.yml:93` `python-version: ["3.9", "3.12"]`；lint / dependency-check / build 固定 3.11。
- `ruff.toml:3` `target-version = "py37"`。
- `okxsdk/websocket/login.py:45` 用 `int | None`、`dict[str, Any]`；`WsPrivateAsync.py:19`、`WsPublicAsync.py:17,24` 用 `dict[...]` 下标。这些在 3.7 / 3.8 上**只因各模块 `from __future__ import annotations`** 才不报错，静态检查按 py37 会认为语法不支持。
- `requirements.txt`：`httpx[http2]>=0.24.0`（0.24.0 元数据 `Requires-Python: >=3.7`；0.28.1 是 `>=3.8`）、`websockets>=10.0`、`certifi>=2021.0.0`，均无上界，pip 在旧 Python 上会各自解析到兼容版本。
- `dev_requirements.txt` 锁 `ruff==0.16.8`，`pytest>=7` / `pytest-cov>=4` / `build>=1` 等无上界。
- 结论：**不是「3.7 装不上」的硬冲突**（已实测 httpx 0.24.0 元数据），而是 3.7 / 3.8 从未被任何 CI 作业验证过。
- 构建告警 `WARNING License classifiers are deprecated`（`setup.py:57` 的 `License :: OSI Approved :: MIT License`），建议改 SPDX 表达式；当前 `twine check` 通过、wheel 含 `licenses/LICENSE`，只是面向未来的清理。

## 建议方案

四处声明收敛到同一个下限；SPDX 许可元数据随本单一并落（同一处 `setup.py`、同一次构建验证）。

### 候选（已拍板：A）

- **A（拍板采纳）**：收窄到 `>=3.9`，删 3.7 / 3.8 classifiers，`ruff target-version = "py39"`，CI 矩阵不变。声明与验证一致，改动最小；代价是放弃两个已 EOL 的版本声明。
- **B**：保持 `>=3.7` 与 `py37`，CI 补 3.7 / 3.8 作业。声明最宽，但 3.7 已 EOL、`actions/setup-python` 未必提供，且要处理 `int | None` 在静态检查下的口径。
- **C**：折中 `>=3.8` + `target-version = "py38"`，CI 加 3.8。比 A 多一个作业，覆盖一个仍有人用的版本。

## 验收标准

1. `python_requires`、classifiers、`ruff.toml target-version`、CI 矩阵四者表达同一个最低版本。
2. `ruff check okxsdk/` 在新 target-version 下通过。
3. `python -m build --no-isolation` + `twine check` 通过，且不再出现 `License classifiers are deprecated` 告警；wheel 仍含 LICENSE 与 `py.typed`。
4. CHANGELOG 记一条 Changed；若下限提高属破坏性，按 ADR-0004 判断是否要进 minor 批次。
5. ADR-0021 已拍板生效、头部提案状态行已删除；本单代码已施工并验证但未提交，暂留 `ready-for-agent`，提交后再转 `resolved` 并补 `Done in:`。

## Answer

**拍板（2026-11-06）：A；ADR-0021 定稿生效。**

- 最低版本收敛到 **`>=3.9`**：`setup.py:48` 的 `python_requires` 改 `>=3.9`，删 3.7 / 3.8 两条 classifiers，`ruff.toml:3` 改 `target-version = "py39"`，`.github/workflows/ci.yml:93` 的 `["3.9", "3.12"]` **不动**。四处声明与 CI 实际验证面一致。
- SPDX 许可表达式随本单一并落（`setup.py:57` 的 `License :: OSI Approved :: MIT License` 换成 `license` 表达式），与新 target-version 用同一次 `python -m build --no-isolation` + `twine check` 验证；wheel 仍须含 LICENSE 与 `py.typed`。
- CHANGELOG 记一条 Changed。**下限提高是否属破坏性、要不要进 minor 批次，按 ADR-0004 另判**，不在本次拍板范围内。
- 不选 B（3.7 已 EOL、`setup-python` 未必提供，`int | None` 静态口径要额外处理）、C（多一个 CI 作业，收益不抵成本）。
- ADR-0021 头部提案状态行已删除，正文「具体取 3.9 / 3.8 / 3.7 由工单 04 拍板」改为「工单 04 已拍板取 3.9」，Considered Options 的 A 标为拍板采纳项。
- 状态暂留 `ready-for-agent`：代码已施工并验证但未提交，无 commit hash 可写 `Done in:`；提交后再转 `resolved`。

**施工（2026-11-06，并行子代理 C，未提交）**：

- `setup.py`：`>=3.9`、删 3.7 / 3.8 classifiers、`license="MIT"`、顺手把 `import okxsdk` 移到顶部（消 E402）。
- `ruff.toml`：`py37` → `py39`；注释由主线程同步为「覆盖 okxsdk/ 与 test/unit/」。
- `.github/workflows/ci.yml` 矩阵未动（按 A）；`CHANGELOG.md` 的 Changed 段由主线程统一写进 `## [Unreleased]`。
- 集成验证：`python -m build --no-isolation` 不再报 `License classifiers are deprecated`；wheel METADATA 为 `Requires-Python: >=3.9`、`License: MIT`、classifiers 仅 3.9–3.12；`twine check` PASSED；wheel 仍含 `licenses/LICENSE` 与 `okxsdk/py.typed`；sdist 不含 `test/`。
- **下限提高是否属破坏性、要不要进 minor 批次**：按 ADR-0004 另判，不在本次施工范围，仍是未决项。

## Comments

- 2026-11-06 审查提出：P2。核实过 httpx 0.24.0 元数据，「3.7 无法安装」是误判，未列入发现。
- 2026-11-06 用户逐条拍板取 A、两张 ADR 都生效；结论落在 `## Answer`，状态 `needs-triage` → `ready-for-agent`。

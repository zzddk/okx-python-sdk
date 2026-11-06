# 05 · sdist 清理与改名后的文档残留

Type: task
Status: needs-triage
Blocked by: —

## Question

清掉打包产物里跑不起来的集成测试，以及 0.17.0 改名后残留的文档 / 配置小问题。机械清理，合并成一单。

## 证据

- `MANIFEST.in` 只有 3 行（`requirements.txt` / `README.md` / `okxsdk/py.typed`）。setuptools 默认把 `test/test*.py` 收进 sdist：实测 `dist/*.tar.gz` 含 19 个顶层集成测试文件（1630 行），却不含 `test/config.py` 与 `test/conftest.py`，从 sdist 里 `from test.config import ...` 会失败，跑不起来。
- wheel 是干净的：顶层只有 `okxsdk` 与 `okx_python_sdk-0.17.0.dist-info`，含 `licenses/LICENSE` 与 `py.typed`。
- `CHANGELOG.md:3`：「All notable changes to `python-okx` are documented in this file.」——改名前的项目名。第 9 行起与 Migration 表里出现 `okx` 是历史记录，按 ADR-0019 不回写。
- `docs/agents/domain.md:16-23`：示例目录树仍写 `okx/`；ADR 示例名 `0001-event-sourced-orders.md` / `0002-postgres-for-write-model.md` 是模板占位，与仓库实际的 19 份 ADR 不符。
- `.gitignore` 末尾 `.env.*.local` 后无换行，与后续内容粘连。
- `test/test_*.py` 的 2×F401 + 2×E402 与 `setup.py` 的 E402 归 01 清理，本单不重复处理。
- `example/*.ipynb` 与 README 的 `okxsdk` 导入已全部对齐，无残留（已核实，不需改）。
- `GLOSSARY.md` 不存在是 `domain.md:12` 明确的「proceed silently」约定，不新建。

## 建议方案

1. `MANIFEST.in` 加 `prune test`（或 `recursive-exclude test *`），重建 sdist 核对。
2. `CHANGELOG.md:3` 的标题行改成 `okx-python-sdk`。
3. `docs/agents/domain.md` 的示例目录树 `okx/` → `okxsdk/`；两个示例 ADR 名换成仓库真实存在的（如 `0001-release-strategy.md`、`0002-errors-raise-by-default.md`），或明写「示意」避免误导。
4. `.gitignore` 补末尾换行。

## 验收标准

1. `tar tzf dist/*.tar.gz | grep '/test/'` 为空；wheel 仍含 LICENSE 与 `py.typed`；`twine check` 通过。
2. `grep -n 'python-okx' CHANGELOG.md` 只剩 Migration / 历史段里的合理引用。
3. `domain.md` 示例树与真实包名一致。
4. `git status` 除本 effort / 两张 ADR 外无其他改动。
5. 不写 ADR：不涉公共契约。

## Answer

**施工完成（2026-11-06，未提交）。**

- `MANIFEST.in` 加 `prune test`；重建 sdist 后 `tar tzf dist/*.tar.gz | grep '/test/'` 为空（原 19 个顶层集成测试文件不再随 sdist 发布）。
- `CHANGELOG.md:3` 标题行 `python-okx` → `okx-python-sdk`；第 9 / 14 / 26 / 529 行的 `python-okx` 是 Migration 与历史叙述，按 ADR-0019 保留。
- `docs/agents/domain.md` 示例目录树 `okx/` → `okxsdk/`，两个占位 ADR 名换成真实存在的 `0001-release-strategy.md` / `0002-errors-raise-by-default.md`。
- `.gitignore` 补末尾换行。
- 验收：`python -m build --no-isolation` + `twine check` 均 PASSED；wheel 仍含 `licenses/LICENSE` 与 `okxsdk/py.typed`；构建产物已清理。
- 构建仍报 `License classifiers are deprecated`：那是工单 04（SPDX 表达式）的范围，本单不动。
- 状态暂留 `needs-triage`：代码已施工但未提交，提交后再转 `resolved` 并补 `Done in:`。

## Comments

- 2026-11-06 审查提出：P2 机械清理。
- 2026-11-06 用户确认机械项，直接施工；未提交。

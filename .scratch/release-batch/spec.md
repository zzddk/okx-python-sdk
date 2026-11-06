# 发版批次清单（下一个破坏性 minor）

来源：`/ub-mode` 会话 2026-11-07 的「核对发版检查清单」。核对对象散落在 handoff 的「发版批次」节、5 个 ADR、CHANGELOG 惯例与 CI build job，仓库没有单一的发版清单文件，故落盘本表统一收口。

**状态：刻意推迟，现在不执行任何一项。** 版本仍是 `0.18.0`，CHANGELOG 无 `## [Unreleased]` 段，`v0.18.0` tag 已在远端。以下变更按 handoff 约定攒入下一个以「WS 凭据契约」为主题的破坏性 minor，届时统一写 CHANGELOG；在此之前别动版本号、CHANGELOG、README 与 tag。见 `handoff-2026-11-07-okxsdk-architecture-review.md` 的「待办 / 悬空项」。

核对快照：2026-11-07，HEAD `02beb88`（`master == origin/master`）。

## 判断

- **批次规则**：ADR-0004「破坏性改动集中成批，每批对应一个以它为主题的 minor，能写在同一段迁移说明里就算一批」。本批主题定为「WS 凭据契约」，把 01 的运行时行为变更与 04 的日志行为变更一起写进同一次发版。
- **不发 PyPI**：ADR-0023 已把分发路径改成 GitHub 源码安装，发版 = 版本号 + CHANGELOG + annotated tag + 推送，没有构建上传、API token、publish job 这些步骤。ADR-0001 的「缺陷补丁先行」前提随之失效，版本只体现在 git tag 与 CHANGELOG。
- **本表只记录状态与发版时待办，不生成 `issues/NN-*.md` 施工工单**：5 项全是推迟项，做成带 `Status:` 的 implementation ticket 会制造「待施工」的假进度，且与 ADR-0024「评审卡片与候选是方向性假设、落地前必须独立复核」冲突。发版批次真正启动、用户拍板后才按 `docs/agents/issue-tracker.md` 拆单。

## 已就绪（现在就满足，发版不改变这些，但发版时须复跑）

| 项 | 依据 | 2026-11-07 实测 |
|---|---|---|
| 测试回路 | CI `test` job（3.9 / 3.12） | `pytest test/unit` → 865 passed, 336 subtests |
| lint 回路 | CI `lint` job | `ruff check okxsdk/ test/unit/` 全绿 |
| 打包四处一致 | ADR-0021 | `setup.py` `python_requires>=3.9`、classifiers 3.9–3.12、`ruff.toml` `target-version = "py39"`、CI 矩阵 3.9+3.12 对齐 |
| 许可元数据 | ADR-0021 | `license="MIT"` SPDX 表达式，无弃用 classifier；LICENSE 随 wheel 分发 |
| source-only 分发 | ADR-0023 | 无 `twine`、无 PyPI/upload job；README / CHANGELOG 均为源码安装；`dev_requirements.txt` 无发布工具 |
| 构建冒烟 | CI `build` job | `python -m build --no-isolation` rc=0、无弃用告警；wheel 含 `LICENSE` + `py.typed`、不含 `test/`；sdist `prune test` 生效；METADATA `Requires-Python >=3.9` / `Version: 0.18.0` |
| 干净安装 + import | CI `build` job | venv 从 wheel 安装成功，`import okxsdk` 通过，版本 0.18.0 |
| 在途工作隔离 | handoff | `.scratch/bug-hunt-2026-11-06/` 与 handoff 文档未跟踪、未误提交 |

上述构建/安装实测都在 `/tmp` 副本里跑，主仓零改动；数字是快照，发版时须重跑，不要直接引用。

## 发版时待办（5 项，届时统一执行）

1. **版本号 + tag**：`okxsdk/__init__.py:7` 的 `__version__` 从 `0.18.0` 升到下一个破坏性 minor；打 annotated tag 并推送。属共享状态操作，推送前单独确认（ADR-0004、handoff）。
2. **01 的 `### Migration`**：无凭据 `Transport` 构造的私有会话，`start()` / `subscribe()` 从抛 `LoginRejected` 变为抛缺凭据 `ValueError`、且不发出任何登录帧。这是运行时行为变更，须在迁移说明里逐行写清（`.scratch/no-credential-ws/spec.md:58`、ADR-0004）。用 GLOSSARY 的「凭据缺席」表述。
3. **04 的 `### Fixed`**：`send:` debug 日志脱敏导致日志内容变化，按 ADR-0020:16 记一条 `### Fixed`（`.scratch/credential-mask-owner/spec.md:62`）。
4. **CHANGELOG 汇总**：新建 `## [Unreleased]` 段，统一写第 2/3 项；`.scratch/credential-mask-owner/spec.md:42` 明确「Fixed 条目攒到发版时由主线程统一写进 `## [Unreleased]`」。
5. **README:175 口径（本次核对新发现，handoff 待办未列）**：该段只写了「有凭据但登录被拒 → `ConnectionError` / `LoginRejected`」，没有覆盖候选 01 新增的「凭据缺席 → `start()` / `subscribe()` 抛缺凭据 `ValueError`、不发登录帧」。这是公开行为变化，应随第 2 项的 Migration 一并补进 README。

## 非目标

- 现在不发版、不动版本号、不动 CHANGELOG、不打 tag、不改 README:175（handoff：发版批次刻意推迟）。
- 不重新建议 05 / 06 / 07（ADR-0024 已判定不做、维持现状）。
- 不回写历史 ADR：`docs/adr/0019` 的 `pip install okx-python-sdk`、ADR-0021:17 的 `twine check` 均为被 ADR-0023 取代的历史快照；`.scratch/review-2026-11-r4/*` 里的 `twine` 同属快照，按约定 3 不回写。
- 不回写已入库的评审报告 HTML。
- 不新增 ADR：本表只记录状态，没有新的公共契约决策；批次规则已由 ADR-0004 / 0020 / 0023 覆盖。

## 验证（发版批次启动时逐条打勾）

1. 第 1–5 项全部落地，`CHANGELOG` 的 `## [Unreleased]` 含 `### Migration`（01）与 `### Fixed`（04），迁移说明里列全公开行为变化。
2. README 的 WS 段同时覆盖「凭据缺席」「登录被拒」两条路径，且与 `start()` 实际行为一致。
3. `pytest test/unit` 全绿、`ruff check okxsdk/ test/unit/` 全绿；`python -m build --no-isolation` 无告警、从 wheel 干净安装可 import（本表「已就绪」四项复跑）。
4. `__version__`、CHANGELOG 版本段、tag 三者一致；tag 已推送且 `master` 与 `origin/master` 同步。
5. 破坏性改动共享同一段迁移说明（ADR-0004 裁量标准），没有把无关特性或补丁混进本批。

## 风险

- **快照过期**：本表核对于 2026-11-07，10 个提交刚推送。若期间有新改动，版本号、测试数、打包四处一致性都要重跑，不要照抄本表数字。
- **批次主题要守住**：01 是「凭据缺席」契约变更，04 是日志脱敏，二者靠「WS 凭据契约」这个主题同批；若发版时又想塞入其它破坏性改动，先按 ADR-0004 判断是否共享同一迁移故事。
- **README 与 CHANGELOG 是两处、别只写一处**：第 2 项要同时落到 CHANGELOG 的 Migration 和 README 的行为描述，漏任一处都会让文档与实际行为不一致。
- **共享状态**：tag 推送与版本号改动影响远端，按 handoff 约定发版前单独确认。

## 权威来源（指针，不复制内容）

- `handoff-2026-11-07-okxsdk-architecture-review.md`「待办 / 悬空项 → 发版批次（已刻意推迟）」
- `docs/adr/0001-release-strategy.md`、`0004-breaking-change-batches.md`、`0020-debug-logging-boundary.md`（:16）、`0021-packaging-metadata-truthfulness.md`、`0023-source-only-distribution.md`
- `.scratch/no-credential-ws/spec.md`（:38、:58）、`.scratch/credential-mask-owner/spec.md`（:42、:62）
- `CHANGELOG.md`、`okxsdk/__init__.py`、`setup.py`、`MANIFEST.in`、`ruff.toml`、`.github/workflows/ci.yml`、`dev_requirements.txt`
- `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/adr/0024-review-cards-are-hypotheses.md`

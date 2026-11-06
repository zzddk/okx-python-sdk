# 发版清单（下一个 minor）

来源：`/ub-mode` 会话 2026-11-07 的「核对发版检查清单」，落盘于 7f6b6a4；2026-11-07 复核后收敛修订（见文末「修订记录」）。核对对象散落在 handoff 的「发版批次」节、5 个 ADR、CHANGELOG 惯例与 CI build job，仓库没有单一的发版清单文件，故落盘本表统一收口。

**状态：刻意推迟，现在不执行任何一项。** 版本仍是 `0.18.0`，CHANGELOG 无 `## [Unreleased]` 段，`v0.18.0` tag 已在远端。handoff 明确「现在别动版本号」，变更攒到下一次发版统一写 CHANGELOG。见 `handoff-2026-11-07-okxsdk-architecture-review.md` 的「待办 / 悬空项」。

核对快照：2026-11-07。本文档随仓库演进，具体 HEAD 与提交数请以 `git log` 为准，勿照抄本表数字。

## 判断

- **handoff 只授权 2 项变更条目**：01 的运行时行为变更（需 `### Migration`）与 04 的日志行为变更（需 `### Fixed`）。其余都是发版流程动作或待拍板建议，不与这 2 项并列计数（详见「发版时待办」的分组）。
- **批次定性要分清**：01 是破坏性改动，按 ADR-0004 攒入以「WS 凭据契约」为主题的破坏性 minor、写进 `### Migration`；**04 不是破坏性改动**——`credential-mask-owner/spec.md:38` 明确「不进 ADR-0004 破坏性批次」，ADR-0004 的裁量标准是「能否写进同一段迁移说明」，而 04 是 `### Fixed`、不进 Migration，与「WS 凭据契约」主题无关。二者只是**搭同一次发版的便车**，不是「同一个破坏性批次」「同批」。handoff 原文只说「攒入下一个…minor，届时统一写 CHANGELOG」，没说同批。
- **不发 PyPI**：ADR-0023 已把分发路径改成 GitHub 源码安装，发版 = 版本号 + CHANGELOG + annotated tag + 推送，没有构建上传、API token、publish job 这些步骤。ADR-0001 的「缺陷补丁先行」前提随之失效，版本只体现在 git tag 与 CHANGELOG。
- **本表只记录状态与发版时待办，不生成 `issues/NN-*.md` 施工工单**：待办全是推迟项，做成带 `Status:` 的 implementation ticket 会制造「待施工」的假进度，且与 ADR-0024「评审卡片与候选是方向性假设、落地前必须独立复核」冲突。发版批次真正启动、用户拍板后才按 `docs/agents/issue-tracker.md` 拆单。

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

上述构建/安装实测都在 `/tmp` 副本里跑，主仓零改动；数字是快照，发版时须重跑。

## 发版时待办

### A. 核心变更条目（handoff 授权的 2 项，写进 CHANGELOG）

1. **01 的 `### Migration`**：无凭据 `Transport` 构造的私有会话，`start()` / `subscribe()` 在**凭据缺席**场景下从抛 `LoginRejected`（会发出以 `'-1'` 为密钥的登录帧）变为抛缺凭据 `ValueError`、且不发出任何登录帧。用 GLOSSARY 的「凭据缺席」表述，在迁移说明里逐行写清（`.scratch/no-credential-ws/spec.md:58`、ADR-0004）。
   - 边界：`LoginRejected` 并未消失——「有凭据但登录被拒」路径 01 前后都抛 `LoginRejected`（`PermanentConnectionError` → `ConnectionError` 子类），迁移说明不得写成「LoginRejected 一律改 ValueError」。
2. **04 的 `### Fixed`**：`send:` debug 日志脱敏导致日志内容变化，按 ADR-0020:16 记一条 `### Fixed`（`.scratch/credential-mask-owner/spec.md:62`）。
   - ⚠️ **别与 0.18.0 已有的 debug 脱敏 `### Fixed` 重复**：`CHANGELOG.md:27` 那条覆盖 REST 头与 WS login 帧；04 这次是公开的 `send()` 可携带手搓登录帧 / 敏感 args 的 `send:` 路径、以及掩码统一到 `mask_sensitive()`。措辞要写清新范围。
   - 04 spec:42 明确「Fixed 条目攒到发版时由主线程统一写进 `## [Unreleased]`」。

### B. 发版流程动作（固有步骤，不是「变更条目」）

3. **版本号 + tag**：`okxsdk/__init__.py:7` 的 `__version__` 从 `0.18.0` 升到下一个 minor；打 annotated tag 并推送。属共享状态操作，推送前单独确认（ADR-0023、handoff）。
4. **CHANGELOG 的写入位置**：新建 `## [Unreleased]` 段容纳 A 组 2 项，发版时把该段改名为版本号段。这是仓库既有惯例——r4 落地（a464c12）就有 `## [Unreleased]`，0.18.0 发版（67fa8cd）直接改名为 `## [0.18.0]`。此项是 A 组的组织方式，不单算一个变更。

### C. 可选、待拍板（非 handoff 授权，不构成既定待办）

5. **README 补「凭据缺席」路径**：`README.md:175` 只写了「有凭据但登录被拒 → `ConnectionError` / `LoginRejected`」，没有描述候选 01 新增的「凭据缺席 → `start()` / `subscribe()` 抛缺凭据 `ValueError`、不发登录帧」。
   - **复核修正定性**：README:175 **没有被 01 改错**——可执行回路证明「有凭据被拒」路径 01 前后都抛 `LoginRejected`、`LoginRejected` 是 `ConnectionError` 子类；01 新增的是另一条路径。这是「新增行为未文档化」的可选增强，不是「口径错误」。
   - handoff 待办未列、01/03/04 三份 spec 均未把 README 列为验收项、ADR-0004 只要求迁移说明、01 spec 验收标准只有「pytest 全绿 + 既有用例不改」。
   - **按约定 1 / ADR-0024，这是未经独立复核与拍板的假设，发版时先决定是否要做**；若做，README 与 CHANGELOG 两处都要顾到，别只写一处。

## 非目标

- 现在不发版、不动版本号、不动 CHANGELOG、不打 tag、不改 README:175（handoff：发版批次刻意推迟）。
- 不重新建议 05 / 06 / 07（ADR-0024 已判定不做、维持现状）。
- 不回写历史 ADR：`docs/adr/0019` 的 `pip install okx-python-sdk`、ADR-0021:17 的 `twine check` 均为被 ADR-0023 取代的历史快照；`.scratch/review-2026-11-r4/*` 里的 `twine` 同属快照，按约定 3 不回写。
- 不回写已入库的评审报告 HTML。
- 不新增 ADR：本表只记录状态，没有新的公共契约决策；批次规则已由 ADR-0004 / 0020 / 0023 覆盖。

## 验证（发版批次启动时逐条打勾）

1. A 组 2 项落地：`### Migration`（01）逐行写清「凭据缺席」行为变化且不抹掉「有凭据被拒仍抛 LoginRejected」；`### Fixed`（04）写清 `send:` 新路径、不与 0.18.0 已有条目重复。
2. 若 C 组第 5 项拍板要做，README 的 WS 段同时覆盖「凭据缺席」与「登录被拒」两条路径，且与 `start()` 实际行为一致；CHANGELOG 与 README 两处都顾到。
3. `pytest test/unit` 全绿、`ruff check okxsdk/ test/unit/` 全绿；`python -m build --no-isolation` 无告警、从 wheel 干净安装可 import（本表「已就绪」四项复跑）。
4. `__version__`、CHANGELOG 版本段、tag 三者一致；tag 已推送且 `master` 与 `origin/master` 同步。
5. 破坏性改动按 ADR-0004「能写在同一段迁移说明里」裁量：本批的破坏性改动只有 01；04 是非破坏性 `### Fixed`、搭便车，不进 Migration、不算同批，别把无关破坏性改动塞进这次发版。

## 风险

- **快照过期**：本表核对于 2026-11-07。若期间有新改动，版本号、测试数、打包四处一致性都要重跑，不要照抄本表数字。
- **别再膨胀清单**：handoff 授权的变更条目只有 A 组 2 项。B 组是发版流程、C 组是待拍板建议，不要把它们升格成「第 N 项待办」；任何新发现按约定 1 先独立复核、再拍板。
- **批次主题只约束 01**：「WS 凭据契约」是 01 的迁移主题，04 与该主题无关、只是搭同一次发版。若发版时又想塞入其它破坏性改动，按 ADR-0004 判断是否共享同一迁移故事。
- **共享状态**：tag 推送与版本号改动影响远端，按 handoff 约定发版前单独确认。

## 权威来源（指针，不复制内容）

- `handoff-2026-11-07-okxsdk-architecture-review.md`「待办 / 悬空项 → 发版批次（已刻意推迟）」
- `docs/adr/0001-release-strategy.md`、`0004-breaking-change-batches.md`、`0020-debug-logging-boundary.md`（:16）、`0021-packaging-metadata-truthfulness.md`、`0023-source-only-distribution.md`
- `.scratch/no-credential-ws/spec.md`（:38、:58）、`.scratch/credential-mask-owner/spec.md`（:38、:42、:62）
- `CHANGELOG.md`、`okxsdk/__init__.py`、`setup.py`、`MANIFEST.in`、`ruff.toml`、`.github/workflows/ci.yml`、`dev_requirements.txt`
- `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/adr/0024-review-cards-are-hypotheses.md`

## 修订记录

- 2026-11-07 收敛修订（承接同日复核）：原稿把 handoff 的 2 项授权膨胀成 5 项并列待办，且把 04 归进「WS 凭据契约」破坏性批次、把 README:175 定性为「口径缺口」。本次按证据改：待办分 A（核心变更，2 项）/ B（发版流程）/ C（可选待拍板）三组；04 明确为非破坏性 `### Fixed`、搭便车；README 项降级为可选并附回路证据（「有凭据被拒」路径 01 前后一致，README 未被改错）；01 项补上「LoginRejected 未消失」边界；04 项补上「别与 0.18.0 已有 Fixed 重复」提醒；去掉会立刻失真的 HEAD / 提交计数。修订不改状态：发版仍刻意推迟。

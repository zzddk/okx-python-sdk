# 地图：2026-11-06 全项目审查（review-2026-11-r4）

> **状态（2026-11-06）**：01 / 02 / 04 已逐条拍板（均取 A），由 3 个并行子代理施工、主线程集成验证通过；`docs/adr/0020`、`0021` 已定稿生效；03 / 05 已施工并验证。**五张工单全部已施工、未提交** —— 01 / 02 / 04 停在 `ready-for-agent`，03 / 05 暂留 `needs-triage`；提交后统一转 `resolved` 并补 `Done in:`。
> **补记（同日后段）**：发现一处本轮遗漏的 P0，由并发 effort `.scratch/bug-hunt-2026-11-06/` 修复（0.17.0 把网络主机名一并改名）。用户拍板补 `docs/adr/0022` 并把修复 + 回归测试提交于 `7bbfa98`（只 commit，未 push、未发版）；详见 `spec.md` 第 7 节。

Labels: wayfinder:map

## Destination

把第四批（ub-mode）全项目审查的 5 组发现推到可施工：先修「一条测试从未运行」及其门禁根因，再定 debug 语义与打包元数据两张公共契约，最后收机械清理。地图内不改代码、不发版、不 push。

## Notes

- 评审来源：`/ub-mode 审查整个项目`（本会话），无 HTML 评审文档；证据全部来自本轮实测，明细见 `.scratch/review-2026-11-r4/spec.md` 第 1 节。
- 基线（审查当时）：`pytest` 846 passed / 322 subtests、覆盖率 98%；`ruff check okxsdk/` 通过、`ruff check .` 8 errors；`build` + `twine check` 均 PASSED；sdist 夹带 19 个顶层集成测试；HEAD `c6d3ed0`，工作区 clean。
- **当前基线（全部施工后）**：`pytest` **856 passed / 336 subtests**；`ruff check okxsdk/ test/unit/` 零错误；普通跑法无 warnings summary（12 条 httpx 告警清零）；`-W error::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning` 全仓 856 passed；`python -m build --no-isolation` 无 license 弃用告警、`twine check` PASSED、sdist 无 `test/`、wheel 含 LICENSE 与 `py.typed`。
- **并行切分**（ub-mode: Separate Before Serializing Shared State）：三个子代理文件级互斥 —— A 只碰 `test/` 与 `ci.yml`；B 只碰 `utils.py` / `WsBaseAsync.py` / `test_logging.py`；C 只碰 `setup.py` / `ruff.toml`。`setup.py` 的 E402 归 C 一并修（避免 A/C 写同一文件），`CHANGELOG.md` 与 `ruff.toml` 注释由主线程统一写。每个代理只跑窄测试，全量集成验证由主线程统一做。
- 候选编号 01–05 与 r2 / r3 / 更早三批重名；引用必须带 effort 名。
- 语言：中文；工单沿用 `.scratch/<effort>/issues/NN-*.md`，Comments 追加在文件末尾。
- 工单 `Status:` 用 `docs/agents/triage-labels.md` 的取值：`needs-triage` → 拍板后 `ready-for-agent`；**代码施工完成且已提交才转 `resolved` 并补 `Done in:`**。`Type:` 用 `grilling` / `task`。
- 凡改动公共契约的决策补 `docs/adr/`（当前最大 0022）。r4 的 0020（debug 边界）与 0021（打包元数据）已定稿生效；另立的 0022（网络主机名不是包名）已随 `7bbfa98` 提交，不属 r4。
- 规格、候选取舍与验收在 `spec.md`；本文件只做导航。
- 构建 / lint / coverage 产物已清理。
- **并发 effort**：`.scratch/bug-hunt-2026-11-06/` 同时修了 0.17.0 主机名盲改（`okx` → `okxsdk` 把 `*.okx.com` 也换成 `*.okxsdk.com`），并新增 `test/unit/okxsdk/test_network_hosts.py`（5 用例）。该 P0 归 bug-hunt effort，本图不重复开单；修复已随 ADR-0022 提交于 `7bbfa98`（只 commit，未 push）。详见 `spec.md` 第 7 节。
- 审查盲区：本轮核对了控制流、测试、打包、CI、文档，但没核对 `consts/http.py` / `consts/websocket.py` 常量的**值**，故漏掉该 P0。

## Decisions so far

- [01 · 被遮蔽的登录测试与 lint 门禁范围](issues/01-shadowed-login-test.md)：**拍板 A，已施工未提交**——CI 并列 `ruff check test/unit/`、AST 重名守卫、类改名恢复契约用例、清 F401/E402；门禁不扩到 notebook 与顶层集成测试。不选 B / C。
- [02 · debug 语义](issues/02-debug-semantics.md)：**拍板 A，已施工未提交**——保留字段名、值打掩码 `***`；删 `logger.setLevel` 改回实例级；补 2 条契约测试。ADR-0020 按 A 定稿生效。
- [04 · Python 支持面对齐](issues/04-python-support-matrix.md)：**拍板 A，已施工未提交**——收窄到 `>=3.9`、删 3.7/3.8 classifiers、`ruff py39`、CI 矩阵不动、SPDX `license="MIT"`。ADR-0021 按 A 定稿生效。下限提高是否进 minor 批次按 ADR-0004 另判。
- [03 · POST 改用 content=](issues/03-httpx-content.md)：机械项，**已施工未提交**——`data=body` → `content=body`，新增 `warnings.catch_warnings` 契约测试（改动前红、改动后绿）；12 条 httpx 告警清零。
- [05 · sdist 清理与文档残留](issues/05-sdist-and-doc-residue.md)：机械项，**已施工未提交**——`MANIFEST.in` 加 `prune test`、CHANGELOG 标题行、domain.md 示例树、`.gitignore` 换行；sdist 不再夹带 `test/`。

## Not yet specified

（无——五张工单全部已施工。剩下的都是决策而非规格：提交、转 `resolved`、0.17.1 发版、下限提高是否进 minor 批次。）

## Out of scope

（见 `spec.md` 第 6 节：端点返回类型建模、整仓格式化与显式导入、PyPI 上传、任何 push / 发版。）

- 0.17.0 主机名盲改的修复与回归：归 `.scratch/bug-hunt-2026-11-06/`，见 `spec.md` 第 7 节。
- 全仓裸 `-W error::DeprecationWarning`：被 pytest-asyncio 的 `asyncio_default_fixture_loop_scope` 告警挡住（与被测代码无关），按 03 预留口径豁免，未改 `pytest.ini`。
- `ruff check .` 剩余 9 条：2 条 notebook 单元重导入 F811 误报、7 条未跟踪探针脚本 `.scratch/bug-hunt-2026-11-06/hunt.py` 的 E402；均不在门禁内。

## 工单索引

- [01 · 被遮蔽的登录测试与 lint 门禁范围](issues/01-shadowed-login-test.md) — ready-for-agent（P0，拍板 A；已施工 / 待提交）
- [02 · debug 语义：日志脱敏与实例级开关](issues/02-debug-semantics.md) — ready-for-agent（P1，拍板 A；已施工 / 待提交；ADR-0020 已生效）
- [03 · POST 改用 content=](issues/03-httpx-content.md) — needs-triage（P1，已施工 / 待提交）
- [04 · 声明的 Python 支持面与 CI 对齐](issues/04-python-support-matrix.md) — ready-for-agent（P2，拍板 A；已施工 / 待提交；ADR-0021 已生效）
- [05 · sdist 清理与改名后的文档残留](issues/05-sdist-and-doc-residue.md) — needs-triage（P2，已施工 / 待提交）

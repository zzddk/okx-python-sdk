# 2026-11-06 全项目审查（ub-mode / review-2026-11-r4）spec

> 状态：01 / 02 / 04 已逐条拍板（均取 A），由 3 个并行子代理施工、主线程集成验证通过；`docs/adr/0020`、`docs/adr/0021` 已定稿生效；03 / 05 已施工并验证。**五张工单全部已施工、未提交** —— 01 / 02 / 04 停在 `ready-for-agent`，03 / 05 暂留 `needs-triage`（无 commit hash，提交后统一转 `resolved` 并补 `Done in:`）。
> 性质：只读审查的交接物；本 effort 不改代码、不发版、不 push。
> 补记（同日后段）：审查结束后发现一处**本轮遗漏的 P0**，由并发 effort `.scratch/bug-hunt-2026-11-06/` 修好，见第 7 节。用户随后拍板补 `docs/adr/0022` 并把修复 + 回归测试提交于 `7bbfa98`（只 commit，未 push、未发版）。
> 范围：`okxsdk/` 的 REST 与 WebSocket 层、`test/` 测试、打包元数据、CI 门禁、仓库文档。
> 判据优先级：ADR 与工单 Answer > 评审证据 > README/CHANGELOG 的叙述（沿用 r3）。
> 引用编号必须带 effort 名（`review-2026-11-r4/NN`）；01–05 与前三批编号重名。
> 导航见 `.scratch/review-2026-11-r4/map.md`；本文件是规格与验收。

## 1. 结论

就本轮实际读到的代码而言，REST/WS 分层、单一决策点、幂等重连、限流分区不变量、19 份 ADR 都到位；发现的 5 组问题集中在**门禁覆盖范围**与**可观测性**。**但这个结论不完整**：同日后段由并发 effort 查出 0.17.0 把网络主机名一并改名、导致所有 REST/WS 请求打到 `*.okxsdk.com` 的 P0（第 7 节）。本轮没有核对 `consts/http.py` / `consts/websocket.py` 的常量取值，是明确盲区。

基线（2026-11-06 实测）：

- `pytest`（`testpaths=test/unit`）：**846 passed / 322 subtests**，覆盖率 98%（1972 语句，漏 39）。
- `ruff check okxsdk/`（CI 门禁，`.github/workflows/ci.yml:80`）：通过；`ruff check .`：**8 errors**，全部在门禁之外。
- `python -m build --no-isolation` + `twine check`：sdist / wheel 均 PASSED；wheel 顶层只有 `okxsdk` 与 dist-info，含 `licenses/LICENSE`、`py.typed`。
- sdist 夹带 19 个顶层集成测试文件（1630 行），不含 `test/config.py` / `conftest.py`。
- 工单 65 resolved + 1 wontfix（`.scratch/ws-hardening/issues/04-ws-proxy.md`）；ADR 19 份，下一张 0020。
- HEAD `c6d3ed0`，审查当时工作区 clean；`master` 与 `origin/master` 同步。

> 以上数字是审查当时的快照。同日后段并发改动落入后变为 **851 passed / 336 subtests**、`ruff check .` 15 errors（新增 7 条来自 `.scratch/bug-hunt-2026-11-06/*.py` 脚本，均不在 CI 门禁内）。详见第 7 节。

## 2. 发现 → 工单 / ADR 归属

| 优先级 | 发现 | 关键证据 | 工单 | ADR |
|---|---|---|---|---|
| P0 | 重复类名遮蔽一条登录契约测试，门禁看不见 | `test/unit/okxsdk/websocket/test_ws_private_async.py:71` 与 `:270`；`ci.yml:80` | 01 | — |
| P1 | `debug=True` 把 passphrase / 签名写进日志；单个实例改写全局 logger 级别 | `utils.py:36,44`、`WsBaseAsync.py:296`、`WsBaseAsync.py:134` | 02 | 0020（已生效） |
| P1 | POST 用已弃用的 httpx `data=` 传 JSON 字符串 | `transport.py:161`；12 条 `DeprecationWarning` | 03 | — |
| P2 | 声明的 Python 支持面与 CI 不一致；许可 classifier 已弃用 | `setup.py:48,57`、`ci.yml:93`、`ruff.toml:3` | 04 | 0021（已生效） |
| P2 | sdist 夹带跑不起来的集成测试；改名后文档残留 | `MANIFEST.in`、`CHANGELOG.md:3`、`domain.md:22` | 05 | — |

## 3. 已拍板的取舍（2026-11-06）

用户逐条拍板：**01 → A、02 → A、04 → A；ADR-0020 / 0021 两张都定稿生效**。B / C 保留在下面作为当时考虑过但未采纳的记录。三张工单的 `## Answer` 段落了结论与施工记录，状态由 `needs-triage` 转 `ready-for-agent`（代码已施工但**未提交**，故不标 `resolved`、不写 `Done in:`；提交后统一转）。

**01 · 门禁范围 → A**

- **A（拍板采纳）**：CI 加 `ruff check test/unit/`（实测该范围仅 1 条错误，即本条 F811），再加一条 AST 重名守卫。门禁噪音为零，且能同时挡住类 / 方法重名。
- **B**：`ruff check .` 全仓 + per-file-ignore 排除 notebook 与顶层集成测试。覆盖更广，但要维护排除清单，并把 1630 行未维护的集成测试拉进视野。
- **C**：不扩 CI，只加「关键测试都在收集列表」的白名单断言。最轻，但只覆盖白名单里的名字。

**02 · debug 脱敏形状 → A**（ADR-0020 按 A 定稿）

- **A（拍板采纳）**：保留字段名、值打掩码（如 `OK_ACCESS_PASSPHRASE=***`）。可排障又不泄密，日志形状变化最小。
- **B**：debug 行只打事件名，完全不打值。最安全，排障信息最少。
- **C**：删掉这几行 debug。最省事，但 `debug=True` 几乎失去意义。
- 「删掉 `logger.setLevel`」只有一种合理做法，不设候选，随 A 一并执行。

**04 · Python 最低版本 → A**（ADR-0021 按 A 定稿）

- **A（拍板采纳）**：收窄到 `>=3.9`，删 3.7/3.8 classifiers，`target-version = "py39"`，CI 矩阵不变。声明与验证一致，改动最小。
- **B**：保持 `>=3.7` 与 `py37`，CI 补 3.7/3.8 作业。3.7 已 EOL，`actions/setup-python` 未必提供；`int | None` 的静态检查口径要额外处理。
- **C**：折中 `>=3.8` + `target-version = "py38"`，CI 加 3.8。多一个作业，覆盖一个仍有人用的版本。

## 4. 验收（全 effort）

1. `pytest` 在当前基线上 +1 passed，且 `test_login_goes_through_the_shared_payload_builder` 出现在 `--collect-only`。
2. `ruff check okxsdk/ test/unit/` 零错误；`pytest -W error::DeprecationWarning` 下 httpx 告警消失。
3. debug 日志中不含 passphrase / sign / API key；连建两个 debug 取值不同的实例后模块 logger level 不变。
4. `twine check dist/*` 通过，sdist 不含 `test/`，wheel 仍含 LICENSE 与 `py.typed`。
5. `python_requires`、classifiers、`ruff target-version`、CI 矩阵四者一致；`CHANGELOG.md:3` 与 `domain.md` 示例树无残留。
6. 构建 / lint 产物已清理，工作区无遗留的临时产物。
7. 验收基线已随并发 effort 变为 851 passed / 336 subtests；施工时以当时 `pytest` 实测为准，不拿 846 当固定值。
8. 集成验证结果（2026-11-06，全部施工后）：`pytest` **856 passed / 336 subtests**；`ruff check okxsdk/ test/unit/` 零错误；`-W error::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning` 全仓 856 passed；`python -m build --no-isolation` 无 license 弃用告警、`twine check` PASSED、sdist 无 `test/`、wheel 含 LICENSE 与 `py.typed`；端到端复核 debug 日志不含凭据、logger 级别不串。

## 5. 已核实不是问题（避免误报）

- README 与 `example/*.ipynb` 的导入已全部对齐 `okxsdk`，0.17.0 改名无残留。
- `GLOSSARY.md` 不存在是 `docs/agents/domain.md:12` 明确的「proceed silently」约定。
- `test/unit/okxsdk/rate_limit_acceptance.py` 与 `RATE_LIMITS` 的双份是刻意的冻结基线（Pin what the code does），不是重复。
- httpx 0.24.0 元数据为 `Requires-Python: >=3.7`，故「3.7 无法安装」是误判；只是 3.7/3.8 未被验证。
- `test/conftest.py` 按凭据缺失跳过顶层集成测试，设计如此，不是死代码。
- 本地初次构建因缺 `setuptools` 失败（CI 会装、打包单测用 stub 绕开），补装后通过，非项目缺陷。
- notebook 的 2 条 F811 是单元重导入的误报，不纳入门禁。
- REST/WS 的**控制流**逐条读过：签名逐尝试重建、outcome-unknown 不重试、登录单写者锁、`on_lost` 边界、订阅表纯数据、分页游标去重、限流器锁外 sleep——这些部分未发现缺陷。但**常量的值没有核对**：`consts/http.py` / `consts/websocket.py` 的主机名被 0.17.0 盲改污染，本轮漏检（第 7 节）。「未发现缺陷」只适用于控制流，不外推到数据。

## 6. 范围外

- 端点返回类型建模（`Dict[str, Any]` → 类型化响应）。
- 整仓格式化与把 19 个星号导入改成显式导入（r3 已列为独立机械批次）。
- 0.17.0 的 PyPI 上传（缺 API token，与改造无关）。
- 0.17.0 网络主机名盲改的修复与回归：归并发 effort `.scratch/bug-hunt-2026-11-06/`（第 7 节），本 effort 不重复开单。
- 任何 push / 发版：共享状态操作，需单独确认。

## 7. 审查盲区与并发发现（同日后段补记）

审查落盘后 `git status` 出现**非本会话产生**的并发改动，说明另一个 effort 同时在跑：

- `.scratch/bug-hunt-2026-11-06/`（`hunt.py` / `hunt_ws.py` / `min-repro.py`）。
- `M okxsdk/consts/http.py`：`API_URL` 由 `https://www.okxsdk.com` 改回 `https://www.okx.com`。
- `M okxsdk/consts/websocket.py`：6 个 WS 主机由 `*.okxsdk.com` / `wspap.okxsdk.com` 改回 `*.okx.com` / `wspap.okx.com`。
- `M test/test_ws_private_async.py`、`M test/test_ws_public_async.py`：URL 字面量跟随改回。
- 新增 `test/unit/okxsdk/test_network_hosts.py`：5 个用例钉住常量与调用点，并断言任何 URL 都不得含 `okxsdk`、host 必须是 `okx.com` 或其子域。

**根因**：0.17.0 的导入包改名（4daa4c6，ADR-0019）把 `okx` 全局替换成 `okxsdk`，连主机名字符串一起换了；当时的测试只断言 `startswith('wss://')` 与 `'wspap' in url`，因此全绿。**这比本轮 5 组发现都严重**：已发布的 0.17.0 所有 REST/WS 请求都打到不存在的域。

**本轮为什么漏掉**：审了控制流、测试、打包、CI、文档，却没有核对常量的**值**；`consts/http.py` / `consts/websocket.py` 没打开过。教训写给后续审查：改名类改动必须单独核对「字面量里哪些是标识符、哪些是外部事实（域名 / 路径 / header 名）」。

**处置（2026-11-06 用户拍板后更新）**：

- 用户拍板：**补一张「网络主机名不是包名」的 ADR，并把那份修复 + 回归测试提交**。已新增 `docs/adr/0022-network-hosts-are-not-the-package-name.md`（已生效，非提案），与 4 个修复文件、1 个回归测试一起提交于 `7bbfa98`；提交前实测 851 passed / 336 subtests、`ruff check okxsdk/` 通过。**只 commit，未 push、未打 tag、未发版**。
- 不在 r4 重复开单——同一决策不落两处；该 P0 归 `.scratch/bug-hunt-2026-11-06/`。0022 是独立 ADR；r4 的 0020 / 0021 已随本次逐条拍板定稿生效。
- 复核后 **01–05 五张工单仍全部成立**：F811 重名类仍在（`ruff check test/unit` 仍报 1 条）、被遮蔽用例仍未被收集、两处 F401 仍在；`data=` / debug 语义 / 打包元数据 / sdist 残留均未被动过。
- 0.17.0 是否发 0.17.1 修复版属发版决策，需单独确认（用户本轮未提）。

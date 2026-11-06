# 01 · 被遮蔽的登录测试与 lint 门禁范围

Type: grilling
Status: resolved
Done in: a464c12
Blocked by: —

## Question

`test/unit/okxsdk/websocket/test_ws_private_async.py:71` 与 `:270` 定义了两个同名类 `TestWsPrivateAsyncLogin`。Python 里后者覆盖前者，前者的唯一用例 `test_login_goes_through_the_shared_payload_builder`（验证登录走共享 `login_payload`）**从未被收集**。

要定下两件事：**(a) 怎么修这条死测试；(b) 门禁要扩到什么范围，才能让同类问题以后不可能静默发生。**

## 证据

- `pytest <file>::TestWsPrivateAsyncLogin::test_login_goes_through_the_shared_payload_builder -q` → `ERROR: not found ... (no match in any of [<UnitTestCase TestWsPrivateAsyncLogin>])`，`no tests ran`。
- `--collect-only` 只列出 `test_start_logs_in_before_anything_else`（第二个类的用例）。
- AST 扫描整个 `test/` 树：只有这一处重名类，类内无重名方法，故不是普遍模式，是孤立问题。
- 根因：`.github/workflows/ci.yml:80` 只跑 `ruff check okxsdk/`；`ruff.toml` 开头明写「test/ 不在门禁内」。F811 因此报不出来，pytest 对类重名也静默。
- `ruff check test/unit --output-format concise` → 恰好 1 条错误（就是这条 F811），是干净门禁。
- `ruff check .` → 8 errors：本条 F811 + `test/test_ws_private_async.py` / `test/test_ws_public_async.py` 2×F401 + `test/test_market.py` 2×E402 + `setup.py` 1×E402 + notebook 2×F811（单元重导入误报）。
- 现有 `test/unit/okxsdk/test_logging.py` 只测「记录能到达应用 handler」，不测收集完整性。
- `.scratch/` 与 handoff 里无相关工单（已 grep `F811` / `redefin` / `重名`）。

## 建议方案

1. 把 `:71` 的类改名（如 `TestWsPrivateAsyncLoginPayload`），恢复那条契约测试。
2. CI 加一步 `ruff check test/unit/`，与 `ruff check okxsdk/` 并列；**不**扩到 notebook 与顶层 `test/test_*.py`，避免把误报和未维护的集成测试塞进门。
3. 顺手清掉门禁外的 F401 / E402（两处未用的 `Transport` 导入、`test_market.py` 与 `setup.py` 的模块级导入位置），让新门禁一次绿。
4. 加一条防回归守卫：断言 `test/unit` 下无重复类名（AST），重名时点名文件。

### 候选（已拍板：A）

- **A（拍板采纳）**：`ruff check test/unit/` + 一条 AST 重名守卫。门禁噪音为零，且能同时挡住类 / 方法重名。
- **B**：`ruff check .` 全仓，配 per-file-ignore 排除 notebook 与顶层集成测试。覆盖更广，但要维护一份排除清单，且会把 1630 行未维护的集成测试拉进视野。
- **C**：不扩 CI，只在测试里加一条「关键测试都在收集列表」的白名单断言。最轻，但只覆盖白名单里的名字。

## 验收标准

1. `test_login_goes_through_the_shared_payload_builder` 出现在 `--collect-only` 且通过。
2. `ruff check okxsdk/ test/unit/` 零错误；`pytest` 在当前基线上 +1 passed。
3. 人为把类名改回重复值时，守卫失败并点名文件。
4. 不改运行时代码。

## Answer

**拍板（2026-11-06）：A。**

- CI 在 `ruff check okxsdk/` 之外并列加 `ruff check test/unit/`；门禁**不**扩到 notebook 与顶层 `test/test_*.py`（那两处 F811 是单元重导入误报）。
- 加一条 AST 守卫：断言 `test/unit` 下无重复类名，同时覆盖类内重复方法名，重名时点名文件。
- `:71` 的类改名（如 `TestWsPrivateAsyncLoginPayload`），恢复 `test_login_goes_through_the_shared_payload_builder`；顺手清掉 `test/test_ws_private_async.py` / `test/test_ws_public_async.py` 的 2×F401、`test/test_market.py` 的 2×E402、`setup.py` 的 1×E402，让新门禁一次绿。
- 不选 B：全仓 `ruff check .` 要维护排除清单，并把 1630 行未维护的集成测试拉进视野。不选 C：白名单只覆盖列出来的名字，挡不住新的重名。
- 施工前基线已随并发 effort 变为 851 passed / 336 subtests；验收按「当前基线 +1 passed」判定，不写死 846。
- 已提交于 `a464c12`，Status 转 `resolved`，`Done in:` 见文件头。

**施工（2026-11-06，并行子代理 A，已提交 `a464c12`）**：

- `test/unit/okxsdk/websocket/test_ws_private_async.py:71` 的类改名 `TestWsPrivateAsyncLoginPayload`，被遮蔽用例重新被 `--collect-only` 收集。
- 新增 `test/unit/okxsdk/test_no_duplicate_test_classes.py`：AST 守卫断言同文件无重名类、同类内无重名方法，失败时点名文件与名字；已用「改回重名 → 守卫红 → 改回」验证。
- `.github/workflows/ci.yml:80` 改为 `ruff check okxsdk/ test/unit/`；`test/test_market.py` 的 2×E402、`test/test_ws_private_async.py` / `test/test_ws_public_async.py` 的 2×F401 清零。`setup.py` 的 E402 归工单 04 的代理一并修，避免两个代理写同一文件。
- 集成验证：`pytest` 856 passed / 336 subtests；`ruff check okxsdk/ test/unit/` 零错误；`ruff check .` 只剩 2 条 notebook F811 误报与 7 条未跟踪探针脚本的 E402，均不在门禁内。

## Comments

- 2026-11-06 审查提出（`/ub-mode 审查整个项目`）：P0，本轮唯一正确性问题，也是其余 P2 lint 残留的根因。
- 2026-11-06 用户逐条拍板取 A；结论落在 `## Answer`，状态 `needs-triage` → `ready-for-agent` → `resolved`（`a464c12`）。

# 02 · debug 语义：日志脱敏与实例级开关

Type: grilling
Status: ready-for-agent
Blocked by: —

## Question

`debug=True` 现在做两件越界的事：把凭据写进日志、把模块级 logger 级别改成全局 DEBUG。要定下 **debug 的边界是什么**，以及脱敏的形状。本单改动 debug 的可观察行为，按惯例配 `docs/adr/0020-debug-logging-boundary.md`（已定稿生效）。

## 证据

- `okxsdk/utils.py:36,44` `logger.debug(f'header: {header}')` 打印完整 header，含 `OK_ACCESS_KEY`、`OK_ACCESS_SIGN`、`OK_ACCESS_PASSPHRASE`。
- `okxsdk/websocket/WsBaseAsync.py:296` `logger.debug("login: %s", payload)` 打印完整 login payload，含 `passphrase` 与 `sign`。
- `okxsdk/transport.py:155-157` 打印 domain / url / body（body 含订单参数，敏感性较低）。
- 实测（debug=True + 应用侧 handler）：
  ```
  passphrase in debug log: True
  signature header in debug log: True
  ```
- `okxsdk/websocket/WsBaseAsync.py:133-134` 在 `debug=True` 时执行模块级 `logger.setLevel(logging.DEBUG)`，影响所有 `WsBaseAsync` 实例且不会复原。实测：debug 实例后 level=10，再建 `debug=False` 实例仍是 10。
- `okxsdk/__init__.py:9-11` 已声明「records propagate to the application's handlers」+ NullHandler，本意是让应用侧控制级别；`setLevel` 与之矛盾。
- 全仓 ADR 与 `.scratch` 工单无一处覆盖 debug 日志内容或 logger 级别（`grep -rni` 无结果）。
- `test/unit/okxsdk/test_logging.py` 只有两条测试，未覆盖这两处。

## 建议方案

统一成一条边界：**debug 只描述事件、不描述秘密；debug 是实例状态，不是全局 logger 状态。**

1. `utils.get_header` / `get_header_no_sign` 的 debug 行对 `OK_ACCESS_*` 三个字段的值打掩码，`WsBaseAsync.login` 的 debug 行不打印 `args[0]` 的 `passphrase` / `sign`；字段名保留。
2. 删掉 `WsBaseAsync.__init__` 里的 `logger.setLevel(logging.DEBUG)`；各 debug 行本来就有 `if self.debug:` 守卫，去掉后仍按实例生效，级别交给应用侧 handler。
3. 补契约测试：debug 日志不含 passphrase / sign / API key；连续建 `debug=True` 与 `debug=False` 两个实例后，模块 logger level 不变。

### 候选（已拍板：A）

- **A（拍板采纳）**：保留字段、值打掩码（如 `OK_ACCESS_PASSPHRASE=***`）。可排障又不泄密，日志形状变化最小。
- **B**：debug 行只打事件名（如 `login request sent`），完全不打值。最安全，排障信息最少。
- **C**：删掉这几行 debug。最省事，但 `debug=True` 几乎失去意义。
- 「删掉 `setLevel`」只有一种合理做法，不设候选，随 A 一并执行。

## 验收标准

1. debug 日志中不出现 passphrase、`OK_ACCESS_SIGN` 的值、`OK_ACCESS_KEY` 的值（有断言）。
2. 建两个 debug 取值不同的实例后，`logging.getLogger('okxsdk.websocket.WsBaseAsync').level` 与建之前一致（有断言）。
3. `test_logging.py` 原有两条测试仍通过；`pytest` 全绿。
4. 不改公开 API 签名；CHANGELOG 记一条 Fixed（行为变更）。

## Answer

**拍板（2026-11-06）：A；ADR-0020 定稿生效。**

- 保留字段名、敏感值打掩码：`OK_ACCESS_KEY` / `OK_ACCESS_SIGN` / `OK_ACCESS_PASSPHRASE` 与 login payload 里的 `passphrase` / `sign` 均以 `***` 代替，其余字段照打。
- 共同部分不设候选、随 A 执行：删掉 `WsBaseAsync.py:134` 的 `logger.setLevel(logging.DEBUG)`，改回实例级；级别交给应用侧 handler（与 `okxsdk/__init__.py` 既有约定对齐）。
- 补 2 条契约测试到 `test/unit/okxsdk/test_logging.py`：日志不含凭据；连续建两个 debug 取值不同的实例后模块 logger level 不变。
- 不选 B（排障价值太低）、C（`debug=True` 失去意义）。
- ADR-0020 头部提案状态行已删除，Considered Options 里「保留字段名、值打掩码」标为拍板采纳项。
- 状态暂留 `ready-for-agent`：代码已施工并验证但未提交，无 commit hash 可写 `Done in:`；提交后再转 `resolved`。

**施工（2026-11-06，并行子代理 B，未提交）**：

- `okxsdk/utils.py` 新增 `_masked_header()` 返回脱敏副本，`get_header` / `get_header_no_sign` 的 debug 行改打印副本；真正返回给请求的 header 不变。
- `okxsdk/websocket/WsBaseAsync.py` 删 `logger.setLevel(logging.DEBUG)`，login debug 行把 `apiKey` / `passphrase` / `sign` 置 `***` 后再打印，保留 op/args 结构。
- `test/unit/okxsdk/test_logging.py` 补 2 条契约测试（凭据不泄露、实例间 logger 级别不串），原有 3 个 case 仍通过。
- 集成验证：端到端用 `debug=True` 发 POST 捕获日志，真实 passphrase 与 api key 均不出现、`***` 存在；连建 `debug=True` / `debug=False` 两个实例后模块 logger level 不变；`pytest` 856 passed。
- `CHANGELOG.md` 的 Fixed 条目由主线程统一写进 `## [Unreleased]`。

## Comments

- 2026-11-06 审查提出：P1。对应 ADR-0020。
- 2026-11-06 用户逐条拍板取 A、两张 ADR 都生效；结论落在 `## Answer`，状态 `needs-triage` → `ready-for-agent`。

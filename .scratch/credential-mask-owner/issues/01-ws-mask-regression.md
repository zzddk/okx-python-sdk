# 01 · WS 脱敏契约的回归测试先行

Type: task
Status: resolved
Done in: b63aa67
Blocked by: —

## 为什么

`test_logging.py:47-89` 唯一的脱敏契约只走 REST POST；`test_wsbase_instances_do_not_change_module_logger_level`（`:92-104`）只构造实例、从不调用 `login()`。全仓 `debug=True` 的 WS 用例无日志断言。基线 155 passed 全绿正是盲区的证据。按 Q5 惯例，回归测试先于实现落地，先红后绿。

## 做什么

在 `test/unit/okxsdk/test_logging.py` 复用 `_CapturingHandler`，补一个 `debug=True` 的 WS 会话（`WsPublicAsync(url=..., connector=FakeConnector(FakeSocket(...)))`），并：

- **`send:` 主回归**：用含 `apiKey` / `passphrase` / `sign` 的 args 调公开 `send()`，断言捕获到的日志不含这三个值、`***` 在、字段名在。当前 `:402` 原样打印 → 红。
- **login 不变量 guard**：同一构造走 `login()`（用 `answer_login=ACK` 的 FakeSocket 让握手成功），断言同样三点。当前 `:292-298` 已掩码 → 绿。
- **只掩日志副本**：断言 FakeSocket 实际收到的 payload 仍含真实凭据值，防止实现把线上帧也改了。
- 保留 `Received message` 不在范围（`spec.md` 非目标）。

## 完成标准

1. `send:` 主回归在**当前代码下变红**（凭据值出现在日志里），证明测试抓得住漏洞。
2. login guard 当前即绿；既有用例一行不改即通过。
3. 不修改任何生产代码。
4. 报告明确的失败数，其余既有用例仍绿。

## Comments

- 2026-11-07 建单。基线：`pytest test/unit/okxsdk/test_logging.py test/unit/okxsdk/websocket/ -q` → 155 passed, 67 subtests passed。
- 2026-11-07 施工：新增 `_capture_ws_debug` / `_ws_session` / `_login_values` 三个 helper 与 2 条契约测试。先红验证 `1 failed, 6 passed`——`send:` 日志原样打印 `{"op": "login", "args": [{"apiKey": "WS_LEAK_KEY_abc123", ...}]}`，断言 `WS_LEAK_KEY_abc123 not in log_text` 失败；login guard 当期即绿。工单 02 + 03 同批落地后 `test_logging.py` → 7 passed、全量 864 passed, 336 subtests passed。

# 01 · 无凭据 WS 的回归测试先行

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: —

## 为什么

「无凭据 `Transport()` → `from_transport`」这条路径今天无人测：`test_ws_config.py:25-27` 的 `_transport()` 永远传真凭据，`test_network_hosts.py:72-77` 只用无凭据 `Transport()` 断言 `.url`，`test_ws_session.py:667` 的无凭据分支用 `''` 且不经 `from_transport`。基线 180 passed 全绿正是这个盲区的证据。按 Q5 拍板，回归测试先于实现落地，先红后绿。

## 做什么

在 `test/unit/okxsdk/websocket/test_ws_config.py::TestNoCredentials` 补主回归（跨 `from_transport` 这个真正的 seam，而不是 `session_config` 内部）：

- `WsPrivateAsync.from_transport(mock_transport())` 的 `start()` 抛 `ValueError`，文案含 `"apiKey, secretKey and passphrase are required for login"`。
- 同一构造下 `subscribe()` 抛同样的缺凭据错误。
- 断言 FakeSocket 未收到任何 `op: login` 帧——今天的 bug 形状是「垃圾凭据被上送」，不是「静默无认证」。
- 补一条重连不变量断言：缺凭据错误只在首次 `_open()` (`connection.py:164-170`) 冒泡到 `start()`，不得进入 `_reconnect()`（`:212` 会把普通 `ValueError` 当瞬时失败无限退避）。当前因 `_task` 创建在 `_open()` 之后而不可达，用 `assertIsNone(ws._connection._task)` 守住。
- 补一条 public 无凭据 guard：`WsPublicAsync.from_transport(mock_transport())` 正常连接、不发登录帧（对应工单 03 完成标准 2）。

无凭据 Transport 用不带凭据的 `mock_transport()`（三个凭据字段为 REST 哨兵、默认 `flag='1'` 选模拟盘私有主机），并以 `FakeConnector` 注入脚本化 socket，避免真实网络与环境代理。

## 完成标准

1. 上述断言在**当前代码下变红**：`start()` 抛 `LoginRejected: login rejected: code=60009`、`subscribe()` 抛 `RuntimeError: start() must be called before login()`，均非 `ValueError`，证明测试真的抓得住 bug。
2. 不使用 `_transport()` 构造无凭据 Transport，显式用不带凭据的 `mock_transport()`。
3. 不修改任何生产代码。
4. 工单 02 + 03 落地后全部转绿。

## Comments

- 2026-11-07 建单。基线：`pytest test/unit/okxsdk/websocket/ test/unit/okxsdk/test_transport.py test/unit/okxsdk/test_okxclient.py -q` → 180 passed, 76 subtests passed。
- 2026-11-07 施工：新增 `TestNoCredentials`（`start` / `subscribe` 主回归 + public guard 共 3 条）；`TestSessionConfig` 的翻译 guard 随工单 02 落地。先红验证 `2 failed in 0.11s`，异常类型如上（原完成标准写的「静默成功」是规格推断，实测 `subscribe()` 在 `start()` 前先撞上 socket 检查，已按实测修正）。02 + 03 同批落地后 `pytest test/unit` → 862 passed, 336 subtests passed，`ruff check` All checks passed。

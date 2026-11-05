# 04 · 签名原语留一份

Type: grilling
Status: resolved
Blocked by: —

## Question

评审候选 04。hmac+base64 有三份：`okx/utils.py:14-23`（`sign`，Transport 在用）、`okx/utils.py:55-88`（`signature`，零调用，9 行死代码）、`okx/websocket/WsUtils.py:11-23`（内联）。要定下：**原语留哪一份、叫什么、放在哪个模块，协议串拼装归谁。**

需要一起定下的：

1. **落点与命名**：保留 `utils.sign`，还是新开 `okx/signing.py`？名字如何说明「只做 hmac+base64，不拼协议串」。
2. `utils.signature`：直接删，还是保留别名一个版本。
3. **WS 侧保留什么**：时间戳、`GET`、path、op 的拼装放 `WsUtils` 还是 `okx/websocket/login.py`（ADR-0012 的落点）。
4. **行为差异**：编码、大小写、空串等是否与现状逐字节一致；用现有 WS 登录测试锁住。
5. **记账**：评审说无行为变化，是只写工单结论，还是仍要一份短 ADR。


## Answer

**拍板（2026-11-05）**：hmac+base64 只留 `okx/utils.py` 的 `sign(message, secret)`，签名与返回类型（bytes）不变；两边都调它。

**WS 拼装搬家**：时间戳、`GET`、`/users/self/verify` 与 JSON 外壳搬进 `okx/websocket/login.py`，导出 `login_payload(api_key, passphrase, secret_key, timestamp=None)`。`timestamp=None` 时取本地整秒时间，便于测试注入固定值。

**删除**：`okx/websocket/WsUtils.py` 整个文件（`initLoginParams` 与 `getLocalTime` 没有别的调用方）；`okx/utils.py:80` 的 `signature`（9 行、零调用、无测试）。`WsBaseAsync` 改为 `from okx.websocket.login import login_payload`，不再 import `WsUtils`。

**行为**：payload 与现状逐字节一致——`str(timestamp) + 'GET' + '/users/self/verify'`，`sign(...).decode('utf-8')`，键序 `apiKey/passphrase/timestamp/sign` 不变。`utils.sign` 与内联实现同为 sha256 + base64，无编码差异。

**记账**：不新写 ADR。`WsUtils.initLoginParams` / `WsUtils.getLocalTime` 的移除是公开面变化，进 CHANGELOG；`utils.signature` 从未被使用，不必单独列条。

**完成标准**：
1. `grep -rn 'hmac\|base64' okx/` 只在 `okx/utils.py` 命中。
2. `okx/websocket/WsUtils.py` 不存在；`grep -rn 'WsUtils\|signature(' okx/` 无命中。
3. WS 登录 payload 与 0.14.1 的字节一致（用固定 `timestamp` 断言整串）。
4. 测试把 `patch('okx.websocket.WsBaseAsync.WsUtils…')` 改成 `patch('okx.websocket.WsBaseAsync.login_payload')`；`test_ws_private_async` 的参数断言随之更新。
5. Transport 的签名路径不动，`test/unit/okx/test_transport.py` 保持绿；`pytest test/unit` 全绿。

**被否的选项**：新开 `okx/signing.py`（为一个函数换 import 地址，不增加保证）；保留 `WsUtils.initLoginParams` 只换内部实现（名字仍说不出属于哪一侧，且 `getLocalTime` 继续为它而存在）；给 `utils.signature` 一个弃用期（无调用方，弃用期只是让下一个人再猜一次）。

## Comments

- 2026-11-05 施工完成：e606dc9（master，合并入 0.15.0 未发布批次）。全量 pytest 853 passed / 46 subtests；完成标准逐条核对见提交说明与测试。
- 2026-11-05 评审补记：完成标准 4 字面要求 `patch('okx.websocket.WsBaseAsync.login_payload')`，施工时没有这条 patch，改由线上帧断言 `payloads[0]["op"] == "login"` 承担。两者不等价：只断言字节抓不到「又内联了一份能产出同样字节的实现」。已补 `test_login_goes_through_the_shared_payload_builder`，按字面锁住这条绑定。

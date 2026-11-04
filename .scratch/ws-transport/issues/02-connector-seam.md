# WS 连接接缝：WebSocketConnector 取代 WebSocketFactory

Status: resolved
Release: 0.11.0
Done in: 0.11.0

## 为什么

见 `spec.md` 与 ADR-0007。`WebSocketFactory` 是透传壳（37 行、2 个方法、1 个调用点），却带来三件事：与基类双份的 `websocket` 状态、`_close_socket` 里的双重关闭、以及一个只能靠模块级 monkeypatch 才能替换的接缝（21 处 patch）。代理也没有入口。

## 做什么

1. 新建 `okx/websocket/connector.py`：`WebSocketConnector(proxy=None)`，只暴露 `async connect(url) -> Connection`；ssl context 与 websockets 版本能力探测收在这里，不保存连接。
2. `WsBaseAsync.__init__` 增 `proxy=None, connector=None`，`connector` 优先；`connect()` 改走 `self._connector.connect(self.url)`。
3. 删除 `okx/websocket/WebSocketFactory.py`，`_close_socket` 里的 `factory.close()` 一并删掉（socket 这时只剩一处持有）。
4. 单测改注入假 connector。

## 完成标准

### 形状

1. `grep -rn WebSocketFactory okx/ test/ example/ README.md` 无命中。ADR 与 CHANGELOG 不在范围内：它们记录的是「已删除」，必须出现这个名字。
2. `WebSocketConnector` 的公开接口只有 `connect(url)`；没有 `websocket` 字段，没有 `close()`。socket 只由 `WsBaseAsync.websocket` 持有。

### 契约（每一条都要有用例）

3. `connector` 与 `proxy` 同时给时，connector 生效、proxy 被忽略，且不抛错——与 `Transport(proxy=, http=)` 一致。
4. 未给代理时，底层 `websockets.connect` 收到的关键字里**没有** `proxy`，保留库自身的默认（15.0 起自动使用系统/环境代理）。用例：假 connect 记录 kwargs，断言键不存在。
5. 给了代理且当前 websockets 签名支持 `proxy` 时，原样传给底层（假 connect 的签名里要显式带 `proxy`，否则会被第 8 条的能力探测判成不支持）。
6. 给了代理但签名不支持（用假 connect 模拟）时，在建立任何连接之前抛错，错误信息点名 `websockets>=15.0` 与替代做法（升级，或自建 connector）。断言假 connect **一次都没被调用**。
7. connector 无状态：同一 `WebSocketConnector` 连续两次 `connect` 返回两个连接，互不影响。
8. 能力探测发生在 `connect()` 时，读当时的 `websockets.connect` 签名，不在 import 时缓存。`connector.py` 用 `import websockets` 并在调用点取模块属性——否则 `03` 第 4 条那种替换做不到，第 6 条也写不出来。

### 测试面

9. 21 处 `patch('okx.websocket.WsBaseAsync.WebSocketFactory')` 全部消失（private 10、public 9、hardening 2）；这些测试改用 `connector=FakeConnector(...)`，连接仍是它们已有的 `_Socket`。
10. `env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest test/unit -q` 602 passed，用例数不减少（改写不算删除）。
11. `ALL_PROXY=socks5h://127.0.0.1:1` 下同样全绿：注入 connector 的路径不解析环境代理。

### 文档

12. CHANGELOG 的 0.11.0 段落记录 `WebSocketFactory` 删除，以及「自建连接」的替代写法（传 `connector=`）。ADR-0007 已记录决策。

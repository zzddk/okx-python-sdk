# WS 登录握手

把「哪一帧是登录回执、什么算拒绝、登录期间收到的其它帧去哪」从会话的两条路径收进一个 module。来源：2026-11-05 架构评审候选 03。

## 判断

`WsBaseAsync.login()` 有两条等待路径：

- **读循环在跑**（`_consuming()`）：给自己建一个 future 放进 `_login_waiter`，`_handle_message` 看到 `event=login` 就 `set_result` / `set_exception`。
- **没有读循环**（重连时的 `_restore_session()`，或 `connect()` 之后、`start()` 之前）：`_read_login_ack` 自己 `recv()`，把同一套判定再写一遍，并顺手把非登录帧 `_emit` 出去。

同一份协议两条实现：改「什么算拒绝」要动两个调用点，改超时文案要动三处，`_read_login_ack` 还多背一个投递职责。`_consuming()` 从「谁在读 socket」这个事实，变成 `_handle_message` 与 `login()` 共同的前提。

删除测试：把两条路径合成一个对象，复杂度不转移——判定、超时、投递各只写一次；会话只剩「谁喂帧」这一个分支，而那是真实差异：socket 只能有一个读者。

## 目标形状

`okx/websocket/login.py`：

```python
class LoginHandshake:
    def __init__(self, timeout: float = DEFAULT_LOGIN_TIMEOUT)
    @staticmethod is_ack(payload) -> bool
    @staticmethod rejection(payload) -> ConnectionError | None
    def feed(self, payload) -> bool                      # 读循环喂帧；True = 已消费
    async def wait(self) -> None                         # 读循环在喂时，会话等结论
    async def read(self, websocket, parse, deliver)      # 没读循环时自己收帧
```

- `feed` 收已解析的 payload：读循环本来解析过，不重复解析。
- `read` 自己解析 socket 帧；非回执帧交给 `deliver`（会话传 `self._emit`），保持「登录期间到达的推送照常投递」。
- 超时文案、拒绝判定、只认第一个回执，三件事都在 module 内。

`WsBaseAsync`：`_login_waiter` → `_handshake`；`_handle_message` 用 `LoginHandshake.is_ack` + `feed`；`login()` 只剩「发帧 + 决定谁喂帧」；删掉 `_read_login_ack` 与 `_login_rejection`。

## 非目标

- 不改 ADR-0005 的回调契约（async、按到达顺序串行、异常隔离、pong 不进回调）。
- 不删 `_consuming()`：socket 只能有一个读者，这个判断是真实差异。改动只是让它从三处收缩到 `login()` 一处。
- 不给 `LoginHandshake` 加事件或回调：它只回答一次登录，用完即弃。
- 不改重连顺序（connect → login → replay）。

## 验证

- 握手单测 7 条：接受、拒绝（code 与 msg 进异常）、数据帧不被消费、只认第一个回执、`read` 投递非回执帧、`read` 拒绝、`read` 超时。
- 会话层新增 1 条：没有读循环时，答案之前到达的帧仍交给回调。
- 既有的 `TestLoginThroughTheReader`、`TestSessionRestore` 一行不改就通过——两条路径的行为没变。

## 风险

- `login.py` 与 `subscriptions.py`、`connector.py` 同级，是可导入的公开名；以后改接口要走弃用流程，而不是直接改名。
- `read()` 多一个 `parse` 参数：让 module 自己解析会复制 `WsBaseAsync._parse` 的容错规则，两条解析规则迟早不一致。

# 03 · 重连把永久失败当瞬时失败

Type: grilling
Status: needs-triage
Blocked by: —

## Question

评审候选 03。`ConnectionSupervisor._reconnect()`（`okx/websocket/connection.py:196-206`）用 `except Exception` 接住所有失败，包括不会自愈的登录被拒（`ConnectionError`）与 proxy 能力缺失（`RuntimeError`），然后按 1s→60s 无限重试。`start()` 之后 task 永远不结束，用户只能从日志看到 `Reconnect failed`。

要定下：**哪些失败算永久、对外怎么表达、首次连接与重连是否共用同一条判据。**

## 证据

- `_reconnect` 的 catch 与 sleep 循环：`connection.py:196-206`。
- `LoginHandshake.rejection()`（`login.py:80-86`）抛普通 `ConnectionError`，与网络断线共用类型。
- `WebSocketConnector.connect()`（`connector.py:35-52`）在 websockets 不支持 proxy 时抛 `RuntimeError`。
- ADR-0005 约定断线由 `start()` 返回的 task 报出；重连路径没有做到。

## 建议方案

引入「可重试 / 永久」判据：

- 永久：登录拒绝（用 `LoginRejected(ConnectionError)` 子类或错误码字段）、proxy 能力缺失、非法 URL。
- 瞬时：`httpx`/socket 网络错误、握手超时。
- 永久错误让 task 以原异常结束；瞬时错误继续退避。

首次连接与重连共用同一条判据。

## 验收标准

1. 登录被拒后，task 在有限时间内以原始异常结束，不再重试。
2. 网络瞬断仍然重连，退避不变。
3. 新增两个用例：永久错误结束 task、瞬时错误继续重试。
4. 与 ADR-0005 的 task 语义对齐；若改变对外行为，补 ADR 或说明。

## 未决

- 永久错误的分类是「类型判断」还是「错误码判断」？建议类型，避免文案匹配。
- 是否给出重试次数上限（例如连续 N 次失败后结束）？

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 03。

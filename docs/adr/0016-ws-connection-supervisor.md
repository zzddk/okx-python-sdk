# 连接监督者独占 socket 与任务图

`WsBaseAsync` 同时是会话、任务状态机与订阅入口：socket、读循环任务、心跳任务、心跳事件、退避参数、停止标志六个字段散在类上，两条跨方法契约只由注释承载——心跳超时直接关 socket 叫醒读循环（`WsBaseAsync.py:465`），`stop()` 要先判断「我是被回调调用的，还是被外部调用的」才知道能不能取消任务（:171）。登录与重连也因此共享一个 `_consuming()` 分支：读循环没跑时，握手要自己 `recv()`。

我们决定：**socket 与任务图收进一个连接监督者**（`okx/websocket/connection.py` 的 `ConnectionSupervisor`），会话只保留「发送、订阅、登录、路由」。

- **拥有范围**：socket、读循环、心跳、退避/重连、停止五项归监督者；它不 import `subscriptions`，也不认识登录协议。
- **交接**：构造时传入 `on_frame(message)` 与 `on_ready()`。每帧先由监督者消费 `pong`，其余交给 `on_frame`；每次连上先起读循环，再 `await on_ready()`。`on_ready` 抛错即本次连接失败，进入退避重试。
- **首连也走 `on_ready`**：会话在 `on_ready` 里标记未登录、丢弃旧连接的一次性请求、按谓词决定是否登录、重放订阅。读循环已经在跑，`handshake.wait()` 永远成立，第二条读路径与 `_consuming()` 一起消失。
- **停止**：监督者用 contextvar 记录「正在派发帧」。`stop()` 置停止标志、停心跳、关 socket；在派发中立即返回，让当前帧走完，否则取消并等待监督者任务。
- **公开面**：删除 `connect()` 与 `consume()`；`websocket` 收成指向监督者 socket 的只读 property；`login()` 只能在 `start()` 之后调用。

## Considered Options

- **只把重连抽成函数**：改动最小，但 socket 与任务仍散在会话上，「关 socket 叫醒读循环」「stop 不能取消调用者」还是注释契约。
- **监督者连订阅与登录一起吃下**：它就得 import `subscriptions` 与 `login`，测试接缝从「帧进、帧出」变成整条协议，边界反而更难说清。
- **读循环把帧塞进队列，会话消费队列**：交接变成显式缓冲，但队列的生命周期、连接关闭时谁清空、残留帧怎么办都要自己管，收益只是把一次 `await` 换成一次 `put`。
- **保留 `connect()` 作为公开入口**：`connect()` 之后、`start()` 之前的状态（能否 send、stop 做什么）没有清晰语义，正是这次要删掉的半连接状态。

## Consequences

- `WsPrivateAsync.start()` 会在返回前完成登录；登录被拒绝时 `start()` 抛 `ConnectionError`，超时抛 `TimeoutError`。`WsPublicAsync.start()` 只在会话曾经登录过（业务频道）时才登录。
- `login()` 的前置条件收紧为「已经 `start()`」，与 README 一直写的用法一致；直接调用 `login()` 的代码不会再走到第二条读路径。
- 心跳仍然「关 socket 叫醒读循环」，但两边同属监督者；仍然不取消读循环，避免打断正在执行的用户回调。
- 测试只需一种 `FakeSocket`，经 `FakeConnector` 注入；不再写 `ws.websocket = …` 或 `ws._pong = …`。
- `connect()` / `consume()` 的移除、`websocket` 与 `isLoggedIn` 的只读化是破坏性变化，进 CHANGELOG。
- `LoginHandshake.read()`（无读循环那条路）失去调用点，随之删除；ADR-0012 的历史描述以本文为准。

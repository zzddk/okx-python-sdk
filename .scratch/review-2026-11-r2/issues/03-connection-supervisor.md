# 03 · 连接监督者的边界与接口

Type: grilling
Status: resolved
Blocked by: —

## Question

评审候选 03。`okx/websocket/WsBaseAsync.py`（484 行）同时是会话、任务状态机与订阅入口：socket 与任务图的六个字段散在类上，两条跨方法契约只由注释承载——心跳直接关 socket 叫醒读循环（:465），`stop()` 要先判断自己被谁调用（:171）。要定下：**「连接监督者」拥有什么、对外长什么样、会话剩下什么。**

需要一起定下的：

1. **拥有范围**：socket、读循环、心跳、退避、重连、停止——全部收进监督者，还是留一部分在会话。
2. **对外接口**：起、停、换连接三个动作的签名；失败如何表达（异常／回调／状态查询）。
3. **会话保留**：`subscribe`/`unsubscribe`/`login`/发送；它还能不能看到任务图或连接状态。
4. **消息交接**：读循环把消息交给谁——回调、队列、还是会话方法；这条决定测试接缝的形状。
5. **隐式契约显式化**：心跳与读循环之间「关 socket 叫醒」怎么表达（`asyncio.Event`／传递 close／超时）。
6. **外溢面**：`WsPublicAsync`/`WsPrivateAsync` 与两个 `from_transport` 的构造是否改变；若改变，是否破坏公共 API。
7. **测试面**：现在要手写三种 socket 替身（`test/unit/okx/websocket/test_ws_session.py:66,104,208,346` 写内部字段），收成一种后长什么样。
8. **与 05 对齐**：`needs_login()` 挂在哪一侧，为 05 留出接口。
9. **ADR**：新写一篇，记录监督者边界与被否的选项。


## Answer

**拍板（2026-11-05）**：新增连接监督者，独占 socket 与任务图；会话只剩发送、订阅、登录与路由。

**1. 边界**：监督者拥有 socket、读循环、心跳、退避/重连、停止五项。它不 import `subscriptions`，也不认识登录协议。会话保留 `start/stop/stop_sync/subscribe/unsubscribe/send/login/subscriptions` 与消息路由。

**2. 交接**：构造时传入 `on_frame` 与 `on_ready`。
- 每帧：监督者先消费 `pong`（心跳自己的协议），其余 `await on_frame(message)`；
- 每次连上：先起读循环，再 `await on_ready()`。会话在 `on_ready` 里做「标记未登录 → 丢弃旧连接的一次性请求 → 必要时登录 → 重放订阅」。因为读循环已在跑，`handshake.wait()` 永远成立，`_consuming()` 分支消失。
- `on_ready` 抛错即本次连接失败，交给退避重试，顺序与今天 `_reconnect` 一致。

**3. 公开面**：删除 `connect()` 与 `consume()`；`websocket` 收成只读 property 指向监督者的 socket；`login()` 只能在 `start()` 之后调用（README 一直这么写，现在代码也这样）。`isLoggedIn` 留在会话，供 05 使用。

**4. stop**：监督者改用「正在派发帧」的 contextvar 代替任务身份判断。`stop()` 置停止标志、停心跳、关 socket；在派发中就立即返回（让当前帧走完，读循环随后自然退出），否则 await 监督者任务。`stop_sync()` 保持不变。

**5. 心跳契约**：仍然是「关 socket 叫醒读循环」，但两边同属监督者，不再是跨方法契约；不取消读循环，避免打断正在执行的用户回调。

**6. 子类**：`WsPublicAsync` 删除纯转发的 `__init__`，改用类属性 `_DEFAULT_URL`；`WsPrivateAsync` 保留必填凭证，不再重复声明 url 默认值。`from_transport` 不变。

**7. ADR**：新写 `docs/adr/0016-ws-connection-supervisor.md`，记录边界、`connect()/consume()` 的移除、首连也走 `on_ready`。

**完成标准**：
1. 新模块（建议 `okx/websocket/connection.py`）不 import `subscriptions`、`login`；会话类不再持有 `_task/_consumer/_heartbeat/_pong/websocket`。
2. `grep -n 'current is\|_consuming\|_consumer\|_pong' okx/websocket/WsBaseAsync.py` 无命中。
3. 测试不再写 `ws.websocket = …` 或 `ws._pong = …`；三种 socket 替身收成一种，全部经 `FakeConnector` 注入。
4. 覆盖：回调里调 `stop()` 不死锁；心跳超时触发一次重连；重连后登录与重放顺序正确；`on_ready` 失败进入退避。
5. 删除 `connect()/consume()` 记入 CHANGELOG 的破坏性段；README 的 WS 示例无需改。
6. `pytest test/unit` 全绿。

**未决**：`LoginHandshake.read()`（无读循环那条路）在 03 之后可能没有调用点；是否删除不在本单，留到 04 的死代码清理或单独一张。

## Comments

- 2026-11-05 施工完成：3a6e1df（master）。全量 pytest 850 passed / 68 subtests；完成标准逐条核对见提交说明与 ADR-0016。

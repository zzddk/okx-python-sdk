# 登录协议收进一个握手对象，两条读帧路径共用它

> 2026-11-05 补记：ADR-0016 让连接监督者在每次连上后先起读循环，再跑会话的 `on_ready`，因此「没有读循环」那条路径不再存在，`LoginHandshake.read()` 与 `_consuming()` 已随 03 删除。本文其余部分记录的是当时的取舍。

`WsBaseAsync.login()` 有两种等回执的方式：读循环在跑时，它把 future 挂在 `_login_waiter` 上，由 `_handle_message` 结算；读循环没跑时（重连后、或 `connect()` 之后 `start()` 之前），`_read_login_ack` 自己 `recv()`，把同一套判定再写一遍，还顺手把非登录帧 `_emit` 出去。

于是「哪一帧算登录回执」「什么算拒绝」「超时说什么」这三件事各有两份实现；`_consuming()` 这个「谁在读 socket」的事实，则同时是 `_handle_message` 与 `login()` 的前提。

我们决定：**登录协议由一个 `LoginHandshake` 拥有**。它接受帧（`feed`），给出结论（`wait` 返回或抛 `ConnectionError` / `TimeoutError`）；没有读循环时，由它自己从 socket 收帧（`read`），非回执帧交给调用方投递。会话不再知道登录帧长什么样。

## Considered Options

- **只抽判定**（`is_ack` / `rejection` 两个纯函数）：diff 最小，但超时实现、`_login_waiter` 的条件结算、`_read_login_ack` 的投递职责全部留下——规则仍然是两份，只是其中一份更短。
- **用帧队列统一两条来源**：读循环把每帧塞进 `asyncio.Queue`，握手只读一个 `AsyncIterator`，`login()` 里不再有 `_consuming()`。等待路径只剩一条，代价是读循环每帧多一次入队、队列生命周期与残留帧（连接关闭时谁清空）要自己管，而这条分支一天只走两次：启动与重连。
- **重连时先起读循环再登录**：能彻底删掉直连路径，但会改变「登录完成后才开始投递」的时序，且 `connect(); login(); start()` 这种用法直接坏掉。
- **保留现状，只把 `_login_rejection` 共享**：判定确实只有一份，但两个调用点的分支、两份超时、`_read_login_ack` 的 `_emit` 都还在，改动收益接近零。

## Consequences

- `okx.websocket.login` 是可导入的公开模块（与 `subscriptions`、`connector` 同级）。改它的接口要走弃用流程；它也是登录行为的唯一测试入口——7 条单测不需要 session、socket 或事件循环之外的任何东西。
- `_consuming()` 保留，但只出现在 `login()` 里，含义收敛为「这次由谁喂帧」。socket 只能有一个读者，这个分支是真实差异，不该假装消失。
- 登录期间到达的其它帧仍照常投递（`read` 的 `deliver` 参数），ADR-0005 的串行与异常隔离契约一字未动。
- 一次连接一个握手对象：`login()` 每次新建，重连不会读到上一个连接的结论。
- 超时文案、拒绝异常的 code/msg 格式保持原样，调用方捕获 `ConnectionError` / `TimeoutError` 的代码无需改动。

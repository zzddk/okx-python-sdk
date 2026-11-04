# WS 订阅与消息路由

把「哪条消息交给哪个回调」从读循环里的一个全局字段，收成一个可独立测试的深模块。来源：2026-11-05 设计评审。

## 判断

`WsBaseAsync` 的会话生命周期（心跳、pong 判定、指数退避重连、登录回执、异常隔离）是深模块：接口约 10 个方法，实现装着 471 行，杠杆在，不动。

浅的是订阅与回调的关系，三处事实：

- `WsBaseAsync.py:336`：`if callback is not None: self.callback = callback`。第二次 `subscribe` 覆盖第一次，此后**所有**消息（含第一个频道的）都进最后一个回调。多频道订阅在接口上成立，在实现上不成立。
- `WsBaseAsync.py:202`：`_emit` 只读 `self.callback`，没有按 `payload["arg"]` 分发。调用方要自己在回调里 `if channel == ...`。
- `WsBaseAsync.py:86,357-369`：`subscriptions` 是 `{整条 arg 的 JSON: arg}`，只为重连重放存在，不含 callback。**「订阅 ↔ 回调」这个关系在代码里没有载体。**

删除测试：把路由删掉，复杂度不会消失，而是回到每个调用方的 `if channel == ...` 分支里，按调用点数重现。这一层值得有名字。

另有一处死代码：`WsUtils.checkSocketParams` / `initSubscribeSet` / `getParamKey` 在生产代码里零调用（只有 `test_ws_hardening.py:21-33` 直接测它们），`getParamKey` 用 `"@" + str(arg[k])` 拼键、不含 channel，会碰撞。连同 `isNotBlankStr` 一起删。

## 方案

新增 `okx/websocket/subscriptions.py`：纯数据，不访问网络、不创建任务、不记日志、不 import `websockets`。

```python
class Subscription:                     # 值对象
    params: Tuple[Dict[str, Any], ...]
    callback: Optional[Callback]

class Subscriptions:
    def add(self, params, callback=None) -> Tuple[Subscription, ...]
    def remove(self, params) -> Tuple[Subscription, ...]
    def add_request(self, request_id, callback) -> None
    def drop_requests(self) -> None
    def take(self, payload) -> Optional[Callback]
    def replay(self) -> List[Dict[str, Any]]
```

`WsBaseAsync` 只留一个字段 `self._subs`：`subscribe`/`unsubscribe` 变成「先改表，再发帧」，`_record`/`_arg_key`/`_resubscribe` 删除，`_handle_message` 结尾由 `_emit(message)` 改为「`take(payload)`，未命中再退回 `self.callback`」。

## 接口契约

写进 docstring，每条都有用例：

1. **路由键是整条 `arg`。** `json.dumps(arg, sort_keys=True)`，与现有重放键一致，所以重连后订阅自动接上。同一 channel 的不同 `instId` 各走各的回调。
2. **后订阅同一 `arg` 覆盖先前的回调。** `Subscription` 是替换不是追加；没有第二个消费者，不做广播。
3. **`take` 先看 `arg`，再看 `id`。** 有 `arg` 且命中 → 订阅的 callback（订阅持久，不删）。无 `arg` 但有 `id` 命中 → 该请求的 callback，**并删除该请求条目**（op 回执只有一条）。都没命中 → `None`。
4. **`callback=None` 的订阅只用于重放。** 路由命中但回调为空时 `take` 返回 `None`，消息落到 `WsBaseAsync.callback`。这条让「订阅但不指定回调」有确定语义，也让兜底路径可测。
5. **`id` 不参与订阅键。** 订阅的 `id` 只是发给服务器的请求标识；路由只看 `arg`。
6. **请求表是一次性的。** `add_request` 只被 `take` 消费；`drop_requests()` 在重连与 `stop()` 时清空——旧连接上的回执不会再来，留着只会泄漏。
7. **`replay` 按加入顺序返回 params 的副本。** 不返回内部对象引用；不含请求条目；退订的条目不再出现。
8. **不改变执行顺序。** `take` 只选回调，调用仍在读循环同一个 await 点。ADR-0005 的「按到达顺序串行、异常隔离」原样成立。
9. **`take` 对任意输入都不抛异常。** 服务器数据不可信：非 dict、`arg` 非 dict、缺 `id` 一律返回 `None`。

`WsBaseAsync` 侧的三条：

10. **`self.callback` 保留为兜底，标 deprecated。** 赋值仍然生效，路由未命中时使用；README 与 docstring 引导新代码改用 `subscribe(params, callback)`。1.0 前删除。
11. **`self.subscriptions` 变成只读 property**，返回 `{key: dict(arg)}` 视图（由 `_subs` 派生，不另存状态），标 deprecated。写入抛 `AttributeError`——伪造内部订阅表不是可支持的用法。
12. **`send(op, args, callback, id)` 分三种。** 有 `callback` 有 `id` → `add_request(id, callback)`；有 `callback` 无 `id` → 退回设置兜底 `self.callback`（无法关联，保持旧行为）；无 `callback` → 不动任何表。`subscribe`/`unsubscribe` 走 `add`/`remove`，不走 `add_request`。

## 测试面

接缝即测试面。`Subscriptions` 的六条契约（键、覆盖、两次 take、重放顺序、退订、脏数据）全部用普通单测锁住：不需要事件循环、不需要假 socket、不需要 `asyncio.run`。

`WsBaseAsync` 只留三条需要会话的用例：未命中落兜底、命中不进兜底、重连后按 `replay` 重发。路由正确性不再由会话测试承担。

## 发布切分

一次走 0.12.0（ADR-0004：一批一 minor）。`callback` 废弃与 `subscriptions` 收窄都是公共契约变化，补丁版本装不下。

- `01` 纯增量：新增模块与纯单测，不接线。
- `02` 接线，改存量断言（`test_ws_public_async.py:275-299` 目前锁的是「后订阅覆盖 callback」，要改成「各自回调」）。
- `03` 独立：删 `WsUtils` 四件套死代码。

## 不选的方案

- **A：在 `WsBaseAsync` 内置路由表。** 接口零改动，但 `_routes` 与 `subscriptions` 变成两份状态，会重演上一轮 `WebSocketFactory` 与基类各存一份 socket 的漂移；路由逻辑也埋进 471 行的会话类，只能靠假 socket 测。
- **C：`on`/`off` 多监听、按 channel 广播。** OKX 一个连接本就一一对应订阅，没有第二个消费者的证据。为一个不存在的适配器加广播能力，是把深度换整齐。
- **按 channel 路由 op 回执。** 订单请求的响应是 `{"id": "...", "op": "order", "data": [...]}`，没有 `arg`，按 channel 查不到任何东西。`id` 是这类回执唯一的关联键，必须经手。

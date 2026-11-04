# WS 消息按订阅路由，callback 降为兜底

`WsBaseAsync` 只有一个 `self.callback`，`send()` 每收到一个 callback 就整体替换它（`WsBaseAsync.py:336`）。于是「订阅两个频道、各给一个回调」在接口上成立、在实现上不成立：第二个 `subscribe` 之后，第一个频道的消息也进了第二个回调。而服务器推送里的 `arg`（`channel` + `instType` + `instId`）本来就能唯一确定一条订阅——信息一直在帧里，只是没人用它。

我们决定：**消息按它携带的 `arg` 投递给该订阅的回调；`arg` 未命中时再看 `id`；都没有才落到 `WsBaseAsync.callback`**。路由、重放和一次性请求收进 `okx/websocket/subscriptions.py` 的 `Subscriptions`（纯数据，6 个方法，不碰 IO）。`self.callback` 保留为兜底并标废弃，1.0 前删除。

## Considered Options

- **在 `WsBaseAsync` 里加一张路由表**：接口零改动，但 `_routes` 与既有 `subscriptions` 会变成两份状态，重演 `WebSocketFactory` 与基类各存一份 socket 的漂移；路由逻辑也埋进 471 行的会话类里，只能靠假 socket 测。
- **`on`/`off` 多监听、按频道广播**：能力更强，但 OKX 一个连接本来就一一对应订阅，没有第二个消费者的证据。为一个不存在的适配器加广播，是用深度换整齐。
- **op 回执按频道路由**：订单请求的响应是 `{"id": "...", "op": "order", "data": [...]}`，**没有 `arg`**，按频道查不到东西。`id` 是这类回执唯一的关联键，必须由路由层经手，不能只透传。
- **保留 `callback` 的「最后设置者赢」语义**：这正是 bug 本身；它还把「哪一个回调」变成依赖调用顺序的隐式状态。

## Consequences

- 破坏性改动，随 0.12.0 发布（ADR-0004 的一批一 minor）。`ws.callback` 仍可读写，但只在路由未命中时生效；`ws.subscriptions` 变为只读视图。迁移说明写进 CHANGELOG。
- **补充 ADR-0005，不取代它。** 那里承诺的是回调的执行语义（async、按到达顺序串行、异常隔离），`take` 只负责选回调，调用仍在读循环同一个 await 点，三条全部原样成立。
- 订阅键沿用 `json.dumps(arg, sort_keys=True)`，与 0.11 的重放键逐字节相同，所以升级后重连逻辑不需要迁移。
- 请求表是一次性的：`take` 命中即删，重连与 `stop()` 时整体清空。否则每个没有回执的 `place_order` 都会在表里留一条。
- 路由正确性从会话测试移到 `Subscriptions` 的纯单测；`WsBaseAsync` 只剩「未命中落兜底 / 命中不进兜底 / 重连按序重放」三条需要假 socket。

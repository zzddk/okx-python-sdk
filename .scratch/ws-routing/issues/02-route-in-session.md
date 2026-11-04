# WsBaseAsync 接上路由

Status: ready-for-agent
Blocked by: 01
Release: 0.12.0

## 为什么

`subscriptions` 建好了不接线，覆盖 bug 就还在：`WsBaseAsync.py:336` 仍然把 `self.callback` 换成最后一个订阅的回调。这一步把读循环从「一个全局字段」改成「先问 `Subscriptions`，未命中再落兜底」。

## 做什么

1. `__init__`：`self.subscriptions = {}` 换成 `self._subs = Subscriptions()`；`subscriptions` 改成只读 property，返回 `{key: dict(arg)}` 视图，标 deprecated。
2. `subscribe` / `unsubscribe`：先 `_subs.add`/`_subs.remove`，再发帧。发送失败时表已经改了——重连会重放一次成功的订阅，这是安全方向，不要回滚。
3. `_record`、`_arg_key`、`_resubscribe` 删除；`_reconnect` 里改调 `_replay`：`args = self._subs.replay()`，空则直接返回，否则逐个 `_send_payload("subscribe", [arg], None)`，日志用 `len(args)`。
4. `send` 的 callback 处理按 spec 第 12 条三分支：有 id 走 `add_request`，无 id 退回 `self.callback`，无 callback 不动表。
5. `_handle_message` 的投递：`callback = self._subs.take(payload)`，为 `None` 时取 `self.callback`；两者都空就丢弃。`_emit` 增加一个可选 callback 参数，或改成 `_deliver(message, callback)`——保持「一个 await 点」不变。
6. `stop()` 与 `_restore_session()` 调 `self._subs.drop_requests()`：旧连接上的回执不会再来。
7. `self.callback` 的 docstring 与赋值点保留，注明它是兜底路径、1.0 前删除。

## 完成标准

### 形状

1. `grep -n "_record\|_arg_key" okx/websocket/WsBaseAsync.py` 无命中。
2. `WsBaseAsync` 里不再有 `Dict[str, Dict[str, Any]]` 形态的订阅表；订阅状态只存在于 `self._subs`。
3. `ws.subscriptions` 读取仍然可用（形状不变）；写入抛 `AttributeError`。

### 行为（每条一个会话用例，走公开接口）

4. 两个频道分别 `subscribe` 后，各自的消息只到各自的回调，互不覆盖。
5. 未订阅的 `arg` 落到 `ws.callback`；已订阅但 `callback=None` 的也落兜底；兜底为空时静默丢弃。
6. `place_order(args, callback=cb, id="o1")` 后收到 `{"id": "o1", "op": "order", "data": []}`（无 `arg`）路由到 `cb`，且不经过 `ws.callback`；第二次同 id 回执走兜底。
7. `place_order(args, callback=cb)`（无 id）仍设置 `ws.callback`，与 0.11 行为一致。
8. 重连后 `replay` 的帧顺序与 `add` 顺序一致；重连会清空请求表，`add_request` 的条目不再等待。

### 存量测试

9. `test_ws_public_async.py:275-299` 与 `test_ws_private_async.py:80,190,255,288,318,351,386,419`、`test_ws_public_async.py:129,240` 中「调用带 id 后断言 `ws.callback == callback`」的写法必须改写：带 id 的走路由，不再改 `ws.callback`。改写后断言的仍是同一条契约（回执交给了谁），只是经由 `_handle_message` 驱动。
10. `test_ws_session.py:199-237` 里直接读写 `ws.subscriptions` 的三处改为操作 `Subscriptions` 或走 `subscribe`；不得为了测试保留可写属性。

### 回归

11. `env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest test/unit -q` 全绿，用例数不减少（01 新增的照常计入）。
12. CHANGELOG 新增 `[0.12.0]` 段：多频道订阅各自的回调、`ws.callback` 降为兜底并标废弃、`ws.subscriptions` 变只读。迁移一行：把 `ws.callback = f` 换成 `await ws.subscribe(params, f)`。

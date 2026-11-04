# 新增 Subscriptions 深模块

Status: ready-for-agent
Release: 0.12.0

## 为什么

见 `spec.md` 与 ADR-0009。「订阅 ↔ 回调」这个关系目前只活在 `WsBaseAsync.callback` 一个字段里，第二次 `subscribe` 就把第一次覆盖掉。把它挪进一个不碰 IO 的值对象，路由、重放、退订、一次性请求全部能用普通单测锁住，不必启动事件循环。

## 做什么

新建 `okx/websocket/subscriptions.py`：

```python
Callback = Callable[[Any], Any]

class Subscription:
    params: Tuple[Dict[str, Any], ...]
    callback: Optional[Callback]

class Subscriptions:
    def add(self, params: Sequence[Dict[str, Any]], callback: Optional[Callback] = None) -> Tuple[Subscription, ...]
    def remove(self, params: Sequence[Dict[str, Any]]) -> Tuple[Subscription, ...]
    def add_request(self, request_id: str, callback: Callback) -> None
    def drop_requests(self) -> None
    def take(self, payload: Any) -> Optional[Callback]
    def replay(self) -> List[Dict[str, Any]]
```

模块只依赖 `json` 与 `typing`。`WsBaseAsync` 的 `Callback` 从本模块重新导入，`from okx.websocket.WsBaseAsync import Callback` 继续可用（`WsPrivateAsync.py:11` 依赖它）。

## 完成标准

### 形状

1. `subscriptions.py` 不出现 `import asyncio`、`import websockets`、`logging`，无模块级可变状态。`grep -nE "asyncio|websockets|logging" okx/websocket/subscriptions.py` 无命中。
2. `Subscriptions` 的公开方法恰好是上面 6 个，无私有字段被外部访问。
3. 键规范化只有一个函数，产出与 `WsBaseAsync._arg_key` 相同的字符串（`json.dumps(arg, sort_keys=True)`）——重连后既有订阅能直接接上，不需要迁移。

### 契约（spec.md 1-9 条，每条约一个用例）

4. 同一 channel 两个 `instId` 各回各的回调。
5. 同一 `arg` 再次 `add` 覆盖旧回调，表内仍只有一条。
6. `take` 命中 `arg` 返回订阅回调且**不删除**订阅；连续两次 `take` 同一 payload 都返回同一回调。
7. `take` 对请求条目返回回调后**删除**它；第二次返回 `None`。
8. `add` 时 `callback=None`，命中 `arg` 返回 `None`（由调用方落兜底）。
9. `remove` 后该 `arg` 的 `take` 返回 `None`；`remove` 不存在的 `arg` 返回空元组、不抛错。
10. `replay()` 顺序等于 `add` 顺序，返回的 dict 修改后不影响内部表；退订与请求条目不出现在结果里。
11. `drop_requests()` 后所有请求条目消失，订阅不受影响。
12. `take` 对 `None`、字符串、列表、`{}`、`{"arg": "x"}`、`{"id": 123}` 一律返回 `None`，不抛异常。

### 测试面

13. 新增 `test/unit/okx/websocket/test_subscriptions.py`，纯 `unittest`，文件内不出现 `asyncio.run`。
14. `env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest test/unit -q`：基线 617 passed，新增用例数按第 4-12 条计，原有用例数不减。

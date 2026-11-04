# WS 连接接缝

把 WebSocket 的连接建立从「模块全局的工厂」挪到「可注入的适配器」，顺带让 WS 能继承 REST 的代理。来源：2026-11-05 设计评审；收口 `ws-hardening/issues/04`（代理）。

## 判断

`WsBaseAsync` 已经是深模块：接口约 10 个方法（`start`/`stop`/`consume`/`login`/`subscribe`/`send`…），实现里装着心跳、pong 判定、指数退避重连、订阅回放、登录回执、回调异常隔离。杠杆在这里，不动。

浅的是它依赖的连接建立：

- `WebSocketFactory` 37 行、2 个方法、1 个调用点（`WsBaseAsync.py:82`）。删除测试：删掉它，复杂度只回到 `__init__`/`connect` 一处，不会在调用点重现——它是透传壳。真正值得留的只有 ssl context 与 websockets 版本差异。
- 它自己存一份 `self.websocket`（`WebSocketFactory.py:19`），基类另存一份（`WsBaseAsync.py:109`）。两份状态已经漂移：`_close_socket` 先关 socket 再调 `factory.close()`，后者因字段已空而成为空操作（`WsBaseAsync.py:459-466`）。
- 接缝落在模块全局而不是接口上：`patch('okx.websocket.WsBaseAsync.WebSocketFactory')` 在单测里出现 21 次（private 10 / public 9 / hardening 2）。假连接的需求是真实的，入口错了。
- 没有代理入口，而 `Transport` 又不保留 `proxy`（`transport.py:44,58` 把参数交给 `_make_http` 后丢弃），所以「`from_client` 继承 REST 的代理」在当前代码上无法实现。

## 方案

**B：注入连接适配器实例。** `WebSocketConnector` 取代 `WebSocketFactory`，只暴露一个方法，不存 socket：

```python
class WebSocketConnector:
    def __init__(self, proxy: Optional[str] = None) -> None: ...
    async def connect(self, url: str) -> Connection: ...
```

`WsBaseAsync.__init__` 增两个参数，其余签名不变：

```python
def __init__(..., proxy: Optional[str] = None,
             connector: Optional[WebSocketConnector] = None) -> None
```

`connector` 优先于 `proxy`（与 `Transport(proxy=, http=)` 的既有优先级一致，`transport.py:37-38`）；默认构造 `WebSocketConnector(proxy=proxy)`。`connect()` 变成 `self.websocket = await self._connector.connect(self.url)`。

配套：`Transport` 保留 `proxy` 字段（`issues/01`，非破坏），`from_client` 改名为 `from_transport` 并从 transport 取代理（`issues/03`，破坏）。

## 接口契约

写进 `WebSocketConnector` / `WsBaseAsync` / `from_transport` 的 docstring，并有用例锁住：

1. **connector 优先于 proxy。** 两者同时给时 proxy 被忽略，不报错——与 `Transport` 同一规则。
2. **未给代理时不传 `proxy=`。** 保持 websockets 自己的默认（15.0 起自动使用系统/环境代理；本机 17.4 的 `proxy` 默认为 `True`，与 httpx `trust_env=True` 一致）。把 `proxy=None` 显式传下去会关掉环境代理，是静默的行为变更。
3. **不支持代理的版本必须报错，不能直连。** 能力用 `inspect.signature(websockets.connect)` 判断：`requirements.txt` 的下限是 `>=10.0`，而 `proxy=` 自 15.0 才有。缺少该参数时，带 proxy 的 connector 在建立连接前抛明确错误。默不作声地直连，等于把本该走代理的流量漏到公网。
4. **connector 无状态。** 不保存连接、不缓存；同一实例可被多次 `connect`，socket 只由 `WsBaseAsync.websocket` 持有。
5. **`http=` 与 WS 无关。** WS 的代理只来自 `transport.proxy`。`Transport(http=...)` 是 REST 侧「不解析环境代理」的开关，不延伸到 WS：没设代理时 WS 仍跟随环境，与直接构造 WS 一致。否则 ADR-0006 的「注入 http 就自己负责代理」会被读成对 WS 也生效。

## 测试面

接缝即测试面：21 处模块级 patch 全部删除，改由 `connector=FakeConnector(sockets=...)` 驱动（session 测试里已有的 `_Socket` 正是假适配器的连接）。`ALL_PROXY=socks5h://127.0.0.1:1` 下必须仍全绿，锁住「注入后不解析环境代理」。

## 发布切分

按 ADR-0004：`01` 纯增量，随 0.10.x 补丁走；`02`+`03` 共享同一段迁移说明（WS 构造方式的改变），集中到 0.11.0。证据见 ADR-0007、ADR-0008。

## 不选的方案

- **注入裸函数 `connect(url)`**：接口最小，但代理得靠 `partial` 绑定，等于把「代理归属」从接口挪进调用方的样板代码；而且没有地方安放版本能力探测。
- **让 REST 的 `Transport` 兼管 WS**：`request(method, path, params)` 是请求响应，WS 是流式帧 + 长生命周期，接口不匹配。给 46 个 REST 模块共用的接口加一条它们用不到的 `connect_ws()`，深度反而下降。
- **保留 `from_client` 别名**：0.10.0 的迁移已经把旧构造方式清干净，留别名等于让一个名不副实的入口活到 1.0。

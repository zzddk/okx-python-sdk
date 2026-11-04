# WS 从 Transport 构造：from_client 改名为 from_transport

`WsPrivateAsync.from_client(client)` 用鸭子类型读取 `API_KEY` / `API_SECRET_KEY` / `PASSPHRASE` / `flag` / `debug`，所以任何长得像的对象都能传，单测传的就是 `SimpleNamespace`。ADR-0006 之后，这些配置的唯一持有者是 `Transport`；名字却还说「client」。同时 WS 需要代理，而代理必须有一个明确的来源对象。

我们决定：**两个 WS 客户端都只提供 `from_transport(transport, ...)`，参数做 `isinstance(transport, Transport)` 校验，不留 `from_client` 别名**。主机按 `transport.flag` 选，代理取 `transport.proxy` 并交给 `WebSocketConnector`。为此 `Transport` 要保留 `proxy` 字段（`ws-transport/issues/01`）。

## Considered Options

- **保留鸭子类型、只改名**：`from_transport` 收任何对象，等于名字继续承诺它不检查的东西；`transport.proxy` 取不到时还得靠 `getattr` 兜底，把类型错误推迟到连接时。
- **保留 `from_client` 并另加 `from_transport`**：两个入口、两套语义，用户要判断该用哪个；0.10.0 的迁移已经把旧构造方式清干净，没必要在 WS 上留一条旧路。
- **接受 API 门面或 `Transport` 都行**：门面只是转发 `Transport` 的属性，收一个明确的配置对象已经够用，多一种输入只会让 `isinstance` 校验失去意义。

## Consequences

- 破坏性改动，与 ADR-0007 同一批，随 0.11.0 发布；迁移是一行：把 API 实例换成构造它用的 `Transport`。
- **取代 ADR-0006 的一条后果。** 那里写的是「`WsPrivateAsync.from_client` 与既有的读取代码不必改」；现在必须改。ADR-0006 的其余结论不变。
- 代理只从 `transport.proxy` 继承。`Transport(http=...)` 的「不读环境代理」是 REST 侧规则，不延伸到 WS；没设代理时 WS 仍跟随环境，与直接构造一致。
- README 的 WS 示例必须改写法：先建 `Transport`，再同时传给 REST API 类与 `from_transport`。旧示例把 `AccountAPI` 实例传进去，改名后不再是合法输入。
- 单测不能再拿 `SimpleNamespace` 冒充 client，要构造 `Transport(http=httpx.MockTransport(...))`，顺带保证测试不读环境代理、不建真实连接。
- `okx/websocket` 首次依赖 `okx.transport`。没有循环：`transport` 不引用 websocket。

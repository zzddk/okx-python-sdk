# REST 配置上移到 Transport，API 类只收一个实例

每个 REST API 类都继承 `OkxClient`，而 `OkxClient` 的构造函数背着 11 个参数：凭证、域名、代理、重试、限流。它们描述的是「怎么发请求」，不是「这个端点要什么」。共享连接池只能靠 `client=`：把一个已经造好的 API 类传给另一个，内部用 11 行字段拷贝模拟共享；它既没法表达「两个不同凭证的客户端」，读起来也像是「复用另一个类的端点」。

我们决定：**`Transport` 持有全部 REST 配置与连接池，API 类只接收一个 `Transport`**。`client=` 删除；`_request_with_params` 与 `_request_without_params` 合并为 `request(method, path, params=None)`。

## Considered Options

- **继续用 `client=` 共享**：它要求源对象已经是 API 类，且复制而非共享配置——改了其中一个的 `max_retries`，另一个不会跟着变，而连接池却是共享的。两种语义混在一个参数里。
- **保留 11 个参数并新增 `transport=`**：两套配置来源必然要回答优先级，T1 的过渡态已经证明了这一点。迁移成本只是把同一串参数挪进 `Transport(...)`。
- **只保留模块级单例 transport**：测试和「不同环境两个客户端」都会立刻需要例外，配置就重新散落回调用点。

## Consequences

- 破坏性改动，随 0.10.0 发布。ADR-0004 规定「一批对应一个以它为主题的 minor」，0.9.0 是 WebSocket 那一批，0.10.0 是这条规则下的下一批。迁移表写在 CHANGELOG，逐条列出每个构造参数的去处。
- 迁移成本集中在一处：`TradeAPI(Transport(...))`。想共享连接池，就把同一个 `Transport` 传给多个 API 类。
- `OkxClient` 保留只读属性并转发到 `Transport`，`WsPrivateAsync.from_client` 与既有的读取代码不必改。
- 显式注入 `http=` 的 `Transport` 不读环境代理，由调用方负责代理配置。
- `OkxClient.request` 成为端点方法与传输层之间唯一的接缝；测试用假 `Transport` 就能截获每个端点的 `(method, path)`，不必再造一个实例。

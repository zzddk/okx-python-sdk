# WebSocket 连接改由可注入的适配器承载

WS 层的连接建立原本是 `WsBaseAsync.__init__` 里硬造一个 `WebSocketFactory`（`WsBaseAsync.py:82`）。工厂 37 行、2 个方法、只有 1 个调用点，删除测试说它是透传壳；但它自己存了一份 `websocket`，与基类那份形成两份状态，`_close_socket` 因此会关两次。更麻烦的是接缝位置：单测只能用 `patch('okx.websocket.WsBaseAsync.WebSocketFactory')`（21 处）替换它，而代理参数没有地方可放。

我们决定：**删除 `WebSocketFactory`，连接由注入的 `WebSocketConnector` 实例承担**。接口只有一个方法 `async connect(url) -> Connection`，返回连接而不持有它；ssl context 与 websockets 的版本能力差异收在实现里。`WsBaseAsync` 新增 `connector=` 与 `proxy=` 两个参数，`connector` 优先，规则与 `Transport(proxy=, http=)` 相同。未给代理时不向底层传 `proxy=`，保留库自身默认（15.0 起自动使用系统/环境代理，与 httpx `trust_env=True` 一致）。

## Considered Options

- **保留类，只改为注入实例**：改动最小，但会继续保留「工厂持有 socket」的双份状态；换名字与换生命周期成本相同，索性一起改掉。
- **注入裸函数 `connect(url)`**：接口更小，却是把代理归属推给调用方的 `partial`，也没有地方安放版本探测。
- **让 REST 的 `Transport` 兼管 WS**：`request(method, path, params)` 是请求响应，WS 是流式帧 + 长生命周期。给 46 个 REST 模块共用的接口加一条无人使用的 `connect_ws()`，等于用深度换整齐。

## Consequences

- 破坏性改动，随 0.11.0 发布（ADR-0004 的一批一 minor）。`WebSocketFactory` 是 import 路径可见的名字，CHANGELOG 给出替代写法：自建连接传 `connector=`。
- 代理继承依赖 `Transport` 保留 `proxy` 字段（`ws-transport/issues/01`，0.10.1）；没有它，`from_transport` 只能靠调用方手工再传一次 `proxy=`。
- 代理能力缺失时必须报错而不是直连。支持与否用 `inspect.signature(websockets.connect)` 判断，因为 `requirements.txt` 的下限是 `>=10.0`，而 `proxy=` 自 15.0 才有。
- 21 处模块级 patch 消失，假连接改为构造参数；WS 的 session / 心跳 / 重连测试第一次完全走公开接口。
- `connector` 无状态，socket 归 `WsBaseAsync` 独有，双重关闭随之消失。

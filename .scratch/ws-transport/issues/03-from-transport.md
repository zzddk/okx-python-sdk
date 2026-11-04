# from_client 改名 from_transport

Status: ready-for-agent
Release: 0.11.0

## 为什么

`from_client(client)` 名不副实：它靠鸭子类型吃 `API_KEY` / `API_SECRET_KEY` / `PASSPHRASE` / `flag` / `debug`，任何长得像的东西都能传（单测传的是 `SimpleNamespace`）。0.10.0 之后这些配置的唯一持有者是 `Transport`（ADR-0006），名字该跟着事实走。代理继承也需要一个明确的来源对象——见 `issues/01`。

## 做什么

`WsPrivateAsync.from_client` → `from_transport`；`WsPublicAsync.from_client` → `from_transport`。参数结构与现在一致，只是第一个参数改为 `Transport` 并做 `isinstance` 校验（与 `OkxClient.__init__` 同一风格，`okxclient.py:16-18`）。代理取自 `transport.proxy` 并交给 `WebSocketConnector`。不留旧名别名。

## 完成标准

1. `from_client` 在 `okx/`、`README.md` 与 `test/` 里全部消失（CHANGELOG 保留一行迁移说明）；传入非 `Transport` 抛 `TypeError`，信息里写明期望类型与实际类型。
2. README 的 WS 示例改为先建 `Transport`，再同时传给 REST API 类与 `from_transport`——旧示例传的是 API 实例，改名后必须改写法。
3. 主机选择：用 `Transport(http=…, flag='1')` 构造的实例，`WsPrivateAsync.from_transport(t).url` 是模拟盘私有主机；`flag='0'` 是正式盘。`WsPublicAsync.from_transport(t, channel='business')` 选 business 主机，非法 channel 仍抛 `ValueError`。
4. 代理继承：`Transport(http=…, proxy='http://p:8080')` → `from_transport` 得到的客户端，`await ws.connect()` 时底层拿到该代理。用例把 `okx.websocket.connector.websockets.connect` 换成**形参里带 `proxy` 的**假函数（能力探测读签名，见 `02` 第 8 条），断言收到 `proxy='http://p:8080'`。
5. `debug` 仍可显式覆盖；`debug=None` 时取 transport 的值。
6. `test_ws_config.py` 里的 `_rest_client()`（`SimpleNamespace`）删除，改用 `Transport(http=httpx.MockTransport(...))`：不建真实连接、不读环境代理。
7. 602 passed 不变；`test/` 下依赖凭据的集成用例仍按原样跳过（不新增失败，不改跳过条件）。

## 备注

与 ADR-0006 的一条后果冲突：那里写了「`WsPrivateAsync.from_client` 与既有的读取代码不必改」。ADR-0008 显式取代这一条，迁移说明写进 0.11.0 的 CHANGELOG。

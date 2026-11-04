# WS 代理支持

Status: needs-triage

## 为什么

`WebSocketFactory.connect` 只传 ssl context，没有代理入口。REST 侧有 `proxy=`，WS 侧没有，所以在必须走代理的环境里只能用 REST。

## 做什么

按 `websockets` 当前版本的代理参数实现，版本差异在工厂里吸收（与 `OkxClient` 处理 httpx 新旧参数的做法一致）。

## 完成标准

`WsPrivateAsync.from_client(client)` 能继承 REST client 的 `proxy`。

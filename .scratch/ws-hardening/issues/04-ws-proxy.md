# WS 代理支持

Status: wontfix
Superseded by: `.scratch/ws-transport/issues/01`（Transport 保留 proxy）、`02`（连接接缝）、`03`（from_transport 继承代理）

## 为什么

`WebSocketFactory.connect` 只传 ssl context，没有代理入口。REST 侧有 `proxy=`，WS 侧没有，所以在必须走代理的环境里只能用 REST。

## 做什么

按 `websockets` 当前版本的代理参数实现，版本差异在工厂里吸收（与 `OkxClient` 处理 httpx 新旧参数的做法一致）。

## 完成标准

`WsPrivateAsync.from_client(client)` 能继承 REST client 的 `proxy`。

## Comments

2026-11-05 — 拆进 `.scratch/ws-transport/`。这条验收标准在旧代码上无法实现：`Transport.__init__` 把 `proxy` 交给 `_make_http` 后就不保留（`okx/transport.py:44,58`），所以没有可继承的来源。新验收线见 `ws-transport/spec.md`。

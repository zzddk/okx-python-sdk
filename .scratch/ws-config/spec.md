# WS 配置对齐

让 WebSocket 层复用 REST 客户端的凭据与环境，而不是各配一套。

## 结论

不做配置对象（可复用的只有 3 个凭据字段 + debug，养不起一层抽象），做配置对齐。

## 范围

- **A. WS URL 常量**：`okx/consts/websocket.py`，正式盘与模拟盘各三条；`url` 改为有默认值。
- **B. `from_client()`**：`WsPrivateAsync.from_client(client)`、`WsPublicAsync.from_client(client, channel='public')`，取凭据 + `flag`，按 `flag` 选 live/demo 主机。

## 暂缓

- **C. 删除 `WsPrivateAsync.useServerTime`**：与 REST 0.4.5 修掉的是同一缺陷（参数还在、内部硬置 `False`），但删参数是签名变更，需要等破坏性窗口。见 `issues/02`。
- **WS 代理支持**：`websockets.connect` 的代理参数随版本变化，属于独立问题。

## 风险

URL 常量会随 OKX 换域名而过期，但这与 REST 的 `API_URL` 是同一模式；`url=` 始终可覆盖。

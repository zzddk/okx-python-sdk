# okxsdk

一个 OKX REST 与 WebSocket API 的 Python 客户端。这里的术语用来区分「凭据、参数、连接状态」这几组容易被混用的概念。

## Language

**凭据缺席（No credentials）**：
一个 REST 客户端或 WebSocket 会话在构造时没有被赋予可用于认证的凭据的状态。它是缺席，不是一个可发送的凭据值；跨过 Transport 到 WebSocket 会话的接缝时必须被识别为缺席，而不是被当作凭据传递。
_Avoid_: 空凭据、匿名、未登录、无鉴权、未设置参数

# 传输层内部化

Status: resolved
Done in: 0.10.0

## 为什么

见 `spec.md`。`OkxClient` 继承 `httpx.Client` 只借了一个构造函数：仓库里没有任何端点方法用 `self.get(` / `self.post(`，但每个 API 类的接口因此多出约 20 个 httpx 方法；`client=` 为了共享连接池复制 11 个字段，让外层的 `_send` / `_limiter` / `domain` 变成死代码。

## 做什么

新建 `okx/transport.py`，`Transport` 只暴露 `request(method, path, params, *, replayable=None)` 与 `close()`。`OkxClient` 不再继承 `httpx.Client`，改为持有 `Transport`；`_request`、`paginate`、9 个构造参数保持原签名。顺带修两个契约缺陷（见完成标准 12、13）和限流器的可测性（14）。

## 完成标准

### 前置

基线必须在没有代理变量的环境里跑：本机 `ALL_PROXY=socks5h://` 会让 133 个用例因缺 `socksio` 失败，与本次改动无关。

```
env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy \
    -u HTTPS_PROXY -u https_proxy python -m pytest test/unit
# 592 passed
```

### 形状

1. `issubclass(okx.okxclient.OkxClient, httpx.Client)` 为 False；`grep -rn 'import httpx' okx/` 只命中 `okx/transport.py`。
2. `Transport.request` 的 docstring 写明接口契约：None 表示不发送；GET 走查询串、POST 走 JSON body；`True`/`False` 序列化为 `'true'`/`'false'`；list/dict 参数内联 JSON；重试会重新生成时间戳与签名。

### 行为不变

3. 前置基线 592 passed，用例数不减少（改写不算删除）。
4. 契约测试 282 个用例全绿，每个端点仍发出原来的 (method, path)。
5. 默认构造不重试、不限流、`raise_on_error=True`。
6. 122 处 `patch.object(..., '_request_with_params')` 原样可用——`_request` 仍是它们最终落到的位置。

### 共享连接池

7. `TradeAPI(client=a)` 与 `AccountAPI(client=a)` 满足 `api._t is a._t`；用计数 http transport 断言两者共用一个 `httpx.Client`，而不是各建一个。
8. `client=` 只做 `self._t = client._t`，11 行字段拷贝消失；传入非 `OkxClient` 抛 `TypeError`（当前是 `AttributeError`）。

### 可测性

9. `ALL_PROXY=socks5h://127.0.0.1:1 pytest test/unit` 仍全绿：显式注入 transport 时 httpx 不再解析环境代理，这条锁住该性质。
10. 契约测试的 `_capture_requests` 去掉 `object.__new__`，改用 `cls(Transport(http=httpx.MockTransport(...)))` 或等价假 transport 构造实例，断言的仍是 (method, path) 与参数。
11. 12 处 `patch('okx.okxclient.Client.__init__')`（proxy / proxies 回退断言）改为对 `Transport` 注入的断言。`Client` 不再是基类后，这些 patch 不报错也不生效——必须改写，不能保留。

### 契约缺陷

12. 429/5xx + 非 JSON 响应体：可重放请求在 `max_retries>0` 下重发，最终抛 `OkxAPIException` 且 `status_code` 正确；不可重放请求只发送一次。用例：`MockTransport` 返回 429 + HTML，`max_retries=1`，断言被调用 2 次。（现状：`_send` 内抛的异常逃出了只捕 `TransportError` 的重试循环。）
13. `raise_on_error=False` + 200 非 JSON 仍抛 `ValueError`，这是 0.4.x 的既有行为，不改；但写进 `request` 的 docstring。
14. `RateLimiter` 的 sleep 可注入：加一个默认等于 `time.sleep` 的参数，限流用例不再真等秒数；对外行为不变。


## Comments

2026-11-05 — implemented. `okx/transport.py` now owns the HTTP policy and `OkxClient`
holds one `Transport`, exposing `request` (plus `close()`).
Verification (with 02 on top): `pytest test/unit` 602 passed, unchanged under
`ALL_PROXY=socks5h://127.0.0.1:1`; contract suite 282 passed. Every unit test now
constructs clients with an injected transport, so the suite never touches the proxy
environment or a real socket. Released as 0.10.0 (tag `v0.10.0`).

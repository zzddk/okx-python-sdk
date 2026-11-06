# 重试只对幂等请求生效

SDK 现在可以在 `_request` 层自动重试（`max_retries`，默认关闭）。但 `place_order` 这类 POST 在没有幂等键时的重试不是「再试一次」，而是「下第二单」——而且默认参数恰恰让这种调用最常见。

我们决定：**GET 一律可重试；POST 只在调用方提供了 `clOrdId`、`algoClOrdId` 或 `reqId` 时才可重试**，且只对瞬时故障重试（`httpx.TransportError`、HTTP 429/5xx、业务码 50001/50004/50011/50013）。参数错误、余额不足这类确定性拒绝永远不重试。

> Update (2026-11-06): ADR-0018 removed `50004` from this set; `50001` / `50011` / `50013` remain retryable. The replayability rule above is unchanged.

## Considered Options

- **所有请求都重试**：对一个交易 SDK 等于默认允许重复下单，这是最坏的一种「方便」。
- **只重试 GET**：安全，但会让「带 `clOrdId` 的下单在超时后重试」这种本来正确且必要的场景被迫由用户手写——而用户手写时不会重新签名、也不会判断可重试性。
- **按端点白名单**：需要为每个端点维护一个分类，随新端点增长必然腐化；幂等键是调用方本来就要传的东西，判断成本更低。

## Consequences

- 交易类调用想获得重试，必须传 `clOrdId`。这条要写进 README，否则用户会以为「开了 `max_retries` 就万事大吉」。
- 每次重试都重新生成时间戳与签名，避免重放已过期的签名（错误码 50102）。

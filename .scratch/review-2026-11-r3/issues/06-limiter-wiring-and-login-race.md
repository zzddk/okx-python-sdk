# 06 · 限流接线与并发登录

Type: task
Status: needs-triage
Blocked by: —

## Question

评审候选 06。两处没有被踩过的分支：

1. `okx/transport.py:122-123` 的 `self._limiter.acquire(path)` 覆盖率为 0；`RateLimiter` 类本身测得很细，但没有一个用例让 `request()` 在 `rate_limit=True` 下真的走一遍。删掉这两行，856 个测试仍全绿。
2. `WsBaseAsync.login()`（`okx/websocket/WsBaseAsync.py:259-300`）把 `self._handshake` 当共享状态写；两个并发 `login()` 会互相覆盖，先发起者等满 `DEFAULT_LOGIN_TIMEOUT`。

## 建议方案

1. 加请求级限流用例：`Transport(rate_limit=True)` + 注入 `sleep`，断言两次调用触发等待。
2. 登录复用 in-flight handshake（或加 `asyncio.Lock`），并发调用共享同一次握手；补一个 `asyncio.gather` 用例。

## 验收标准

1. `okx/transport.py:122-123` 不再漏测。
2. 并发两个 `login()` 只发送一个登录请求，且两者都返回成功。
3. 第二个 `login()` 在第一个失败后仍能重新尝试（不因锁卡死）。
4. `pytest test/unit` 全绿。

## 未决

- 锁的范围：只锁握手创建，还是锁整个 `login()`？后者更简单，但要验证 `_on_ready` 重入不会死锁。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 06。

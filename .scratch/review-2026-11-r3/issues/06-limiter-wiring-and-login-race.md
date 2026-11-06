# 06 · 限流接线与并发登录

Type: task
Status: resolved
Done in: 815b316
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

## Answer

**拍板（2026-11-06）**：锁整个 `login()`（懒创建、`stop()` 丢弃）；限流接线补请求级测试。

- 只锁「创建握手」不够：两个调用者仍可能各发一次 login；锁住整个尝试才能保证「并发只发一次」。
- `_on_ready` 是顶层调用者，不在另一把锁里，重入不会死锁；从回调里调用 `login()` 本来就会卡住读循环（ACK 进不来），不是这次引入的问题。
- 失败时锁释放，第二个调用者重新尝试（与「显式调用两次」语义一致）。
- 锁在首次 `login()` 时创建（运行中的 loop 内），`stop()` 置空，避免会话换 loop 复用旧锁。
- 限流：两个请求级用例证明 `request()` 每次尝试都 `acquire()`（含重试），不改运行时。

**验收对照**：并发两个 `login()` 只发 1 个登录帧、都返回 True；被拒时两个都拿到 `LoginRejected`（证明锁已释放）；871 passed / 313 subtests。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 06。
- 2026-11-06 施工完成：097e2ef（限流接线测试）、815b316（并发登录锁 + CHANGELOG）。两个并发用例在修复前均以 TimeoutError 红。

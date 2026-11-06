# 02 · 正常关闭不进 on_lost

Type: task
Status: needs-triage
Blocked by: —

## Question

评审候选 02。`okx/websocket/connection.py:232` 只捕获 `ConnectionClosedError`；真实服务器的正常关闭（1000/1001）走 `ConnectionClosedOK`，会直接穿透 `_read()`，既不调用 `_on_lost`，也不中断进行中的登录握手。

## 证据

复现（同一 `ConnectionSupervisor`，只换异常类型）：

```
ConnectionClosedOK    -> task raised ConnectionClosedOK    | on_lost calls: 0
ConnectionClosedError -> task raised ConnectionClosedError | on_lost calls: 1
```

`ConnectionClosedOK` 是 `ConnectionClosed` 的子类，不是 `ConnectionClosedError` 的子类。docstring（`connection.py:217`）却承诺「A closed connection is reported to on_lost」。

影响：正常关闭时 `LoginHandshake.wait()` 要等满 `DEFAULT_LOGIN_TIMEOUT`（10s）才抛 `TimeoutError`，而不是立即得到 `ConnectionError`。

## 建议方案

捕获基类 `ConnectionClosed`（或单独补 `ConnectionClosedOK`），让「自己停的」与「连接没的」成为唯一两种关闭语义；补一个 `ConnectionClosedOK` 的用例锁住 `on_lost`。

## 验收标准

1. `ConnectionClosedOK` 触发一次 `on_lost`，登录握手立即失败而不是等超时。
2. `reconnect=False` 下正常关闭的 task 结束语义有明确决定（正常返回还是抛异常），并有测试。
3. 新增用例，`pytest test/unit` 全绿。
4. docstring 与新行为一致。

## 未决

- `reconnect=False` 时正常关闭是否应视为「流结束」而不是错误？若保留正常结束，`_read` 需要返回结束原因，不能只放宽 except。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 02。

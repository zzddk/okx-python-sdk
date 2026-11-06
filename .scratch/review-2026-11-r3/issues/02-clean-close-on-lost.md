# 02 · 正常关闭不进 on_lost

Type: task
Status: resolved
Done in: a37e054
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

## Answer

**拍板（2026-11-06）**：捕获基类 `ConnectionClosed`，正常关闭同样进 `on_lost`；`reconnect=False` 时仍由 task 抛出 `ConnectionClosedOK`，不改成静默返回。

- 根因：`ConnectionClosedOK` 与 `ConnectionClosedError` 都是 `ConnectionClosed` 的子类；`_read` 只捕后者，正常关闭穿透，登录握手只能等满 10s。
- 关闭语义保持两种：`stop()` 主动关（不回报）；其余关闭回报 `on_lost` 并重抛。
- `reconnect=False` 保留「task 抛出关闭原因」：与 README 的 "the returned task surfaces the connection error" 一致，也避免把「服务器正常结束」与 `stop()` 混为一谈。要改成静默返回需让 `_read` 返回结束原因，属另一决定。
- 日志分级：正常关闭 info、异常关闭 error；`_supervise` 的 "stream ended" 同样按类型分级。

**验收对照**：登录中的正常关闭在 0.5s 内抛 `ConnectionError`（修复前是 `TimeoutError`）；`ConnectionClosedError` 路径不变；`reconnect=False` 的 task 语义有单独用例锁定；`pytest` 862 passed / 313 subtests。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 02。
- 2026-11-06 施工完成：a37e054（master）。新增两个用例（登录中正常关闭快速失败、reconnect=False 的 task 语义）；修复前第一个用例以 TimeoutError 红，修复后全绿。

# 05 · raise_on_error=False 的文档与行为相反

Type: task
Status: resolved
Done in: 7c3e7f1
Blocked by: —

## Question

评审候选 05。`README.md:117` 写「With `raise_on_error=False` nothing is retried」，但 `Transport.request` 对 `httpx.TransportError` 仍然重试；`_retry_allowed()` 只看 `replayable` 与 `max_retries`。实测 `max_retries=2` 时共 3 次尝试。`.scratch/rate-retry-policy/spec.md` 第 5 节写了同一句话。

## 证据

```
Transport(raise_on_error=False, max_retries=2)
  GET /api/v5/public/time -> ConnectError
  raised ConnectError | attempts: 3
```

`test/unit/okx/test_retry.py:121` 的用例名为 `test_raise_on_error_false_never_retries`，但只覆盖「业务码以 payload 返回」这一种情况。

## 建议方案

以代码为准改文档（行为合理：GET 重试安全，POST 仍受 `replayable` 约束）：

- README 与 spec 改为两句话：业务错误返回 payload、不重试；网络错误仍重试。
- 测试改名 `test_business_error_payload_is_returned_without_retry`。
- 新增「`raise_on_error=False` + 网络错误仍重试」的用例，把边界锁死。

## 验收标准

1. README 与 spec 不再写「nothing is retried」。
2. 两个用例分别覆盖业务码与网络错误的行为。
3. 不改运行时行为，`pytest test/unit` 全绿。

## Answer

**拍板（2026-11-06）**：以代码为准——`raise_on_error` 只决定「错误响应是抛还是作为 payload 返回」，不关闭网络错误的重试。

- 业务 / HTTP 错误且有 JSON body → 返回 payload，因此不重试（没有异常可分类）。
- `httpx.TransportError` → 仍走 `max_retries`；POST 仍受 `replayable` 约束（无幂等键不重放）。
- 不改代码：关掉网络重试会让 `max_retries` 失去一半价值，且 GET 重试是安全的；真正需要防的重复下单已由 `replayable` 拦住。
- 文档：README、`.scratch/rate-retry-policy/spec.md` 两处、`Transport.request` docstring 改为同一句话。
- 测试：`test_raise_on_error_false_never_retries` 改名 `test_business_error_payload_is_returned_without_retry`；新增 `test_network_error_is_still_retried`。

**验收对照**：867 passed / 313 subtests；变异检查（让 `_retry_allowed` 看 `raise_on_error`）只让新用例红；无运行时改动。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 05。
- 2026-11-06 施工完成：7c3e7f1（master）。README/spec/docstring 统一措辞；测试改名 + 新增网络重试用例；全量 867 passed / 313 subtests。

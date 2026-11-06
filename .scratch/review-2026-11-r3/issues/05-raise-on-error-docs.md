# 05 · raise_on_error=False 的文档与行为相反

Type: task
Status: needs-triage
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

## 未决

- 如果原意确实是「`raise_on_error=False` 完全不重试」，则改代码而不是文档；需要重新评估 GET 网络抖动只尝试一次的影响。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 05。

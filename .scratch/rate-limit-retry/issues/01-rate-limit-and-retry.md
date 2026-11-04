# 限流与重试

Status: resolved
Release: 0.6.0
Done in: 0.6.0

## 为什么

用户在各自的上层手写重试，而 `_request` 是唯一能正确做到的地方——只有它能在重试时重新生成时间戳与签名。限流同理：每用户每端点的配额，调用方并不知道。

## 做什么

见 `spec.md` 与 `docs/adr/0003-retry-idempotency.md`。

## 完成标准

- `pytest test/unit` 全绿，含重试与限流的单元测试。
- 默认构造行为与 0.5.0 逐字节一致（不重试、不限流）。
- 无幂等键的 POST 在任何错误下都只发送一次。

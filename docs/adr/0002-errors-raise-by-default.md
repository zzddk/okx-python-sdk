# 错误默认抛异常，而非返回错误 dict

`OkxClient._request` 无条件 `return response.json()`，从不检查 HTTP 状态码或业务码 `code != '0'`；`okx/exceptions.py` 里的三个异常类从未被抛出。结果是「订单被拒」和「下单成功」在调用侧看起来是同一种东西——都只是一个 dict。

我们决定：**HTTP 状态码 ≥ 400 或 `code != '0'` 时抛 `OkxAPIException`**，并提供 `raise_on_error=False` 退回旧的返回 dict 行为。

## Considered Options

- **保持返回 dict**：调用方每处都要写 `if resp['code'] != '0'`，漏写一次就是一次静默的错误处理。SDK 的边界是唯一该做这件事的地方。
- **两个都抛**：HTTP 层与业务层共用一个异常类型会让重试策略无法区分「网络抖动」与「参数被拒」。

## Consequences

- `OkxAPIException` 需要暴露 `code`、`message`、`status_code` 与原始 response，重试逻辑才能只对前者生效。
- 这是一处行为变更，随 0.5.0 发布（见 ADR-0001）。

# 限流与重试

在 `OkxClient` 里提供可选的请求重试与按端点限流。来源：设计评审后的第一批 0.6.0 特性。

## 决策

- **重试只对幂等请求生效**：GET 全部可重试；POST 仅在带 `clOrdId`/`algoClOrdId`/`reqId` 时可重试。见 `docs/adr/0003-retry-idempotency.md`。
- **限流元数据用旁表**：`okx/consts/rate_limits.py` 里的 `{path: (次数, 窗口秒)}`，端点常量保持字符串，不再开一次破坏性窗口。
- **配置走构造参数**：`max_retries=0`、`retry_backoff=1.0`、`rate_limit=False`，默认值与 0.5.0 完全一致，升级不改变任何行为。

## 范围外

- 分页迭代器：待本项落地后单独拆。
- WS 复用 REST 配置：暂不做——目前可复用的只有三个凭证字段，不足以支撑一层抽象。

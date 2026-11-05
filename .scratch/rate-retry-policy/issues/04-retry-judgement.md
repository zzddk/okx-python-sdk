# 04 · 重试判定是否改动

Type: grilling
Status: open
Blocked by: —

## Question

ADR-0003 锁了三条：GET 一律可重试；POST 仅在带 `clOrdId` / `algoClOrdId` / `reqId` 时可重试；只对瞬时故障（`httpx.TransportError`、HTTP 429/5xx、业务码 50001/50004/50011/50013）重试，每次重试重新生成时间戳与签名。逐项拍板是否改动：

1. 幂等键集合 `_IDEMPOTENCY_KEYS`（`okx/transport.py:29`）要不要扩充？依据是什么——OKX 官方文档还公布哪些幂等键？
2. `_RETRYABLE_CODES`（`okx/transport.py:25`）要不要增删？判据是什么（例如 429 与业务码重叠时的优先级）？
3. 「GET 全可重试」是否保持？有没有 GET 端点其实带副作用？
4. 要不要引入「按端点白名单」的补充判定？ADR-0003 明确否过这条路，若翻案要说明为什么现在条件变了。
5. 每一处改动是否构成公开面变化、要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`。

保持原状也是一个答案，但要写明「不改」的理由，别让它悬着。

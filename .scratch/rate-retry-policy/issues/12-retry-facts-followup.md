# 12 · 11 的事实要不要改重试判定

Type: grilling
Status: open
Blocked by: 11

## Question

由 [OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](11-idempotency-and-error-codes.md) 的事实回来后才拍板，问题现在已 sharp，故先建工单（blocked by 11）。[重试判定是否改动](04-retry-judgement.md) 已 resolved 并决定维持 ADR-0003 三条原状，按「一个决策只住一处」不重开 04；若 11 查出确凿遗漏或错误，由本工单承接。

要拍板：

1. 11 若查出官方还有别的幂等键：`_IDEMPOTENCY_KEYS` 要不要扩充？判据是什么——只收「官方明确列为幂等键」的，还是也收语义等价字段？`replayable=True` 逃生口是否足以替代扩充？
2. 11 若发现 `50001` / `50004` / `50011` / `50013` 里有确定性拒绝、或官方另有瞬时码：`_RETRYABLE_CODES` 要不要增删？`okx/transport.py:22-24` 的注释要不要一并改？
3. 11 若发现带副作用的 GET 端点：「GET 一律 replayable」要不要收紧？收紧的形状是什么（按端点例外表、还是要求调用方显式 `replayable`）？注意 ADR-0003 否过「按端点白名单」，翻案要说明条件变化。
4. 若 11 与现状一致、无遗漏：本工单直接关闭，并在地图 Out of scope 留一行，不留悬空工单。
5. 每一处改动是否构成公开面变化、要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`——由 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 统一判断归属。

只决策，不改 `okx/transport.py` / `okx/okxclient.py`。解本工单时先 zoom 11 的 Answer。

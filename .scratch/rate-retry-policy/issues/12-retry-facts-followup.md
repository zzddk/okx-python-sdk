# 12 · 11 的事实要不要改重试判定

Type: grilling
Status: resolved
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

> **来自 07 的输入（2026-11-06）**：[文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 定了 ADR / Migration 判据：本图不新建 0018、不改 ADR-0003、不写 `### Migration` 行；若本工单决定改动幂等键集合 / 可重试码 / GET 判定，届时按 `/domain-modeling` 三判据重新判断 ADR 与 Migration 归属，不重开 07。

> **来自 11 的输入（2026-11-06）**：[OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查](11-idempotency-and-error-codes.md) 已查明：① **50004 = 接口超时，官方明说「不代表请求成功或失败，请检查请求结果」**——`okx/transport.py:22-24` 的「rejected before it could be matched」无官方依据且对 50004 相反；② 即便带 `clOrdId`，它在 pending 内唯一、终态可复用，**不保证不重复下单**；③ 官方**没有**「可重试 / 不可重试」分类，也没有 429 与业务码的优先级说明（50011 同时出现 200/429；51115 是 429 + 确定性条件）；④ 255 个 GET 无一条被官方描述为改状态，但也未声明无副作用，唯一候选 `GET /api/v5/asset/deposit-address` 属推断。解本工单时先 zoom 11 的 Answer，**重点重评 50004 是否仍可重试**。

## Answer

重试判定已按 11 的事实重判（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：把「可重试」拆成三类，只对「处理前失败」自动重试；50004 与 51149（结果未知）一律不自动重试；`_IDEMPOTENCY_KEYS` 不扩充；GET 判定不收紧；这是行为变化，需要 ADR-0018。**

**事实基线（11 的官方原文）**：
- `50001` = HTTP 503「Service temporarily unavailable. **Please try again later.**」
- `50004` = HTTP 400「API endpoint request timeout.（**does not mean that the request was successful or failed, please check the request result**）」
- `50011` = HTTP 200/429「Rate limit reached. **Please throttle requests accordingly.**」
- `50013` = HTTP 429「Systems are busy. **Please try again later.**」
- `51149` = **HTTP 500**「Order timed out.（**does not mean … successful or failed, please check the request result**）」
- 另 50026 / 51054 / 52910 / 52911 / 52912 为 5xx；`51115` 是 429 + 确定性条件；`51000` 是参数错误。
- `clOrdId` 只在 pending 内唯一、终态可复用，**不保证 exactly-once**。

1. **`_IDEMPOTENCY_KEYS` 不扩充**。理由：官方没有「幂等键」定义；`attachAlgoClOrdId`、`clientId`、`clRfqId`、`clQuoteId` 虽存在，但官方都不声明去重；扩了只会扩大「以为安全」的错觉。术语写死：「幂等键」在本项目 = 「请求携带 client order id，服务端在 **pending** 期间据此拒绝重复」，**不是 exactly-once 保证**；`replayable=True` 仍是调用方的显式逃生口。
2. **`_RETRYABLE_CODES`**：**移除 `50004`**，保留 `50001` / `50011` / `50013`；**不新增**那 6 个 5xx 码（它们到达时 HTTP 就是 5xx，已被 `status >= 500` 覆盖，加进 code 白名单是冗余）。理由：官方对 50001/50011/50013 的措辞是「稍后重试 / 限流」，重试是官方建议；对 50004 明说「结果未知、请检查请求结果」，不该自动重放。
3. **「结果未知」拒重试集合**：新增 `_OUTCOME_UNKNOWN_CODES = {'50004', '51149'}`，在 `_is_transient` 里**先于** `status >= 500` 判断——命中就一律不重试（即使 HTTP 是 500）。理由：`51149`（Order timed out）官方同样说「结果未知、请检查」，但它是 HTTP 500，现状会被 5xx 规则重试，风险与 50004 同源（重复下单）。将来遇到同类码可以加入这个集合。
4. **注释改写**：`okx/transport.py:22-24` 的「rejected before it could be matched, so replaying it cannot double-execute」**对 50004 与官方原文直接冲突**（官方说结果未知）。改成：「50001 / 50011 / 50013 是官方建议稍后重试的处理前失败；50004 / 51149 是结果未知，不自动重试，调用方应先查请求结果」。注释是施工项，本工单不改文件。
5. **GET 判定不收紧**：保持「GET 一律 replayable」。理由：255 个 GET 无一条被官方描述为改状态；ADR-0003 已否过「按端点白名单」，翻案没有新证据；`GET /api/v5/asset/deposit-address` 可能创建地址只是从错误码 58310 反推、属推断，写进 spec 的「已知差异」；调用方仍可用 `replayable=False` 反向覆盖。
6. **公开面与 ADR**：Q2/Q3 是**行为变化**（对 opt-in `max_retries` 的用户：超时类错误不再自动重试）→ 进 CHANGELOG 的 `### Changed`，**不写 `### Migration`**（没有 API 签名 / 结构变化，用户不需要改代码）。按 `/domain-modeling` 三判据（难回退：交易 SDK 的失败语义变化；不看上下文会奇怪：为什么超时不重试；真有取舍：重试便利 vs 重复下单）**3/3 成立 → 需要 ADR-0018**。07 当时写「不建 0018」，但它也写了「若 12 改动则届时按三判据重新判断」，这是 07 预留的重判，不是翻案。
   - **ADR-0018 要点（handoff 落盘）**：标题「超时类错误不自动重放」；背景 = 11 的官方原文（50004/51149 结果为未知）；决策 = 只自动重试「官方建议稍后重试」的错误，结果未知的码（50004/51149）不重试，调用方先查结果；取舍 = 失去超时自动重试的便利，换取不重复下单；后果 = `_RETRYABLE_CODES` 移除 50004、新增 `_OUTCOME_UNKNOWN_CODES`、注释与 README 改写、CHANGELOG `### Changed`；与 ADR-0003 的关系 = 不推翻「只重试可重放请求」，只细化「哪些错误算可重试」。

## 边界

- **12 部分修订 04**：04 的「ADR-0003 三条全维持」在「可重试码」这一点上被本工单取代（04 自己写了「若 11 查出确凿遗漏由 12 承接」）——**不重开 04**，04 的 Answer 保持历史记录，地图索引补注「12 已改」。
- **07 的重判**：07 写「不建 0018」但预留了「若 12 改动则重判」；本工单按三判据判断**需要 ADR-0018**（要点在本文，handoff 落盘）。
- **不改代码**：12 只决策，`okx/transport.py` / `okx/okxclient.py` 的改动（移除 50004、加 `_OUTCOME_UNKNOWN_CODES`、改注释）是施工项；README / CHANGELOG 正文归 07 定的结构、由施工写。
- **收图**：12 resolved 后 14 张工单全部 resolved、fog 已清空，满足收图判据；`spec.md` 与 `ADR-0018` 属 handoff 交付物，本图不落文件。
- 不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理、未新建工单）。


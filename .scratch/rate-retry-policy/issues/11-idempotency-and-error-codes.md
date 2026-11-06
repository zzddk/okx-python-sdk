# 11 · OKX 官方幂等键、瞬时业务码与 GET 副作用端点核查

Type: research
Status: resolved
Blocked by: —

## Question

[重试判定是否改动](04-retry-judgement.md) 决定维持 ADR-0003 的三条判定原状，但 README.md:111 与 CHANGELOG.md:330 把 `_IDEMPOTENCY_KEYS`（`clOrdId` / `algoClOrdId` / `reqId`）与 `_RETRYABLE_CODES`（50001 / 50004 / 50011 / 50013）当既成事实陈述，没有出处；[OKX 官方限流文档的事实结构](01-okx-rate-limit-docs.md) 的 findings 只查了限流，没覆盖这些。把**事实**铺回来，作为「维持原状」这一决定的依据核实，以及 [11 的事实要不要改重试判定](12-retry-facts-followup.md) 的输入。只查证、不下结论、不替项目定改动：

1. OKX v5 官方是否公布过「幂等键 / 客户订单 ID」的完整清单？除 `clOrdId` / `algoClOrdId` / `reqId` 外还有哪些（例如批量下单、策略委托、提币、划转等场景的等价字段）？逐条给出来源。
2. 业务码 `50001` / `50004` / `50011` / `50013` 官方分别是什么含义？`okx/transport.py:22-24` 的注释称它们「rejected before it could be matched, so replaying it cannot double-execute」——这个解释与官方一致吗？
3. 官方是否还公布其他属于「瞬时 / 可重试」的业务码（例如服务繁忙、限流类）？CHANGELOG.md:330 举 `51000` 为「永不重试」的确定性拒绝，这个分类有官方依据吗？
4. 有没有 GET 端点其实带副作用或会改变服务端状态？ADR-0003 把「GET 一律可重试」当公理，需要核实这个前提。
5. HTTP 429 / 5xx 与业务码同时出现时，官方对优先级有没有说明（04 已确认代码现状是 429/5xx 优先）？

每一条结论追到拥有它的官方来源（OKX docs-v5 错误码页 / 端点详情 / Change Log），不引二手转述；查不到就写明，不要编造数值或 URL。**不回答**：该不该改集合、该不该翻白名单、要不要 ADR——那是 04 与 [11 的事实要不要改重试判定](12-retry-facts-followup.md) / [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 的决策。

## Context

findings 落在 throwaway 分支 `research/idempotency-and-error-codes` 上的 `.scratch/rate-retry-policy/research/idempotency-and-error-codes.md`；按 wayfinder 约定永不合并，沿用本地保留决定、不 push。本工单为 AFK research，被解时由 fresh-context 子代理调用 `/research`；charting 阶段之外不主动 fire。

## Answer

事实已由 AFK research 子代理查回，全文见 Context 段所指分支（commit `09aac54`，303 行）。**结论：官方没有「幂等键完整清单」、没有「可重试 / 不可重试」分类、也没有 429 与业务码的优先级说明；且 `okx/transport.py:22-24` 的注释「rejected before it could be matched」不是官方说法，对 50004 直接相反。**

**取证范围**：官方 `www.okx.com/docs-v5/en` 全文（5.28 MB）、中文版、Change Log、Best Practice 页，均用 curl 取完整 HTML 后解析；错误码表解析出 1,091 行 / 997 个不重复基础码，GET 路径 255 条。快照 2026-11-06；未用二手转述或镜像站。

1. **幂等键**：官方**没有**「幂等键完整清单」。「idempotency」字样只出现在 flexible-loan 借 / 还（明确 60 秒幂等键，重复分别返回 51016 / 51784）与 OKUSD 申购 / 赎回。除 `clOrdId` / `algoClOrdId` / `reqId` 外，官方还有 `attachAlgoClOrdId`、`clientId`（提币 / 划转 / 移动仓位 / 法币提币）、`clRfqId`、`clQuoteId`，但**都不声明去重**。另 Best Practice 页明写：标准订单的 `clOrdId` 只在 pending 内唯一、终态可复用——**即便带键也不保证不重复下单**。
2. **业务码含义**：50001 = 服务暂不可用（HTTP 503）；**50004 = 接口超时，官方明说「不代表请求成功或失败，请检查请求结果」（HTTP 400）**；50011 = 限流（HTTP 200 与 429 两条）；50013 = 系统繁忙（HTTP 429）。`okx/transport.py:22-24` 的注释「rejected before it could be matched, so replaying it cannot double-execute」**不是官方说法，对 50004 直接相反**——超时的请求可能已经到达并被执行。
3. **可重试分类**：官方**没有**「可重试 / 不可重试」分类。另公布 6 个 5xx 码（50026 / 51054 / 51149 / 52910 / 52911 / 52912）和大量「稍后重试」类 200 码。51000 = 参数错误，与「确定性拒绝」相容，但「永不重试」这个分类**无官方依据**；且 51000 的 HTTP 状态并非固定 400。
4. **GET 副作用**：255 个 GET 中**没有一条**被官方描述为改变状态；但官方也从未声明 GET 无副作用。唯一候选 `GET /api/v5/asset/deposit-address`——正文只说「获取（含历史地址）」，是从错误码 58310「无法创建新的充币地址」反推出可能创建，**属推断、非官方明文**。
5. **优先级**：**查不到**官方说明。业务码与 HTTP 状态是多对多（50011 同时 200/429；51115 是 429 + 确定性业务条件），说明 429 也不等于可重试；项目「状态优先」是本地策略，不是官方口径。

**未查到 / 未穷尽**：官方幂等键清单、可重试分类、优先级说明三者均不存在；未发真实请求（无凭证），429 响应体是否带 code 等运行时行为无法实证；错误码表为启发式解析（本文引用码已人工复核，但未逐个核对 997 个）；WS 错误码表、Agent / Broker 专页、历史版本未查。

**对 12 的输入（只陈述事实含义）**：① 50004 超时 = 结果未知，与「重放不会二次执行」的前提冲突；② 即便带 `clOrdId`，终态后复用也不保证去重；③ 官方没有可重试分类，所以 `_RETRYABLE_CODES` 的增删只能按「官方含义 + 项目策略」判断，没有现成清单可抄；④ 「GET 无副作用」官方未明文，但 255 个 GET 也无一条被描述为改状态。

## 边界（口径与事实含义）

- **11 是 AFK research，只铺事实** → 无公开面变化、不建 ADR、不写 `### Migration` 行；不回答该不该改集合、该不该翻白名单、要不要 ADR（归 04 / 12 / 07）。
- **不重开 04**：04 的 Answer 已明确「若 11 查出确凿遗漏，由 12 承接」。但 04 对 50004 的「rejected before it could be matched」依据已被证伪，**12 必须重评 50004 是否仍可重试**——这是 12 的核心输入，不是 11 的决策。
- **README / CHANGELOG / `okx/transport.py:22-24` 的陈述缺官方出处**：README.md:111 与 CHANGELOG.md:330 把两个集合当既成事实，`transport.py` 的注释还给出了一个不准确的理由；这些订正归 12 决定、由 07 / 施工落。
- **不收图**：11 resolved 后 open 只剩 12（`grilling`，blocked by 11 → 已解锁）；11 不代解、不触发第二个子代理。
- 本清单是**一次性事实输入**（10 已定），留在 throwaway 分支、不长期维护、不合并进 master；不改 `okx/` 代码、不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（AFK research，由 fresh-context 子代理调用 `/research` 完成；findings 落 `research/idempotency-and-error-codes` @ `09aac54`，本地保留、不 push）。


# 01 · 限流表的覆盖不变量

Type: grilling
Status: needs-triage
Blocked by: —

## Question

评审候选 01。限流表有 237 条，端点方法实际可达 273 条，差 36 条：4 条 batch-order 已在 `okx/consts/rate_limits.py:12-15` 的注释里说明是 orders-only，另 32 条既不在表里、代码里也没有说明。`RateLimiter.acquire()` 对未知路径直接返回（`okx/rate_limit.py:23-25`），所以 `rate_limit=True` 在这 32 条上是静默的空操作。

要定下：**这 32 条是补表、删掉，还是记成显式豁免？以及怎么让「表与可达集」的漂移以后不可能静默发生。**

## 证据

- 可达路径 273、表 237、缺失 36（用 `test/unit/okx/test_contract.py` 的 `ALL_API_METHODS` + `_capture_requests` 实测）。
- 缺失的 32 条中，`LIQUIDATION_ORDERS` 没有任何 API 方法；其余 31 条由公开方法派发，例如 `/api/v5/account/fixed-loan/*`（7 条）、`/api/v5/affiliate/tvb/*`（5 条）、`/api/v5/account/vip-loan-*`、`/api/v5/asset/deposit-lightning`、`/api/v5/market/block-trades`。
- `CHANGELOG.md:9` 写「the limits published for the endpoints this package exposes: 237 paths」，与实际不符。
- `test/unit/okx/test_rate_limits.py:10-11` 只断言「表 == 手工快照」，不绑定可达集。
- spec（`.scratch/rate-retry-policy/spec.md` 第 2 节）把 33 条「仅项目」路径称为「项目没有这个路径，不是豁免」，但代码里它们仍可调用。

## 建议方案

用 `test_contract.ALL_API_METHODS` 现成捕获器派生可达集，新增一张「路径 → 豁免原因」表，断言：

```
set(RATE_LIMITS) | set(EXEMPT) == reachable_paths
```

失败消息点名缺失路径。豁免只允许三类：orders-only（已有 4 条）、官方清单未收录（需注明证据）、无 API 绑定（当前只有 `LIQUIDATION_ORDERS`）。

## 验收标准

1. 测试能从代码派生可达集，不依赖第二份手工路径清单。
2. 缺一条表项或一条豁免，测试红，并打印路径。
3. 豁免表每行带原因；orders-only 的 4 条从注释迁进豁免表（或两边一致）。
4. `CHANGELOG.md:9` 与 `rate_limits.py` 的措辞不再声称覆盖全部暴露端点。
5. 不改运行时，`pytest test/unit` 全绿。

## 未决

- 32 条 project-only 路径的定性：官方漏列、已下线，还是路径写错？这决定豁免措辞是「未收录」还是「待删除」。
- 如果确认是错路径，删除它们会改变公开方法；按 ADR-0004 走 minor。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 01。

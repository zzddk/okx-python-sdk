# 删除端点的 None 分支

Status: resolved
Release: 0.14.0（原定 0.13.0）

## 为什么

见 `spec.md` 与 ADR-0010。`Transport` 已经丢弃 `None`，端点里 136 处 `if x is not None: params[x] = x` 只是把同一条规则再写一遍。

## 做什么

14 个端点 module：把 `params = {}` + 条件赋值合并成一个 dict 字面量；`MarketData.get_tickers` 的 if/else 合并；`SubAccount.reset_subaccount_apikey` 保留 `if ip != '-1'`、合并 `label` / `perm`。测试改用 `fakes.sent_params` / `fakes.assert_request` 断言实际发送的参数。

## 完成标准

1. `grep -rn "is not None" okx --include='*.py'` 不再命中端点里的 params 分支；剩下的只有 `SubAccount` 的 `ip != '-1'`、`Trade.cancel_algo_order` 的别名选择与 `Transport` / `utils` 自身。
2. 837 条线上请求（279 端点 × 3 组参数）与改动前逐字节相同，唯一差异是 `reset_subaccount_apikey` 的 JSON 键序。
3. `python -m pytest test/unit` 全绿，用例数不减少。
4. 每个端点形参都出现在 params dict 里（别名与 list payload 除外）。

## Comments

2026-11-05 — 已实现。134 处纯分支由脚本合并（按原有插入顺序，格式化后 ≤120 列），2 处手工（`get_tickers`、`reset_subaccount_apikey`）。51 个用例改为 `assert_request` / `sent_params`。`pytest test/unit` 639 passed。

# 修正 get_deposit_lightning 丢弃 ccy 与 amt

Status: resolved
Release: 0.13.0

## 为什么

`FundingAPI.get_deposit_lightning` 原样：

```python
params = {'ccy': ccy, 'amt': amt}
if to is not None:
    params = {'to': to}          # 覆盖整个 dict，而不是写入一个键
```

`to` 的默认值是 `""`，不是 `None`，所以默认调用永远走这一支：发给 `GET /api/v5/asset/deposit-lightning` 的查询串只有 `?to=`，`ccy` 与 `amt` 被丢掉。这是删除 None 分支时按 AST 扫描发现的，与本次重构无关，但修在同一个方法上。

## 做什么

```python
params = {'ccy': ccy, 'amt': amt, 'to': to}
```

## 完成标准

1. `get_deposit_lightning(ccy='BTC', amt='0.001', to='lnbc1...')` 发出的查询串包含三个参数。
2. 用例：`test/unit/okx/test_funding.py::TestFundingAPIDepositLightning`。
3. CHANGELOG 的 `Fixed` 记一条——这是本批唯一用户可见的行为变化。

## Comments

2026-11-05 — 已实现并加用例。线上请求比对中，该端点三组参数从 `?to=…` 变为 `?ccy=…&amt=…&to=…`，是预期差异。

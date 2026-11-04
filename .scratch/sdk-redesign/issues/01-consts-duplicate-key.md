# 修复 consts 重名常量覆盖

Status: resolved
Release: 0.4.5
Done in: 0.5.0

## 为什么

`GET_OPTION_TRADES` 在 `okx/consts.py` 中定义两次（第 118 行 market 端点、第 141 行 public 端点），后者静默覆盖前者。`MarketAPI.get_option_trades()` 因此实际请求了 `/api/v5/public/option-trades`，market 那个端点从 SDK 不可达。

## 做什么

给两个常量不同名字（按端点语义命名），修正 `okx/MarketData.py:131` 与 `okx/PublicData.py:124` 的引用。检查 `consts.py` 其余重名。

## 完成标准

两个端点各自可达；`grep -E '^[A-Z_0-9]+' okx/consts.py | sort | uniq -d` 无输出。

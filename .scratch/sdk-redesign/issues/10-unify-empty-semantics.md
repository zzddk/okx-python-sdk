# 统一空值语义

Status: ready-for-agent
Release: 0.5.0

## 为什么

两套约定并存：`''` 靠序列化器丢弃，`None` 靠手写 `if` 丢弃。`Account.py:104` 与 `Account.py:221` 是相邻的两种风格。list/dict 参数目前被 `str()` 成 Python repr 而不是 JSON。

## 做什么

统一为「只有 `None` 表示缺省，`''` 是合法值」；list/dict 序列化为 JSON 字符串。全仓改造并更新单测。

## 完成标准

同一模块内不再混用两种空值约定；传空串会真的发出空串参数。

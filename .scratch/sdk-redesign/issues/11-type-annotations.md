# 补类型注解与 py.typed

Status: ready-for-agent
Release: 0.5.0

## 为什么

全仓 0 个返回注解，无 `py.typed`，用户拿到的永远是裸 `dict`，IDE 无法补全。

## 做什么

补全公共方法签名注解，`okx/py.typed` 随包分发。不做 TypedDict/数据类模型——那层要跟着 API 版本变，维护成本远大于收益。

## 完成标准

`mypy okx`（或 pyright）在公共接口上无 error；安装后 IDE 能补全参数名。

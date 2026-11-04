# 子类构造收敛到基类

Status: ready-for-agent
Release: 0.5.0

## 为什么

22 个子类各写一遍相同的 `__init__`，把 8 个位置参数透传给 `OkxClient.__init__`（`Trade.py:9-11`、`Grid.py:6-7`…）。加一个 client 级选项要改 22 个文件，且 `domain` 与 `base_api` 已是同一件事的两个名字。

## 做什么

删除子类 `__init__`，由基类统一接收；新增 `client=` 注入参数供需要共享连接池的调用方使用。不改 `TradeAPI(...)` 的调用写法。

## 完成标准

`grep -rln 'OkxClient.__init__' okx/` 只剩基类；`TradeAPI(api_key=..., flag='0')` 仍可用。


## Comments

- 2026-11-05: done in 0.5.0. All 22 subclass constructors removed; `domain=` unified to `base_api=` (positional slot unchanged) and `client=` added for connection-pool sharing. `grep -rln 'OkxClient.__init__' okx/` now matches only `okx/okxclient.py`.

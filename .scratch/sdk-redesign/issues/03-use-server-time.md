# 处理 use_server_time 的死参数

Status: ready-for-agent
Release: 0.5.0

## 为什么

`OkxClient.__init__` 把 `self.use_server_time` 硬置为 `False`（`okx/okxclient.py:30`），传 `True` 静默无效；`_get_timestamp()` 因此是死代码，而该参数仍出现在 22 个子类签名里并标注 deprecated。

## 做什么

二选一：真正实现（取 `/api/v5/public/time` 校时）或从全部签名中移除。倾向移除——本地时钟漂移应该是使用方显式处理的事，且现有实现每次请求都要多打一次接口。选定的方向写进 CHANGELOG。

## 完成标准

参数不再静默失效；若移除，子类签名里不再出现 `use_server_time`。

## Comments

- 2026-11-05: 0.4.5 keeps the parameter and replaces the default-hidden `DeprecationWarning` with a visible `UserWarning`. Removal is deferred to 0.5.0 because deleting a constructor argument breaks callers.

## Comments

- 2026-11-05: done in 0.5.0 by removal. `use_server_time` is gone from `OkxClient.__init__` (and therefore from all 22 API classes); passing it now raises `TypeError`. Positional callers shift `flag` into the fourth slot, which is called out in the CHANGELOG. Removed the now-unused `SERVER_TIMESTAMP_URL` constant and updated integration tests and example notebooks.

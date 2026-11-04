# 处理 use_server_time 的死参数

Status: ready-for-agent
Release: 0.4.5

## 为什么

`OkxClient.__init__` 把 `self.use_server_time` 硬置为 `False`（`okx/okxclient.py:30`），传 `True` 静默无效；`_get_timestamp()` 因此是死代码，而该参数仍出现在 22 个子类签名里并标注 deprecated。

## 做什么

二选一：真正实现（取 `/api/v5/public/time` 校时）或从全部签名中移除。倾向移除——本地时钟漂移应该是使用方显式处理的事，且现有实现每次请求都要多打一次接口。选定的方向写进 CHANGELOG。

## 完成标准

参数不再静默失效；若移除，子类签名里不再出现 `use_server_time`。

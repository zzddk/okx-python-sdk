# 破坏性批次：删除 useServerTime 与硬编码的时间接口

Status: needs-triage
Blocked by: 0.9.0 窗口
Release: 0.9.0

## 为什么

`WsPrivateAsync.useServerTime` 是死参数（构造里硬置 `False`），与 REST 0.4.5 修掉的是同一缺陷；`WsUtils.getServerTime` 硬编码正式盘域名，删掉参数后成为死代码。

## 做什么

- 移除 `useServerTime` 参数与对应警告。
- 一并处理 `WsUtils.initLoginParams` 的 `useServerTime` 参数与 `getServerTime`。
- CHANGELOG 写明第四位位置参数已变化。

## 完成标准

`grep -rn useServerTime okx/` 无输出。

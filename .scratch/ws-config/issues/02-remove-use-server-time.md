# 删除 WsPrivateAsync 的死参数 useServerTime

Status: resolved
Done in: 0.9.0
Superseded by: .scratch/ws-hardening/issues/03-breaking-batch.md

## 为什么

`okx/websocket/WsPrivateAsync.py:15` 仍接受 `useServerTime`，但构造里 `self.useServerTime` 被硬置为 `False`，登录时永远用本地时间。传 `True` 只会拿到一条用户默认看不到的 `DeprecationWarning`。

这与 REST 侧 0.4.5 修掉的 issue 03 是同一个缺陷，当时只清了 REST 侧。

## 做什么

- 从签名中移除 `useServerTime`，删掉对应警告。
- `WsUtils.initLoginParams` 的 `useServerTime` 参数一并收敛。

## 为什么暂缓

ADR-0001 把破坏性改动集中到了 0.5.0，那扇门已关。不要为一个死参数单独再开一次。

## 完成标准

- `grep -rn useServerTime okx/` 无输出。
- CHANGELOG 里写明位置参数序的变化（`debug` 成为第五位）。

## Comments

- 2026-11-05: Closed with the 0.9.0 WebSocket batch; the same work is tracked in `.scratch/ws-hardening/issues/03-breaking-batch.md`. `useServerTime` and `getServerTime` are gone, `grep -rn useServerTime okx/` is empty, and the CHANGELOG records the positional shift.

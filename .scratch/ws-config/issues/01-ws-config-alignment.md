# WS 配置对齐（常量与 from_client）

Status: resolved
Release: 0.8.0
Done in: 0.8.0

## 为什么

`okx/` 里没有任何 WS URL 常量，用户必须记住正式盘 `ws.okx.com` 与模拟盘 `wspap.okx.com + brokerId=9999`；而 REST 侧环境是由 `flag` 决定的，WS 侧完全不认识它。

## 做什么

见 `spec.md` 的 A 与 B。

## 完成标准

- 不传 `url` 时默认正式盘。
- `from_client` 在 `flag='1'` 时选模拟盘主机，与 REST 环境一致。
- 显式 `url=` 覆盖一切推导。

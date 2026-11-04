# WS 加固

WebSocket 层从「能连上」做到「能长期跑」。盘点于 2026-11-04，共 13 项。

## 已修（0.8.1）

1. `isNotBlankStr` 用位运算 `~param.isspace()`，返回值恒为真 `-2`/`-1`，channel 校验从未生效
2. `WebSocketFactory.connect` 吞掉所有异常返回 `None`，真实原因丢失
3. `login()` 不读回执就置 `isLoggedIn = True`，密码错也当成功
5. README 声称有重连和复用连接，代码里没有
9. `subscribe` 里固定 `sleep(5)`，已随 3 一并去掉

## 0.9.0 本批

6. 无心跳：空闲约 30 秒后服务端断连，SDK 从不发 `ping`
7. `subscriptions` 是死状态，无一处读取——它本该是重连后重订阅的依据
8. 回调在事件循环里同步调用：慢回调阻塞整条流，抛异常直接终止 `consume` 且不可恢复
10. `WsPublicAsync` 与 `WsPrivateAsync` 394 行里约 90% 重复
11. WS 层 0 个类型注解（REST 在 0.5.0 已补齐）

6/7/8 必须一起做：重连要重订阅，重订阅要订阅集合，订阅集合要和回调生命周期对齐。10 跟着一起，否则重连逻辑要写两遍。

## 破坏性批次（0.9.0，见 ADR-0004）

12. 删 `WsPrivateAsync.useServerTime`（`issues/03`，与 `ws-config/issues/02` 同一条）
4. `WsUtils.getServerTime` 硬编码正式盘域名，随 12 一起删或改走常量

## 单列

13. 无 proxy 支持：`websockets.connect` 的代理参数随版本变化，与上面无关（`issues/04`）

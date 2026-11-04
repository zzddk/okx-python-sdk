# WS P0 修复

Status: resolved
Release: 0.8.1
Done in: 0.8.1

## 为什么

见 `spec.md` 第 1、2、3、5 条。四条里三条会让错误静默通过，一条是 README 与代码不符。

## 完成标准

- 空白 channel 会被 `checkSocketParams` 拒绝。
- 连接失败抛原始异常。
- 登录被拒抛 `ConnectionError`，无回执抛 `TimeoutError`。
- README 不再声称有重连。

# 破坏性批次：删除 useServerTime 与硬编码的时间接口

Status: resolved
Release: 0.9.0
Done in: 0.9.0

## 为什么

`WsPrivateAsync.useServerTime` 是死参数（构造里硬置 `False`），与 REST 0.4.5 修掉的是同一缺陷；`WsUtils.getServerTime` 硬编码正式盘域名，删掉参数后成为死代码。

## 做什么

- 移除 `useServerTime` 参数与对应警告。
- 一并处理 `WsUtils.initLoginParams` 的 `useServerTime` 参数与 `getServerTime`。
- CHANGELOG 写明位置参数序的变化：删掉 `useServerTime` 后 `debug` 成为第五位（`apiKey`、`passphrase`、`secretKey`、`url` 之后）。

## 完成标准

`grep -rn useServerTime okx/` 无输出。

## Comments

- 2026-11-05: Implemented for 0.9.0. `WsPrivateAsync.__init__` no longer takes `useServerTime` (nor the `DeprecationWarning`); the `self.useServerTime = False` shim in `WsPrivateAsync.__init__` is gone. `WsUtils.initLoginParams` dropped its first parameter and `getServerTime` was deleted along with the now-unused `httpx` import. Three tests existed only for the removed surface (two warning tests, one `getServerTime` test): 595 → 592 passed. CHANGELOG records the shift of `debug` to the fifth positional parameter.

# 统一日志与依赖

Status: resolved
Release: 0.5.0
Done in: 0.5.0

## 为什么

REST 层用 `loguru`，WS 层用标准 `logging`，同一 SDK 两套日志；`requests` 只为 `WsUtils` 取服务器时间而存在。

## 做什么

统一到标准 `logging`，`requests` 换成已有的 `httpx`，从 `requirements.txt` 移除 `loguru` 与 `requests`。

## 完成标准

`requirements.txt` 不含 `loguru`/`requests`；使用方的 logging handler 能收到 SDK 日志。

## Comments

- 2026-11-05: done in 0.5.0. REST and WS layers both use stdlib `logging`; `okx` installs a `NullHandler`. `WsUtils.getServerTime` uses `httpx`. `requirements.txt` now lists only `httpx[http2]`, `websockets`, `certifi`; the packaging test asserts exactly those three.

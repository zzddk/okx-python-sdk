# 共享 Transport 到 WS 会话配置的解析

Status: resolved
Release: 0.14.0（原定 0.13.0）

## 为什么

见 `spec.md` 与 ADR-0014。两个 `from_transport` 各写一遍 isinstance 校验、demo 判定、5 个字段拷贝；Transport 增加一个 WS 该继承的字段要改两个文件。

## 做什么

新增 `okx/websocket/config.py`（`require_transport` + `session_config`）；两个客户端各留一张 `_HOSTS` / `_CHANNELS` 表，`from_transport` 退成 1–3 行。

## 完成标准

1. `session_config(transport, hosts, url=None, debug=None)` 返回 6 个构造键；主机由 `hosts[str(transport.flag) == '1']` 选出。
2. `isinstance(transport, Transport)` 在 `okx/websocket/` 只出现一次（`config.py`）。
3. 两个客户端的公开签名、默认主机、代理规则、错误文案全部不变。
4. `test_ws_config.py` 17 → 23 条，既有用例不改即通过。
5. `pytest test/unit` 全绿。

## Comments

2026-11-05 — 已实现。`WsPrivateAsync.from_transport` 约 38 行 → 8 行，`WsPublicAsync` 约 48 行 → 12 行；新模块 58 行。`pytest test/unit` 822 passed。

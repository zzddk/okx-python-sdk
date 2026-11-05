# 登录协议收进 LoginHandshake

Status: resolved
Release: 0.14.0（原定 0.13.0）

## 为什么

见 `spec.md` 与 ADR-0012。登录回执被两条路径各自实现一遍：读循环结算 `_login_waiter`，`_read_login_ack` 自己 `recv` 并顺手投递非登录帧。判定、超时、投递三件事散在三处。

## 做什么

新增 `okx/websocket/login.py`（`LoginHandshake`）；`WsBaseAsync` 删掉 `_login_waiter` / `_read_login_ack` / `_login_rejection`，改为把帧喂给握手对象。

## 完成标准

1. `LoginHandshake` 的公开面就是 `is_ack` / `rejection` / `feed` / `wait` / `read` 五个。
2. `WsBaseAsync` 里不再出现 `event == 'login'` 的判定与 `no login acknowledgement` 的文案；grep 只命中 `login.py`。
3. 读循环路径与直连路径的行为不变：既有 `TestLoginThroughTheReader`、`TestSessionRestore` 不改即通过。
4. 新增握手单测 7 条 + 会话级直连投递 1 条，无需启动会话即可覆盖协议。
5. `pytest test/unit` 全绿；`ruff check okx/websocket/login.py` 无错误。

## Comments

2026-11-05 — 已实现。`WsBaseAsync` 505 → 473 行，新模块 102 行。`pytest test/unit` 814 passed（原 806，新增 8 条）。

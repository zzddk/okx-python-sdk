# 03 · WS 两处日志接入共享掩码

Type: task
Status: resolved
Done in: b63aa67
Blocked by: 01

## 为什么

`WsBaseAsync.py:292-298` 的 login 内联循环与 `:402` 的 `send:` 原样打印是两条独立日志行；`send:` 由公开 `send()` 触发，可携带手搓 login 帧或任意敏感 args，是目前唯一可泄漏凭据的未脱敏路径。R3·Q2 拍板给 `send:` 补掩码、`Received message` 不纳入（服务器帧不含 API 凭据，ADR-0020 的边界是「不落凭据」）。

## 做什么

- `WsBaseAsync.py` 新增 `from okxsdk import utils`（`login.py:27` 已有先例）。
- `login()` 的 debug 块改成 `logger.debug("login: %s", json.dumps(utils.mask_sensitive(json.loads(payload))))`，删掉内联元组与循环。
- `_send_payload()` 的 `send:` 日志改成打印 `utils.mask_sensitive(payload_dict)` 的序列化结果；**只掩日志副本**，实际发给 socket 的 `payload` 不变。
- 两处都保留 `if self.debug:` 守卫（ADR-0020:5）。
- `Received message` (`:197`) / `connection.py` / `connector.py` 不动。

## 完成标准

1. `send()` 的 debug 日志不含凭据值、含 `***` 与字段名；socket 收到的 payload 仍含真实值。
2. `login()` 的 debug 日志行为不变（既有掩码等价）。
3. `test_ws_hardening.py` / `test_login.py` / `test_ws_session.py` 既有断言不改即通过。
4. `pytest test/unit` 全绿；`ruff check` 全绿。

## Comments

- 2026-11-07 建单。与 02 同批落地。
- 2026-11-07 施工：`okxsdk/websocket/WsBaseAsync.py` 新增 `from okxsdk import utils`；`login()` 的内联 7 行掩码循环收成一行 `utils.mask_sensitive(json.loads(payload))`；`_send_payload()` 的 `send:` 改打 `json.dumps(utils.mask_sensitive(payload_dict))`，`await self._connection.send(payload)` 仍发原始字符串。两处 `if self.debug:` 守卫保留。`test_logging.py` 的线上帧断言（socket 仍含真实凭据值）通过，证明掩码只作用于日志副本。全量 864 passed, 336 subtests passed，`test_ws_hardening.py` / `test_login.py` / `test_ws_session.py` 既有断言不改即通过。

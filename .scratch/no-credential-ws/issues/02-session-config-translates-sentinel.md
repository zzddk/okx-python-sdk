# 02 · session_config 在接缝处翻译空值契约

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: 01

## 为什么

ADR-0014 把 `websocket/config.py:34-53` 定为 Transport→WS 映射的唯一 owner，但 `:48-50` 只逐字拷贝三个凭据字段。REST 侧「凭据缺席」是 `'-1'` 哨兵（`consts/http.py:23`，唯一解释点 `transport.py:149`），WS 侧是空串（`WsBaseAsync.py:81-83`），两套空值契约在接缝处对立。Q2 拍板用桥接：修复落在这个 owner 上，两个 WS 客户端同时受益，不动 `Transport` 的公开默认值与签名（ADR-0014:22 仍成立）。

## 做什么

- `config.py` 引入 `from okxsdk import consts`；`apiKey` / `passphrase` / `secretKey` 三个值等于 `consts._NO_CREDENTIAL` 时取 `''`，否则原样。
- 不动 `session_config` 的签名、参数、默认值、异常、url / debug / proxy 规则。
- 补 `test_ws_config.py::TestSessionConfig` 一条 guard 断言。

## 完成标准

1. `session_config(Transport(), HOSTS)` 三个凭据键均为 `''`；显式 stub 凭据原样不变（只对等于哨兵的值翻译，不误伤真实字符串）。
2. `test_ws_config.py` 既有 `TestSessionConfig` / `TestFromTransport` / `TestProxyInheritance` 用例一行不改即通过。
3. 工单 01 的 seam 主回归转绿（需与工单 03 同批落地）。
4. `pytest test/unit` 全绿。

## Comments

- 2026-11-07 建单。**单独落地本单会把响亮失败降级成静默失败**（`_needs_login()` 会变 `False`），必须与 03 同批。
- 2026-11-07 施工：`okxsdk/websocket/config.py` 新增 `from okxsdk import consts` 与 `_ws_credential(value)`（等于 `consts._NO_CREDENTIAL` 时取 `''`，否则原样），`session_config` 的三个凭据字段改走该 helper；module docstring 补上空值契约翻译的所有权。`session_config` 的签名、参数、默认值、异常、url / debug / proxy 规则均未动。`test_ws_config.py::TestSessionConfig` 补 `test_no_credential_transport_yields_empty_ws_credentials`。与 03 同批落地，`pytest test/unit` → 862 passed, 336 subtests passed。

# 03 · 拆开 must / can，凭据检查收回 login()

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: 01

## 为什么

`WsBaseAsync.py:324-328` 的 `_needs_login()` 用 `and _has_credentials()` 把「这个连接需要登录吗」和「有凭据能登录吗」混成一个 bool。工单 02 翻译后，私有客户端 `_needs_login()` 会变 `False`，`start()` / `subscribe()` 静默跳过登录——私有频道在未认证状态下订阅。Q1 拍板：必须认证却无凭据是错误，不是跳过登录的理由；Q4 拍板用 must / can 分离。

## 做什么

- `_needs_login()` 重构成 `_must_login()`：`(_LOGIN_REQUIRED or _ever_logged_in) and not _is_logged_in`，不看凭据。
- `_on_ready()` (`:227-228`) 与 `_ensure_login()` (`:330-332`) 都改用它；`_on_ready` 在 must 为真时调 `login()`，凭据检查由 `login()` (`:272-273`) 单点承载，沿用既有 `ValueError` 文案。
- **不新增抛出点、不新增异常类**：既有 `login()` 的 `if not self._has_credentials(): raise ValueError(...)` 就是唯一的凭据 owner。
- 更新 `test/unit/okxsdk/websocket/test_ws_session.py::TestNeedsLoginPredicate`：改名 `_must_login`；`(False,False,True,False)`、`(True,False,False,False)`、`(True,False,True,False)` 三行期望由 `False` 翻 `True`；加一条「must 且 !can → `login()` 抛 `ValueError`」断言。

## 完成标准

1. `WsPrivateAsync.from_transport(Transport())` 的 `start()` / `subscribe()` 抛 `"apiKey, secretKey and passphrase are required for login"`，且未发出登录帧。
2. `WsPublicAsync.from_transport(Transport())` 的公共频道行为不变；显式 `login()` 仍抛同一缺凭据错误。
3. `test_ws_session.py` / `test_ws_hardening.py` / `test_login.py` 既有断言不改即通过。
4. `pytest test/unit` 全绿。

## Comments

- 2026-11-07 建单。`_must_login` 是私有谓词，改名不算公开契约变更。
- 与 02 同批落地：`_on_ready` 开头已置 `_is_logged_in=False`，故每次连接 private 的 must 恒为真，凭据检查自然落到 `login()`。
- 2026-11-07 施工：`okxsdk/websocket/WsBaseAsync.py` 的 `_needs_login()` 改名 `_must_login()`、返回值去掉 `and self._has_credentials()`；`_on_ready()` 与 `_ensure_login()` 两处调用同步改名。`login()` 的既有 `if not self._has_credentials(): raise ValueError(...)` 成为唯一凭据 owner，未新增抛出点或异常类。`test_ws_session.py` 的 `TestNeedsLoginPredicate` → `TestMustLoginPredicate`，真值表 3 行期望由 `False` 翻 `True`，新增 `test_must_login_without_credentials_raises_from_login`；`test_ws_config.py` 新增 public 无凭据 guard（对应完成标准 2）。全仓 `grep -rn "_needs_login" okxsdk/ test/` 无残留。`pytest test/unit` → 862 passed, 336 subtests passed，`ruff check okxsdk/websocket/ test/unit/okxsdk/websocket/` All checks passed。

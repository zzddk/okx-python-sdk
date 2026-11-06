# debug 的边界：不落凭据、不改写全局 logger 级别

`debug=True` 目前把完整签名 header 与 login payload 写进日志：`okxsdk/utils.py:36,44` 打印 `OK_ACCESS_KEY` / `OK_ACCESS_SIGN` / `OK_ACCESS_PASSPHRASE`，`okxsdk/websocket/WsBaseAsync.py:296` 打印含 `passphrase` 与 `sign` 的登录帧。同时 `WsBaseAsync.py:134` 对模块级 logger 执行 `logger.setLevel(logging.DEBUG)`，把一个实例的配置变成所有实例的配置，且与 `okxsdk/__init__.py:9-11`「级别交给应用侧 handler」的约定冲突。

我们决定：**debug 只描述事件、不描述秘密；debug 是实例状态，不是全局 logger 状态。** 敏感字段（`OK_ACCESS_*`、`passphrase`、`sign`）在日志里打掩码；删掉 `setLevel`，各 debug 行沿用已有的 `if self.debug:` 守卫，日志级别由应用侧 handler 决定。

## Considered Options

- **保留字段名、值打掩码（拍板采纳）**：可排障又不泄密，日志形状变化最小。
- **只打事件名、完全不打值**：最安全，但 `debug=True` 的排障价值大幅下降。
- **删掉这几行 debug**：最省事，等于让开关失去意义。
- **保留 `setLevel` 但改成按实例 logger**：需要每个实例一个 logger 名，与「一个模块一个 logger」的现有结构冲突，收益不抵复杂度。

## Consequences

- `debug=True` 的日志内容变化（少一些字段值），属行为变更，CHANGELOG 记一条 Fixed；不改任何公开 API 签名。
- 依赖 SDK 自己把 logger 级别调到 DEBUG 的应用，需自行配置 handler 级别；这是与 `__init__.py` 既有约定对齐，不是新要求。
- `test/unit/okxsdk/test_logging.py` 补两条契约测试：日志不含凭据；实例间 logger 级别不串。
- 对应工单 `review-2026-11-r4/02`（2026-11-06 拍板取 A）。

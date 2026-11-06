# 让「凭据缺席」只有一个 owner

来源：2026-11-07 架构评审候选 01（`/improve-codebase-architecture`），经 `/grilling` 逐轮拍板 Q1–Q10。落地见 `.scratch/no-credential-ws/issues/`。

## 判断

`consts/http.py:23` 的 `_NO_CREDENTIAL = '-1'` 是 REST 侧「凭据缺席」的表示，`transport.py:149` 是唯一把它解释成「不发签名头」的地方。WS 会话侧用另一套契约：`WsBaseAsync.py:81-83` 三个凭据默认 `''`，`_has_credentials()` (`:314-315`) 用真值判断。

`websocket/config.py:48-50` 把 `Transport` 的三个凭据字段逐字拷进构造参数。ADR-0014 指定它是 Transport→WS 映射的唯一 owner，但它只搬值、不翻译。于是 `'-1'` 在 WS 侧不是「空」，而是三个合法凭据：

- `WsPrivateAsync._LOGIN_REQUIRED=True` → `_needs_login()` 为真 → `start()` 真的发出以 `'-1'` 为 HMAC 密钥的登录帧 → 服务器拒 → `LoginRejected` 从 `start()` 抛出。响亮但误导。
- `WsPublicAsync` 的 `start()` 静默正常，但显式 `login()` 会发垃圾帧；成功后 `_ever_logged_in=True` 会让重连反复重登。

**关键**：单独把 `'-1'` 翻成 `''` 不是修复。`_needs_login()` (`WsBaseAsync.py:324-328`) 把「需要登录吗」和「有凭据能登录吗」用 `and _has_credentials()` 混成一个 bool；翻译后私有客户端 `_needs_login()` 变 `False`，`start()` / `subscribe()` 一帧登录都不发、静默成功，私有频道在未认证状态下订阅。翻译必须和 must/can 分离一起落，否则是把响亮失败降级成静默失败。

删除测试：把「两套空值契约不同」这件事收进 `session_config` 一处后，下游所有 module 只面对一个空值契约，`_has_credentials()` 成为唯一解释者；复杂度不会摊给两个 WS 客户端（Public / Private 两个 adapter 共用同一 owner）。

## 目标形状

`websocket/config.py`（ADR-0014 的唯一 owner）：

- 三个凭据字段：值等于 `consts._NO_CREDENTIAL` 时翻成 `''`，否则原样。
- 签名、参数、公开接口、`from_transport` 全部不变。

`websocket/WsBaseAsync.py`：

- `_needs_login()` 重构为 `_must_login()`：`(_LOGIN_REQUIRED or _ever_logged_in) and not _is_logged_in`，不看凭据。
- `_on_ready()` 与 `_ensure_login()` 都改用它；凭据检查继续由 `login()` (`:272-273`) 单点承载，沿用既有 `ValueError` 文案 `"apiKey, secretKey and passphrase are required for login"`。
- 不新增抛出点、不新增异常类。

结果：`WsPrivateAsync.from_transport(Transport())` 的 `start()` / `subscribe()` 抛清晰的缺凭据错误，且不发出任何登录帧；`WsPublicAsync` 公共频道行为不变。

## 非目标

- 不改 `Transport.__init__` 的公开默认值、不统一成 `None`（触发 ADR-0004 破坏性批次）。
- 不新增异常类、不改 `_reconnect()` 的异常分类。
- 不清理 `SubAccount.py:17` 的 `'-1'`，也不动 OKX wire 惯例里 `-1` 的真实取值（市价等）；这两个概念与「凭据缺席」无关，见 ADR-0010 的 Update。
- 不单独发版、不动 CHANGELOG 版本：按 ADR-0004:15 攒入下一个以「WS 凭据契约」为主题的破坏性 minor。
- 不合并两个 `__init__`、不动主机表、代理规则与 debug 规则。

## 验证

基线（2026-11-07 落盘前）：`pytest test/unit/okxsdk/websocket/ test/unit/okxsdk/test_transport.py test/unit/okxsdk/test_okxclient.py -q` → **180 passed, 76 subtests passed**，全绿，印证「无凭据 → WS」路径无人测（`test_ws_config.py:25-27` 的 `_transport()` 永远传真凭据）。

三层测试（工单 01 先行，先红后绿）：

1. `test_ws_config.py::TestFromTransport` 主回归：无凭据 `Transport()` → 私有客户端 `start()` / `subscribe()` 抛缺凭据 `ValueError`；断言 FakeSocket 未收到登录帧。
2. `test_ws_config.py::TestSessionConfig` guard：`session_config(Transport(), HOSTS)` 三个凭据键为 `''`。
3. `test_ws_session.py` 真值表：`_must_login()` 下 3 行期望由 `False` 翻 `True`，另加一条「must 且 !can → `login()` 抛 `ValueError`」断言。

不变量断言：缺凭据错误只在首次连接 `_open()` (`connection.py:164-170`) 冒泡到 `start()`，不得进入 `_reconnect()`（`:212` 会把普通 `ValueError` 当瞬时失败无限退避）。当前因 `_task` 创建在 `_open()` 之后而不可达，以断言守住。

验收：`pytest test/unit` 全绿；`test_ws_config.py` 既有用例一行不改即通过。

## 风险

- 翻译与 must/can 分离必须同批落地，只做前者会引入静默未认证（工单 02、03 都 `Blocked by: 01`）。
- `start()` 从抛 `LoginRejected` 变为抛缺凭据 `ValueError`，属运行时行为变更；按 ADR-0004 需攒入破坏性批次并在 CHANGELOG 的 Migration 一段写完。
- GLOSSARY 的「凭据缺席」是领域术语，不写任何字面量；实现细节只留在 spec / ADR。

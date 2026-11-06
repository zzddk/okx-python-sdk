# 清掉会话上的死策略状态

来源：2026-11-07 架构评审候选 03（`/improve-codebase-architecture`），经 4 个只读复核子代理并行复核、用户拍板「只做 03 最小修复」。落地见 `.scratch/ws-policy-dead-state/issues/`。其余三候选的复核结论见 `docs/adr/0024-review-cards-are-hypotheses.md` 的「2026-11-07 补充」。

## 判断

卡片说「`WsBaseAsync.__init__` 是 13 参的 pass-through，5 个连接策略参数纯转发」「默认值有三个声明点」「让 factory 构造 supervisor 且不推翻 ADR-0016」。独立复核后：

- **计数**：`WsBaseAsync.py:79-93` 含 `self` 是 13、**调用方入参 12 个**；卡片自家 diagram 也只列 12 名。
- **「5 个纯转发」锐化**：这 5 个在 `WsBaseAsync.py:114-118` 被赋值成**死属性**（全仓 grep 只有这 5 行赋值、无读取），真正读取都在 `connection.py` 的 supervisor 上；会话还多转发一个 `debug`（`:131`→`connection.py:74`），共 6 个。策略参数在 `WsBaseAsync.py:126-130` 原样传给 `ConnectionSupervisor`。
- **「默认值三点」证伪**：数值字面量单点在 `connection.py:43-46` 的四个 `DEFAULT_*` 常量，两处参数表只是引用它们。唯一真重复是 `reconnect=True` 字面量两处（`connection.py:71`、`WsBaseAsync.py:88`）——它没常量。另 `WsPrivateAsync.py:39-55` 用 `**options` 透传、`WsPublicAsync.py` 根本无 `__init__`，「两个构造器各声明一次」也不成立。
- **卡片方案证伪（核心）**：`docs/adr/0016-ws-connection-supervisor.md:8` 明确把交接定为「构造时传 `on_frame`/`on_ready`」，`:25` 把测试接缝固定在 `FakeConnector`。factory 在 session 存在前拿不到绑定回调（`WsBaseAsync.py:123-125`），要让它造 supervisor 就得改 ADR-0016:8、两阶段构造或回调重绑；退而让 factory 只造策略值对象，则 `session.__init__` **必须新增**一个 `policy` 入参（12→8），接口未必收窄。
- **破坏性范围**：`README.md:177`、`CHANGELOG.md` 把 5 个参数写成公开调参项；≥20 处测试传策略 kwarg（`test_ws_session.py` 约 16 处、`test_ws_hardening.py:56`、`test_ws_public_async.py:292,305,317`）。改 `session_config` 的返回形状还会断 `test_ws_config.py:55-62` 的 dict 全等断言与 ADR-0014 的契约。
- **假接缝**：全仓仅一个 `ConnectionSupervisor`（`connection.py:54`）、一个构造点（`WsBaseAsync.py:120`），测试注入的是 `FakeConnector`（不是 supervisor），没有 `FakeSupervisor`、没有 `supervisor=` 注入。按「一个 adapter = 假接缝」，为 supervisor 引入注入 seam 无第二 adapter 支撑。
- **删除测试**：真删除只是 5 个死属性；5 个参数与默认值仍要在 supervisor 里声明、~20 处调用仍要传值——是「声明集中、使用搬家」，不是卡片说的 locality 从三点收成一点（数值上早已是一点）。

**结论**：候选 03 不作 deepening，退到**零签名最小修复**——删 5 个死属性 + 给 `reconnect` 补 `DEFAULT_RECONNECT` 常量，让两处默认值与其它四个 `DEFAULT_*` 一致。不动接口、不动 ADR-0016、不动任何测试调用点。05 / 06 / 07 判定不做 / 维持现状（理由见 ADR-0024 补充节）。

## 目标形状

`okxsdk/websocket/connection.py`：

- 在 `:43-46` 的常量组新增 `DEFAULT_RECONNECT = True`。
- `:71` 的 `reconnect: bool = True` 改为引用该常量。

`okxsdk/websocket/WsBaseAsync.py`：

- `:45-52` 的 import 组新增 `DEFAULT_RECONNECT`。
- `:88` 的 `reconnect: bool = True` 改为引用该常量。
- 删 `:114-118` 五行死属性赋值；`:126-130` 仍把 5 个策略参数原样传给 supervisor。

公开签名、默认值、运行时行为、测试调用点一律不变。

## 非目标

- 不改 `WsBaseAsync.__init__` 签名、不移除 5 个策略参数、不引入 factory / 策略值对象 / supervisor 注入。
- 不给 ADR-0016 写 Update、不改交接契约、不动 `session_config` 的 6 键 dict。
- 不动 README / CHANGELOG / 测试调用点、不发版、不走 ADR-0004 批次。
- 不实现 05 / 06 / 07（判定不做 / 维持现状）。
- 不回写已入库的评审报告 HTML。

## 验证

- **零行为变化、零签名变化**：删的是全仓无读取的死属性、补的是常量引用，因此**没有红→绿回归测试可写**（与候选 02 的不变量 guard 同类，但连 guard 都不必要）。
- 契约保证：全仓 grep 确认 `ping_interval` / `ping_timeout` / `reconnect` / `reconnect_backoff` / `reconnect_max_backoff` 在 `WsBaseAsync.py` 之外无对 session 实例的读取；`grep -rn "reconnect: bool = True"` 归零。
- 验收：`pytest test/unit` 与基线一致（865 passed, 336 subtests）；`ruff check okxsdk/ test/unit/` 全绿；`git diff` 只含 2 个生产文件，无测试改动。

## 风险

- 极小。唯一潜在影响：若有外部用户直接读 `ws.ping_interval` 等实例属性，删除会破坏它们——但这些属性未文档化（README 写的是**构造参数**，不是实例属性），且复核确认全仓无读取。

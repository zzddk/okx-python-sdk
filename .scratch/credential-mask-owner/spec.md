# 让「debug 不落凭据」的掩码只有一个 owner

来源：2026-11-07 架构评审候选 04（`/improve-codebase-architecture`），经 `/grilling` 三轮拍板（R1–R3 共 7 问）与 Q8 共识确认。落地见 `.scratch/credential-mask-owner/issues/`。

## 判断

ADR-0020 定下的边界是「debug 只描述事件、不描述秘密；debug 是实例状态，不是全局 logger 状态」：敏感字段打掩码、删 `setLevel`、各 debug 行保留 `if self.debug:` 守卫。r4 补了 REST 侧——`utils.py:13,16-22` 的 `_SENSITIVE_HEADER_KEYS` + `_masked_header()`，`test_logging.py:47-89` 有一条端到端契约测试。WS 侧另有 `WsBaseAsync.py:292-298` 的内联循环掩 `apiKey`/`passphrase`/`sign`。

报告卡片说「哪些字段算敏感有两个 owner」「为可测性抽出的纯函数仍带 debug、无 locality」「拿掉 debug 形参需重开 ADR-0020」。深挖后三条都站不住：

- 两份掩码是**同一策略的两种命名**（`OK-ACCESS-*` ↔ `apiKey/sign/passphrase`），不是两个策略；报告还漏了更严重的第三条——`WsBaseAsync.py:402` 的 `send:` 与 `:197` 的 `Received message` 未脱敏，公开 `send()` 可携带手搓 login 帧或任意敏感 args 原样打印。
- 「为可测性抽出的纯函数」**史实反了**：`b6cef36` 首个提交这三个函数就带 `print` 副作用，从未 pure；真正为可测性抽出的是 `_masked_header()`（`a464c12`）。`sign()` 倒是已 pure。
- 真正的开关是 `Transport.debug` 一个实例标志（`transport.py:150,151,153` 显式传值，`debug=True` 默认值包内从未被依赖）；「让 debug 决策只有一个 owner」**与 ADR-0020:5 直接冲突**（ADR 明确要求各 debug 行保留实例守卫）。另 `pre_hash` 与 `_send` 重复打印同一 body（`utils.py:33` / `transport.py:157`）。
- ADR-0020:16 的「不改公开签名」是那次行为修复的 Consequence 注记，破坏性签名变更归 ADR-0004 管；三个 utils 函数未被 `__init__.py` 导出、文档/迁移表不提、无测试断言签名，「公开 API」未经证明。
- 报告的 After 图把 login payload 画成经 `transport._send` 打印，但 `transport` 是 HTTP 层，永远看不到 WS 帧。

**结论**：候选不作 deepening。真实改进是零签名变更地落实 ADR-0020 已定的边界到漏掉的路径：`send:` 的 args 掩码 + 补 WS 侧零覆盖的契约测试 + 统一掩码 owner + 删重复 body 日志。删除测试也支持这个收窄：REST / WS 差异仅在字段命名与容器形状，只够证明一层共享掩码原语，不证明新 DEEP 模块；把 debug 决策一起收进来是复杂度搬家。

## 目标形状

`okxsdk/utils.py`：

- 一份统一敏感字段名清单，收编 REST 的 `OK-ACCESS-*` 常量与 WS 的 `apiKey/passphrase/sign` 字面量。
- 新增**模块级**纯函数 `mask_sensitive(value)`（不进 `okxsdk` 包级导出）：递归遍历 dict / list，命中清单的键把值换成 `***`，返回副本，不改入参。
- `_masked_header()` 保留为薄包装，内部改调 `mask_sensitive`。
- `pre_hash` / `get_header` / `get_header_no_sign` 的三个 `debug` 形参**保留且生效**（R2·Q1）；删 `transport.py:157` 的重复 `body:{body}` 行、保留 `utils.py:33`，使 `pre_hash.debug` 仍有实效、接口不说谎。

`okxsdk/websocket/WsBaseAsync.py`：

- 新增 `from okxsdk import utils`（`login.py:27` 已有先例）。
- `login()` 的内联掩码循环与 `_send_payload()` 的 `send:` 日志都改用 `utils.mask_sensitive`，各自保留 `if self.debug` 守卫。
- **只掩日志副本**，实际发送的 payload 一个字节都不改。

`Received message` (`:197`) 是服务器帧、不含 API 凭据，不在本次范围（R3·Q2）。`connection.py` / `connector.py` 的日志不动。

## 非目标

- 不删、不 no-op 三个 `debug` 形参，不进 ADR-0004 破坏性批次。
- 不重开 ADR-0020、不新建 `okxsdk/logging.py`、不把 debug 决策收成单处。
- 不治理 `Received message` / `connection.py` / `connector.py`。
- 不改任何公开签名、`__all__`、`_NO_CREDENTIAL`、consts 两份清单、12 参构造器。
- 不改 CHANGELOG（R3·Q3：Fixed 条目攒到发版时由主线程统一写进 `## [Unreleased]`）、不发版。
- 不回写已入库的评审报告 HTML（R1·Q2）。
- 不碰候选 02 / 03（按用户指令搁置）。

## 验证

基线（落盘后、实现前）：`pytest test/unit/okxsdk/test_logging.py test/unit/okxsdk/websocket/ -q` → **155 passed, 67 subtests**，全绿——`test_logging.py` 的唯一脱敏契约只走 REST POST，WS login 掩码零覆盖，`send:` 完全未脱敏。

回归测试（工单 01 先行，先红后绿）：

1. `send:` 主回归：`debug=True` 的 WS 会话，用含凭据的 args 调公开 `send()`，捕获日志，断言凭据值不在、`***` 在、字段名在。当前代码无掩码 → **红**。
2. login 不变量 guard：同一构造走 `login()`，断言同样三点。当前已正确 → 绿。
3. REST guard 不回归：`test_logging.py` 既有用例一行不改即通过。
4. 不变量断言：掩码只作用于日志副本，实际发出的 payload 仍含真实凭据值（防止为了不泄密把线上帧也改了）。

验收：`pytest test/unit` 全绿；`ruff check` 全绿。

## 风险

- `mask_sensitive` 递归遍历 `args`，若调用方传入恰好叫 `sign` 的业务字段会被掩（概率低，且与 ADR-0020「保留字段名、值打掩码」一致）。
- `send:` 掩码会改变 debug 日志内容，属 ADR-0020:16 说的「行为变更」，Fixed 条目待发版时补。
- 与候选 01 无交互：无凭据会话在 `login():272-273` 就抛 `ValueError`，早于 `:292` 的 debug 块；`config.py:_ws_credential` 也不触碰 login debug 路径。

# 05 · 「这条连接要不要登录」的谓词

Type: grilling
Status: resolved
Blocked by: 03

## Question

评审候选 05。「要不要登录」写在三个地方——`_LOGIN_REQUIRED`（:75）、`_should_login`（:107，首登后锁存）、`isLoggedIn`（:118，公开可写）——并由三个调用点各自组合（:265-268、:290-306、:438-443）；`login()` 里还要再校验一次凭证以避免调用点抛错。要定下：**这条规则落在哪个谓词上，三个调用点如何只问不判。**

需要一起定下的：

1. **谓词形状**：模块函数 `needs_login(client_type, credentials, logged_in) -> bool`，还是会话方法 `self._needs_login()`。
2. **锁存的归属**：「公共客户端登录后重连仍需登录」（:294）是真实需求，必须留在谓词里，不能退回只看 `_LOGIN_REQUIRED`。
3. **`isLoggedIn` 的可写性**：收成只读属性？先查 README/example/测试里有没有外部写入。
4. **三个调用点**：首连、重连、subscribe 前是否都收敛成同一句；`login()` 的二次凭证校验是否删除。
5. **与 03 的接口对齐**：若 03 让会话不再看到连接状态，谓词放在监督者还是会话；谁持有「本次是否已登录」。
6. **测试**：断言落在谓词上，覆盖三种客户端类型 × 凭证有无 × 已登录与否的真值表。
7. **ADR**：与 03 合写，还是单独一篇。


## Answer

**拍板（2026-11-05）**：这个问题由会话上的一个私有谓词回答，三个调用点只问不判。

**谓词**：`WsBaseAsync._needs_login() -> bool`，一行：`(self._LOGIN_REQUIRED or self._ever_logged_in) and not self.isLoggedIn and self._has_credentials()`。

**锁存改名**：`_should_login` → `_ever_logged_in`（初始 False，`login()` 成功后置 True）。它表达的是「这条会话曾经登录过」，而不是「本类要求登录」——后者是 `_LOGIN_REQUIRED`。

**调用点**：`_ensure_login()` 与 `_restore_session()` 都改成 `if self._needs_login(): await self.login()`。`_restore_session` 仍然先置未登录、丢弃旧连接的一次性请求，但不再依赖「上一行刚把 `isLoggedIn` 置 False」这个顺序成立。

**`isLoggedIn` 收只读**：内部 `_is_logged_in`，公开只读 property；写入只发生在 `login()`（True）、`stop()` 与 `_restore_session()`（False）。

**`login()` 的护栏保留**：已登录直接返回 True；缺凭证抛 `ValueError`。调用点现在不会误触它们，它们只服务直接调 `login()` 的用户；账户侧的唯一判断仍然只有谓词一处。

**记账**：不新写 ADR（0016 只记连接监督者边界）；`isLoggedIn` 变为只读进 CHANGELOG。

**完成标准**：
1. `grep -rn '_should_login' okx/` 无命中；两个调用点都只出现 `_needs_login()`。
2. `_restore_session` 里删掉对顺序的隐式依赖（先置位、再问谓词）。
3. 真值表用例（无需 socket）：私有/公开 × 曾登录/未曾 × 有凭证/无凭证 × 已登录/未登录，断言 `_needs_login()` 的期望值；重点锁住「公开客户端登录过后，重连仍要登录」。
4. `ws.isLoggedIn = True` 抛 `AttributeError`；测试里只保留读取。
5. 现有登录、重连、重放用例全绿；`pytest test/unit` 通过。

**被否的选项**：`login.py` 纯函数（四个布尔参数、三层转手，收益只是省掉无 socket 会话的构造）；公开 `needs_login`（没有消费者，`login()` 本身幂等）；删除 `login()` 的凭证护栏（直接调用者会得到服务端拒绝而不是本地错误）。

## Comments

- 2026-11-05 施工完成：3a6e1df（master）。全量 pytest 850 passed / 68 subtests；完成标准逐条核对见提交说明与 ADR-0016。
- 2026-11-05 评审补记：完成标准 3 要的是四种布尔的全表，施工只写了 8 格，缺「无凭证 × 曾登录」「有凭证 × 已登录」等组合。已补到 16 格（`test_truth_table`），锁存那条仍由 (False, True, True, False → True) 守住。

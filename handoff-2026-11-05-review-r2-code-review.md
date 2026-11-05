# Handoff — python-okx 2026-11-05 评审第二批（r2）两轴代码评审

- 日期：2026-11-05
- 仓库：/home/user/.adev/work/python-okx/python-okx
- 分支：master，HEAD = 02cfd55，工作区干净
- 评审范围：`v0.14.1(43f47d6)...HEAD`，42 个文件、+2465/−1405、7 个提交
- 规格：`.scratch/review-2026-11-r2/` 的 `map.md` + 工单 01–06（含各自 `## Answer`），加 `handoff-2026-11-05-review-r2.md` 的补记、`docs/adr/0004`、`docs/adr/0016`
- 状态：**只评审，未改任何代码**。本轮结论仅落在此文件，未纳入版本控制之外的任何工单。

## 本次完成了什么

在 `/code-review` 技能下对 r2 批次的 7 个提交做了一次两轴评审。Standards 与 Spec 各由一个全新上下文的子代理完成；主代理对下方标「已核实」的结论做了代码抽验（其余为子代理判断，未逐条复核）。Spec 子代理跑了全量 `pytest`：**850 passed / 68 subtests**。

## Standards 轴（9 条：1 硬违规 + 8 判断项）

### 硬违规

1. **可变默认参数回潮**，已核实。14 处 `Any = []`：
   `okx/BlockTrading.py:12,13,22,30,34`、`okx/Trade.py:152,173,206`、`okx/Grid.py:80`、
   `okx/SubAccount.py:56`、`okx/Account.py:137`、`okx/Finance/FlexibleLoan.py:15`、
   `okx/Finance/StakingDefi.py:16`。
   ADR-0001 第 3 行把「12 处可变默认参数」列为已修缺陷；工单 01 拍板改成 `= []` 时，
   没有按 `docs/agents/domain.md` 的「Flag ADR conflicts」提出这条冲突。
   注意这不是施工失误：决策是工单拍的，缺的是**把这次反转记进 ADR 或工单**。

### 判断项（基线坏味道，均为「可能的 X」）

- **主机双源**，已核实：`WsPrivateAsync.py:15` / `WsPublicAsync.py:14` 的 `_DEFAULT_URL`
  与 `_HOSTS` / `_CHANNELS['public']` 各自声明默认主机，与 ADR-0014 Consequences
  「主机表成了唯一的主机事实」相反。两处读的是同一个 `consts` 常量，重复的是**声明位置**
  而非字面值，故未按子代理的初判列为硬违规。
- **可能的 Duplicated Code**，已核实：`okx/websocket/connection.py:260` 与 `:269` 的
  `_stop_heartbeat` / `_stop_reader` 除字段外逐行相同，可收成一个 `_cancel(task)`。
- **可能的 Duplicated Code**：三份测试构造器 `test_ws_session.py:37,42`、
  `test_ws_hardening.py:20,25`、`test_ws_private_async.py:26` 各自拼 `FakeSocket`。
- **可能的 Duplicated Code**：`test/unit/okx/endpoints.py:429` 的 `DEFAULTED_COLLECTIONS`
  重复 `ENDPOINTS` 的参数名，且没有「所有 `= []` 都有行」的守卫，与 ADR-0011「一张表」
  形成第二个事实。
- **可能的 Primitive Obsession**：连接丢失用伪造 OKX 帧传递（`connection.py:229` 造
  `{"event":"error","code":"ConnClosed"}`，`WsBaseAsync.py:63` 反向解析），会话因此
  认识一个假协议帧，且该帧会落进用户回调兜底。
- **文档与事实不符**，已核实：`.scratch/review-2026-11-r2/map.md:11` 称评审 HTML
  「未纳入版本控制」，02cfd55 却把 `architecture-review-20261105-201639.html` 加进了仓库
  （`architecture-review-20261105-okx.html` 此前也已入库）。
- **次级**：`okx/pagination.py:81` 与 `:88` 各自取 callable 名；`CHANGELOG.md:5` 的
  Unreleased 段缺 `### Migration` 小节（0.14.0 / 0.10.0 / 0.9.0 都有）；
  `okx/websocket/WsBaseAsync.py:264` 的「未连接」前置检查与 `connection.py:134` 的
  `send()` 守卫重复，只是文案不同。

### 检查过、干净

AGENTS.md 与 issue-tracker/wayfinder 约定（目录、`NN-slug`、`Type:`/`Status:`、
`## Answer`/`## Comments`）、triage 标签；ADR-0005 串行与异常隔离、0009 六个纯方法 /
请求一次性、0010 端点无分支、0012 删 `read()` 与补记、0013 调用点抛错与文案、0016 边界
（`connection.py` 不 import `subscriptions`/`login`，首连也走 `on_ready`）；
README 两处新增与实现一致。ruff 只报格式与 `Dict` 类，按要求跳过。

## Spec 轴（7 条：3 缺失 + 2 范围外 + 2 可疑）

### (a) 规格要求但缺失／只做一半

1. **05 完成标准 3**，已核实。原文要求「私有/公开 × 曾登录/未曾 × 有凭证/无凭证 ×
   已登录/未登录」真值表；`test/unit/okx/websocket/test_ws_session.py:661` 的
   `test_truth_table` 只有 8 格，缺「无凭证 × 曾登录」等组合。关键那格
   「公开客户端登录过后重连仍要登录」有覆盖。
2. **map「交付注意 1」**：要求开工前按 ADR-0004 定 0.15.0 单批还是拆 patch；
   `handoff-2026-11-05-review-r2.md` 自述「尚未确认」，之后无任何落盘记录。
3. **04 完成标准 4**，已核实。原文写「改成 `patch('okx.websocket.WsBaseAsync.login_payload')`」，
   实际全仓无此 patch，改为断言 `payloads[0]["op"] == "login"`：目的达到，字面未做。

### (b) 规格没要求的行为

- `LoginHandshake.abort()` 与 `_is_connection_lost()` / 合成 `ConnClosed` 帧回灌
  `on_frame`：六张工单均未提，是施工自加的「握手—会话」契约。
- 02cfd55 同时带入了上一批的 `handoff-2026-11-05-python-okx-code-review.md`（92 行），
  本批规格未要求。

### (c) 看起来做了但可疑

- **01**：14 处 `= []` 把同一个 list 直接放进 `params`；`DEFAULTED_COLLECTIONS`
  只断言发出的值，区分不了「签名默认」与「默认 `None` + 方法体内归一化」，
  所以标准 1「方法体不含归一化」只能靠 grep 人工守。
- **03**：`stop()` 在派发中返回时已经 `_task = None`，会话随后才改 `_is_logged_in`、
  `drop_requests`；此刻若 `start()` 不被拦截，新旧监督者与读循环可能并存。

### 总判

01 / 02 / 03 / 06 逐条满足；04 差标准 4 的字面、05 差标准 3 的全表，其余无功能缺口——
六张工单**未做到逐条**满足，但缺口都在测试面，不是实现缺陷。

## 抽验记录（主代理）

| 结论 | 抽验方式 | 结果 |
|---|---|---|
| 14 处 `Any = []` | `grep -rn 'Any = \[\]' okx` | 成立，与清单一致 |
| ADR-0001 把可变默认参数列为已修缺陷 | `grep -n 可变默认 docs/adr/0001-release-strategy.md` | 成立（第 3 行） |
| `_DEFAULT_URL` 双源 | 读两个子类与 `config.py` | 成立，但两处同读 `consts`，降为判断项 |
| `_stop_heartbeat`/`_stop_reader` 重复 | 读 `connection.py:245-285` | 成立，逐行相同 |
| map 说 HTML 未入库 | `git ls-files \| grep architecture-review` | 成立，两个 HTML 都已入库 |
| 05 真值表 8 格 | 读 `test_ws_session.py:655-690` | 成立，8 条 case |
| 04 无 `login_payload` 的 patch | `grep -rn login_payload test/` | 成立，只在 `test_login.py` 直接调用 |
| 全量测试 | Spec 子代理执行 | 850 passed / 68 subtests |

## 下一步建议（按优先级）

1. **05 补全真值表**：8 → 16 格，纯测试面、风险最低，先做。
2. **决定 14 处 `= []` 的去留**：要么在 ADR（0017？）记下这次对 ADR-0001 的反转与理由，
   要么改回 `None` 哨兵；这是唯一硬违规，别让它悬着。
3. **定发版节拍**：0.15.0 单批还是拆 patch，写回 `map.md` 或本文件；同时给
   `CHANGELOG.md` 的 Unreleased 补 `### Migration`。
4. **主机双源二选一**：或删 `_DEFAULT_URL` 改由主机表派生，或在 ADR-0014 里承认这个例外。
5. **`ConnClosed` 合成帧**：要么写进 ADR-0005/0016 当成协议的一部分，要么换成显式信号，
   别让它既不是协议也不是内部事件。
6. `_stop_heartbeat`/`_stop_reader` 合并成 `_cancel(task)`；顺手把三份测试构造器收成一份。
7. `map.md:11` 的「未纳入版本控制」改成与事实一致；04 标准 4 要么补 patch 用例，要么改工单措辞。
8. `stop()` 派发中返回后紧接着 `start()` 的竞态：补一个用例，或在 `start()` 里显式拦住。
9. 63 个提交尚未推送；推送/开 PR 属于共享状态操作，需用户确认。

## 复用命令

```bash
cd /home/user/.adev/work/python-okx/python-okx
git log --oneline v0.14.1..HEAD
git diff v0.14.1...HEAD
git diff v0.14.1...HEAD -- okx/websocket/ okx/pagination.py
env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest -q
```

## 环境附注

- 仓库没有 `CODING_STANDARDS.md` 也没有 `CONTRIBUTING.md`，`pyproject.toml` 不存在；
  Standards 轴实际靠 ADR（0001–0016）与 `docs/agents/`，lint 走 `.github/workflows/ci.yml` 的 ruff job。
- `AGENTS.md` 与 `docs/agents/domain.md` 都指向根目录 `GLOSSARY.md`，该文件仍不存在（上一份评审已记录，未处理）。

## 建议下次调用的技能

- `tdd` —— 05 的真值表补格、03 的 `stop()/start()` 竞态用例，都适合先红后绿。
- `code-review` —— 修复后复跑两轴，基准点仍用 `v0.14.1`，可只审修复涉及的文件。
- `domain-modeling` —— 若决定为「连接丢失」建显式信号、或补 `GLOSSARY.md`。
- `pr` —— 若要推送 63 个提交并为 0.15.0 写 PR 正文（先取得用户授权）。

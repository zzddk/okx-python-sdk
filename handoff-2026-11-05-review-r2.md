# Handoff — python-okx 2026-11-05 评审第二批

- 日期：2026-11-05
- 仓库：/home/user/.adev/work/python-okx/python-okx
- 分支：master，HEAD = 43f47d6（tag v0.14.1）
- 状态：**决策已定，未施工**。本批只产出决策与工单，没有改动任何代码。
- 来源：`architecture-review-20261105-201639.html`（仓库根目录，未纳入版本控制）
- 地图：`.scratch/review-2026-11-r2/map.md`；工单：同目录 `issues/01–06`

## 六条决策

细节在各自工单的 `## Answer`，这里只做索引。

| 工单 | 决策 | 破坏性 |
|---|---|---|
| 01 必填集合字段 | 缺省值写进签名 `legs: Any = []`，删 14 处 `if X is None: X = []`；显式 `None` 回到「省略」 | 行为变化 |
| 02 翻页请求投影 | `paginate()` 整体投影；`before` 与 `params['limit']` 在调用点抛 `ValueError`；`params['after']` 保留为起点 | 行为变化（原本静默错数据） |
| 03 连接监督者 | 监督者独占 socket/读循环/心跳/退避/停止；删 `connect()/consume()`；ADR-0016 | 是 |
| 04 签名原语 | 只留 `utils.sign`；WS 拼装搬进 `login.py` 的 `login_payload()`；删 `WsUtils.py` 与 `utils.signature` | 是 |
| 05 登录谓词 | 私有 `_needs_login()`；锁存改名 `_ever_logged_in`；`isLoggedIn` 收只读 | 是（只读化） |
| 06 订阅表 | 保留序列入口但先全量校验；条目 `(arg, cb)`；删 `Subscription` 类与返回值 | 是 |

## 施工顺序建议

1. **02**：单文件、两个用例，先落地验证流程。
2. **01**：14 处机械替换 + 表驱动测试，独立。
3. **04**：删死代码与搬家，独立；注意 4 处测试把 `patch(...WsUtils.initLoginParams)` 改成 `patch(...login_payload)`。
4. **06**：订阅表内部重构，独立；会改写 `test_subscriptions.py` 的返回值断言。
5. **03**：最大的一张，单独排期；它的接口会决定 05 的落点。
6. **05**：与 03 同一区，建议紧接着做。

02/01/04/06 可并行；03 与 05 成对。

## 发版

按 ADR-0004 作为一批处理，建议 **0.15.0**：03、04、05、06 都有公开面变化，01 有行为变化，拆 patch 会让 CHANGELOG 与弃用说明分散。开工前确认这个判断。

## 交接注意

1. **登录握手死路径**：03 之后 `LoginHandshake.read()` 没有调用点；施工时顺手删，并同步 `test_login.py` 与 ADR-0012。
2. **文档面**：README 的 WS 示例不用改（`start/subscribe/stop` 不变）；CHANGELOG 需汇总 01–06；`docs/` 下凡出现 `WsUtils`、`connect()`、`consume()` 的说明一并更新。
3. **ADR 编号**：本批只写 0016（连接监督者）；04/05/06 明确不新写。
4. **不要改** `okx/SubAccount.py:19` 的 `ip != '-1'`：规格要求保留。

## 验证

```bash
cd /home/user/.adev/work/python-okx/python-okx
env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest -q
```

每张工单的 `## Answer` 都带「完成标准」，可作为该张的验收清单。

## 建议下次调用的技能

- `tdd` —— 02/01/06 都适合先红后绿。
- `diagnosing-bugs` —— 03 的重连与停止时序若出现死锁，用它定位。
- `pr` —— 一批做完后写 PR 正文（推送需授权）。
## 施工进度（2026-11-05 补记）

02 / 01 / 04 / 06 按 02 → 01 → 04 → 06 合入；03 与 05 作为一对最后完成（03 重写了会话与连接任务图，05 的谓词落在同一个文件里，故共用一次提交）：

| 工单 | 提交 | 要点 |
|---|---|---|
| 02 | 422adc0 | paginate() 内 _project() 整体投影；before / params['limit'] 调用点 ValueError；params['after'] 作起点 |
| 01 | ab0a840 | 14 处 is None → [] 删除，签名默认 []；test/unit/okx/endpoints.py 新增 DEFAULTED_COLLECTIONS 表 |
| 04 | e606dc9 | 删 WsUtils.py 与 utils.signature；login_payload() 落在 okx/websocket/login.py |
| 06 | 3de62d2 | 条目 (arg, cb)、删 Subscription；_require_routable 覆盖 add/remove，_require_channel 删除 |
| 03 | 3a6e1df | 新增 okx/websocket/connection.py（socket/读循环/心跳/退避/停止）；会话只剩发送、订阅、登录、路由；删 connect()/consume()；ADR-0016 |
| 05 | 3a6e1df | _needs_login() 一处谓词；_should_login → _ever_logged_in；isLoggedIn 收只读；真值表用例 |

- 全量：850 passed, 68 subtests passed；`git diff 43f47d6 --check` 干净。
- CHANGELOG 的 [Unreleased] 已汇总 01–06（含破坏性段）；README 的 Pagination 段补了 before/limit 拒绝说明，WS 段补了 start() 会先恢复会话。
- ADR：只新增 0016；ADR-0012 顶部加了「read() 已删除」的补记。
- `LoginHandshake.read()` 及其测试已删；测试替身收成一个 `FakeSocket`，全部经 `FakeConnector` 注入。
- 发版仍建议整批 0.15.0，尚未确认；master 未 push（本地领先 origin，tag 仍只到 v0.14.1）。

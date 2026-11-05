# Handoff — python-okx 0.14.0 两轴代码评审

- 日期：2026-11-05
- 仓库：/home/user/.adev/work/python-okx/python-okx
- 分支：master，HEAD = 9b86a0a（tag v0.14.0），工作区干净
- 状态：本地领先 origin/master 47 个提交（尚未推送）

## 本次完成了什么

在 `/code-review` 技能下对 `origin/master(06bb8a9)...HEAD(9b86a0a)` 做了一次两轴评审：
47 个提交、200 个文件、+8990/−4939。Standards 与 Spec 各由一个全新上下文的子代理完成，
主代理对关键结论做了代码抽验（下方标「已核实」的都是抽验过的）。

评审报告目前**只存在于本文件**，没有落盘到仓库。

## 评审结论

### Standards 轴（有效 7 条：1 硬违规 + 6 判断项）

硬违规
1. `README.md:43-48` —— 硬违规，已核实。同一节 66-91 行已改成 `AccountAPI(Transport(...))`，
   43 行仍用 `api_key=`/`api_secret_key=`/`passphrase=`/`flag=`/`debug=`；这些构造参数在 0.10
   就已删除（ADR-0006 / ADR-0015），照抄必抛 TypeError。
2. `okx/SubAccount.py:19` 的 `if ip != '-1'` —— **已核实为误报，不要改**。
   `.scratch/endpoint-params/spec.md:14` 与 `issues/01-drop-none-branches.md:12` 明确要求保留该分支。

判断项（基线坏味道，均为"可能的 X"，非硬性）
- `okx/websocket/WsBaseAsync.py:220` vs `:226-228` —— callback 兜底规则有两个落点（`_deliver` 与 `_emit`）。
- `okx/websocket/WsBaseAsync.py:130` —— `json.dumps(arg, sort_keys=True)` 重写了
  `okx/websocket/subscriptions.py:52` 的路由键 `_key`，而后者文档承诺与 0.11 重放键逐字节相同。
- `okx/websocket/WsUtils.py:18` —— WS 登录自建 hmac+base64，与 `okx/utils.py:14` 的 `sign()` 同形。
- `okx/websocket/subscriptions.py:45` —— `Subscription.params` 恒为单元素 tuple，`add`/`remove`
  返回的 tuple 无调用方使用（规格未要求的通用性）。
- `okx/websocket/WsBaseAsync.py:252` —— `login(timeout=10.0)` 与 `okx/websocket/login.py:22`
  的 `DEFAULT_LOGIN_TIMEOUT` 各存一份默认值。
- `test/unit/test_packaging.py:5` —— docstring 仍写 "ONLY the 5 runtime dependencies"，断言已是 3（:102）。

### Spec 轴（8 条：4 缺失 + 2 范围外 + 2 疑似做错）

缺失或只做了一半
1. `okx/websocket/WsBaseAsync.py:305` `subscribe` 无 channel 校验，`subscriptions.py:63` 的 `add`
   照收 `{'channel': ''}`；`.scratch/ws-hardening/issues/01-p0-fixes.md` 的「空白 channel 会被
   `checkSocketParams` 拒绝」在 `ws-routing/issues/03` 删除该 helper 后不再成立，且没有替代校验。
2. `README.md:43-48` 与 `example/.ipynb_checkpoints/get_started_en-checkpoint.ipynb` 仍是 0.10 前的构造方式
   （`.scratch/transport-seam/issues/02` 完成标准 #1）。
3. `.scratch/endpoint-table/spec.md` 要求「签名契约：位置参数顺序」，但
   `test/unit/okx/test_endpoint_table.py:53` 用 `**arguments` 调用，全局只有
   `test_account.py:113`、`test_trade.py:31` 两个方法断言了位置顺序。
4. `.scratch/ws-routing/issues/01..03` 仍为 `Status: ready-for-agent`，功能却已在 0.14.0 交付；
   最后一个提交 9b86a0a 只改了 `Release:` 字段。

范围外改动
- `architecture-review-20261105-okx.html`（28K 评审工件，无 spec 要求入库）。
- `example/.ipynb_checkpoints/...`（无 spec 要求维护 checkpoint）。

疑似做错
- `okx/websocket/WsPublicAsync.py:37-38` —— `cls._CHANNELS[channel]` 只捕 KeyError；`channel=[]` 抛
  TypeError 而非 ADR-0014 承诺的 ValueError（"异常类型与文案都不动"）。
- `okx/websocket/WsBaseAsync.py:327` —— `unsubscribe` docstring 承诺 "messages ... fall back to
  `callback`"，但 `callback` 形参完全未使用（0.9/0.10 的 `send()` 会设置 `self.callback`）。

### 附注
`AGENTS.md` 与 `docs/agents/domain.md` 都指向根目录 `GLOSSARY.md`，该文件不存在。

## 下一步建议（按优先级）

1. **修 README.md:43-48**（Standards 硬违规 + Spec 缺失同一处，用户可见、必崩）。改成
   `AccountAPI(Transport(...))`，与同节 66-91 行一致。
2. 决定 `WsPublicAsync` 非法 channel 的异常类型：要么恢复 ValueError 语义，要么改 ADR-0014 的措辞。
3. 给 `subscribe`/`Subscriptions.add` 补空白 channel 拒绝（先确认是恢复旧验收还是新建规格）。
4. 把 `.scratch/ws-routing/issues/01..03` 的 Status 从 `ready-for-agent` 改成 `resolved`，
   与同批其它 issue 一致（见 `docs/agents/triage-labels.md`）。
5. 清理 `test/unit/test_packaging.py:5` 的 "5 runtime dependencies"。
6. 判断坏味道是否值得动：路由键重复（第 2 条）风险最高，因为它有两份实现且其中一份是公开视图的契约。
7. 47 个提交尚未推送；推送/开 PR 属于共享状态操作，需用户确认。

## 复用命令

```bash
cd /home/user/.adev/work/python-okx/python-okx
git log --oneline origin/master..HEAD
git diff origin/master...HEAD
git diff origin/master...HEAD -- README.md okx/websocket/
env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest -q
```

## 建议下次调用的技能

- `code-review` —— 修复后复跑两轴，基准点仍用 `origin/master`，可只审修复涉及的文件。
- `tdd` —— 为 `WsPublicAsync` 异常类型与空白 channel 校验补测试时先红后绿。
- `domain-modeling` —— 若决定补 `GLOSSARY.md` 或把「订阅键」写成领域术语。
- `pr` —— 若要推送 47 个提交并为 0.14.0 写 PR 正文（先取得用户授权）。

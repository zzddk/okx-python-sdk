# 地图：2026-11-05 评审第二批（review-2026-11-r2）

> **已收图（2026-11-05）**：六张决策工单全部 resolved；开工前看「交付注意」，六条决策看「Decisions so far」。交接文档：仓库根目录 `handoff-2026-11-05-review-r2.md`。

## Destination

把 0.14.1 评审的六个候选从「候选」推到「可直接施工的决策」：每项定下接口形态与迁移策略，产出工单；地图内不改代码、不发版。

## Notes

- 评审源：`architecture-review-20261105-201639.html`（仓库根目录，未纳入版本控制）。候选编号 01–06 与上一批重名，本 effort 用 `review-2026-11-r2` 区分。
- 上一批（0.14.0）的 01–06 已全部落地，见 `.scratch/endpoint-params`、`endpoint-table`、`ws-login`、`pagination-seam`、`ws-session-config`、`client-config`；本图不重复计入。
- 所有工单都是 HITL grilling：按 `/grilling` 走，先讨论候选方案再拍板；每个会话只解一张。
- 拍板后若动公共契约，补 `docs/adr/`（当前最大编号 0015，下一张 0016）。
- 语言：中文；工单沿用 `.scratch/<effort>/issues/NN-*.md`，Answer 段追加在文件末尾。

## Decisions so far

- [01 · 必填集合字段怎么声明](issues/01-required-collection-fields.md)：缺省值写进签名（`legs: Any = []`），14 处 `if` 删除；显式 `None` 回到「省略」，不新写 ADR，行为变化进 CHANGELOG。
- [02 · 翻页请求的投影](issues/02-pagination-request-projection.md)：`paginate()` 整体投影，`before` 与 `params['limit']` 在调用点抛 `ValueError`；`params['after']` 保留为起点；不新写 ADR。
- [03 · 连接监督者的边界与接口](issues/03-connection-supervisor.md)：监督者独占 socket/读循环/心跳/退避/停止，会话经 `on_frame`/`on_ready` 相接；删 `connect()/consume()`，首连也走 `on_ready`；ADR-0016。
- [04 · 签名原语留一份](issues/04-signing-primitive.md)：只留 `utils.sign`；WS 拼装搬进 `login.py` 的 `login_payload()`，删 `WsUtils.py` 与 `utils.signature`；不写 ADR，公开面变化进 CHANGELOG。
- [05 · 「这条连接要不要登录」的谓词](issues/05-needs-login-predicate.md)：私有 `_needs_login()` 一处判断，锁存改名 `_ever_logged_in`；`isLoggedIn` 收只读；不写 ADR。
- [06 · 订阅表的条目形状与入口校验](issues/06-subscription-table-shape.md)：保留序列入口但先全量校验；条目 `(arg, cb)`，删 `Subscription` 类与返回值；校验覆盖 `add`/`remove`；不写 ADR。


## Not yet specified

（无——地图已收，剩余三件事转成「交付注意」。）

## 交付注意

收图（2026-11-05）时仍不作决策、留给施工的三件事：

1. **发版节拍**：破坏面已经明确——03 删 `connect()/consume()`、04 删 `WsUtils.py`、05 `isLoggedIn` 只读、06 删 `Subscription` 类与返回值、01 显式 `None` 的行为变化。开工前按 ADR-0004 决定 0.15.0 单批还是拆 patch；六张工单的完成标准里已经各自标明要进 CHANGELOG 的条目。
2. **登录握手死路径**：03 之后 `LoginHandshake.read()` 没有调用点，删除属于施工顺手，不单独决策；删了要同步 `test_login.py` 与 ADR-0012 的描述。
3. **文档面**：README 的 WS 示例不用改（`start/subscribe/stop` 签名不变）；CHANGELOG 汇总 01–06 的公开面变化；`docs/` 下凡出现 `WsUtils`、`connect()`、`consume()` 的说明一并更新。

## Out of scope

- `okx/SubAccount.py:19` 的 `ip != '-1'`：第三种「未设置」拼法，评审明确说规格要求保留，不在候选 01 内。

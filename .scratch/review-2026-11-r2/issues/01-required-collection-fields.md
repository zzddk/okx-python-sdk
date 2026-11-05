# 01 · 必填集合字段怎么声明

Type: grilling
Status: resolved
Blocked by: —

## Question

评审候选 01。ADR-0010 把「未设置」的解释收在 Transport（`None` = 省略），但端点里仍有 14 处把 `None` 改写成 `[]`，接口因此无法表达「必填」与「可选」的差别。要定下：**端点怎么声明「这个集合字段是必填的、调用方不传时要发 `[]`」？**

站点（评审列出的 14 处）：`okx/Account.py:138`、`okx/BlockTrading.py:14,16,27,29,39,45`、`okx/Trade.py:153,176,211`、`okx/Grid.py:82`、`okx/SubAccount.py:57`、`okx/Finance/FlexibleLoan.py:16`、`okx/Finance/StakingDefi.py:17`。`okx/Trade.py:127` 的 `data is None` 是另一类，不在内。

需要一起定下的：

1. **声明载体**：签名默认值（`legs: List = []`，Transport 保留默认值）／显式标记（`Annotated` 或模块级表）／包装类型（如 `RequiredList`）——哪种最不容易被下一个人绕过。
2. `None` 与「不传」是否继续同义。调用方显式传 `None` 时，是「省略」还是「发空数组」？
3. 行为差异是否算破坏性：现有调用方靠传 `None` 得到 `[]`，改后会少发字段。
4. 14 处如何一次验证：能否并进 `test/unit/okx/endpoints.py` 的表驱动测试（ADR-0011 的表）。
5. 是否需要 ADR（预计 0016）：这是 ADR-0010 的遗留执行，还是一个新决定。


## Answer

**拍板（2026-11-05）**：集合字段的缺省值写在签名上——`legs: Any = []`，方法体只保留 `'legs': legs`，14 处 `if X is None: X = []` 全部删除。

**None 的语义**：显式传 `None` 回到 ADR-0010 的全局含义「不发送」，与「不传」区分开。今天 `create_rfq(legs=None)` 发 `[]`、之后不发，是唯一的行为变化，记进 CHANGELOG，不新写 ADR。

**迁移清单**（14 处）：
`okx/Account.py:138` (`simPos`)、`okx/BlockTrading.py:14,16` (`counterparties`, `legs`)、`:27,29` (`rfqIds`, `clRfqIds`)、`:39` (`legs`)、`:45` (`legs`)、`okx/Trade.py:153` (`fromCcy`)、`:176` (`debtCcy`)、`:211` (`repayCcyList`)、`okx/Grid.py:82` (`recurringList`)、`okx/SubAccount.py:57` (`alloc`)、`okx/Finance/FlexibleLoan.py:16` (`supCollateral`)、`okx/Finance/StakingDefi.py:17` (`investData`)。

**完成标准**：
1. 上述 14 处的 `if … is None` 消失，签名默认值为 `[]`，方法体不含任何集合归一化。
2. 新增默认调用用例：对这 14 个方法以无参调用，断言发送的 params 里对应键为 `[]`（今天该分支 CI 覆盖为 0；端点表的哨兵字符串不会走到默认值）。
3. `create_rfq(legs=None)` 的发送参数不含 `legs` 键，用例锁住这条新语义。
4. `pytest test/unit` 全绿；`grep -rn 'is None' okx/` 不再命中这 14 处。

**被否的选项**：`utils.collection(legs)` 调用点归一（零行为变化，但签名不声明、14 处仍各写一次）；`request(..., collections=(...))` 表驱动（投影离开签名，Transport 多认识一个端点概念）；签名默认 `()`（`parse_params_to_str` 只对 list/dict 做 JSON 序列化，元组会在 GET 上变成 `%28%29`，把一个坑留给以后）。

**未决**：是否构成破坏性、进哪个版本，仍挂在 map 的「发版节拍」；本工单只定语义。

## Comments

- 2026-11-05 施工完成：ab0a840（master，合并入 0.15.0 未发布批次）。全量 pytest 853 passed / 46 subtests；完成标准逐条核对见提交说明与测试。
- 2026-11-05 评审补记：本条拍板反转了 ADR-0001「可变默认参数是缺陷」与 `.scratch/sdk-redesign/issues/04` 的完成标准，当初没有按 `docs/agents/domain.md` 报冲突。反转的理由、适用边界与「默认 list 不得就地修改」的约束见 ADR-0017；结论是保留 `= []`，不回退到 `None` 哨兵（那会重新让 `None` 有两种解释）。

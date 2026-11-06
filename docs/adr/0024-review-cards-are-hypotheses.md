# 架构评审候选是方向性假设，落地前必须深挖

`/improve-codebase-architecture` 产出的卡片描述的是摩擦方向，不是施工方案。2026-11-07 这批（`architecture-review-20261107-001928.html`）的 01 / 02 / 04 三个候选，方案都在独立复核后被推翻，且真实改进都比卡片写的更小。

我们决定：**任何评审候选在落盘前先做一次独立复核；复核推翻卡片方案时，以复核结论为准，不照抄卡片。** 复核结论与卡片的偏差记在各自的 spec 或本文，报告 HTML 保持当时的快照不回写。

## Considered Options

- **照卡片施工**：01 会把响亮失败降级成静默失败；02 会删掉已有的 ruff F401 守卫；04 会为史实错误的目标去动公开签名。
- **每次从头讨论而不记录**：成本重复，且这些否决理由正是未来 explorer 避免重提同一建议所需的信息。
- **直接改报告 HTML 修正卡片**：把静态评审产物变成需要持续同步的活文档，且与 ADR 用 `> Update (...)` 而非改正文的惯例不一致。

## Consequences

- **01（凭据哨兵）**：卡片的「把 `'-1'` 翻成空值」单独做会让 `_needs_login()` 变 `False`、私有客户端静默跳过登录。最终必须配 must / can 分离（`_must_login()` + `login()` 单点承载凭据检查）才成立。见 `.scratch/no-credential-ws/spec.md` 与 ADR-0014 的 Update。
- **02（收拢端点常量接线面）**：不作 deepening。卡片说的「两份清单无守卫、常量静默消失」被 ruff F401（漏改 `_MODULES`）与导入期 `NameError`（漏改 import）部分否定；「让 `_MODULES` 驱动导入」需动态导入，会撞 `consts/__init__.py:55` 的 `_NO_CREDENTIAL` 绑定——候选 01 刚让 `config.py` 依赖它，约束更紧——并删掉 F401 这层守卫。合并 20 个端点模块是复杂度搬家（524 处 `c.X` + 886 处裸名原封不动）。按产品区命名会动约 1400 处引用、需重开 ADR-0011。真实缺口只是「新增模块两处都不写」，应由一条契约测试封住。
- **04（掩码与 debug 决策归一）**：不作 deepening。「为可测性抽出的纯函数仍带 debug」史实反了（`b6cef36` 首个提交这三个函数就带 `print` 副作用）；「让 debug 决策只有一个 owner」与 ADR-0020:5「各 debug 行保留 `if self.debug:` 实例守卫」直接冲突；ADR-0020:16 的「不改任何公开 API 签名」是那次行为修复的 Consequence 注记，破坏性变更归 ADR-0004 管，且这三个 utils 函数未被公开导出或文档化。真实改进是零签名变更的掩码归一 + 补 WS 侧契约测试，见 `.scratch/credential-mask-owner/spec.md`。
- 卡片里的计数、批号（如 r3 07 被写成 r4）、史实都需复核，不可直接引用。

## 2026-11-07 补充：剩余四候选的并行复核

4 个只读复核子代理并行复核了 03 / 05 / 06 / 07，结论仍符合本文判断——卡片方案再次被推翻，且实现阶段**无法无条件并行**：05 与 07 改同一个 `okxclient.request` 签名且方向相反、06 与 05 撞 `Trade.py`、03 / 07 共享 ADR-0004 破坏性批次。用户据此拍板「只做 03 最小修复」。

- **03（连接策略构造器）**：收敛为零签名最小修复。「factory 造 supervisor 且不推翻 ADR-0016」不成立——ADR-0016:8 规定构造时传 `on_frame`/`on_ready`/`on_lost` 绑定回调，factory 在 session 存在前拿不到；5 个策略参数在 `WsBaseAsync.py:114-118` 是全仓无读取的死属性；「默认值三点」实为单点，唯一真重复是 `reconnect=True` 两处。另无第二个 adapter（`FakeSupervisor` 不存在），supervisor 注入 seam 是假接缝。落地见 `.scratch/ws-policy-dead-state/spec.md`。
- **05（request interface 说真话）**：**不做，维持现状**。「形状判别只活在测试约定」被 `transport.py:177` / `utils.py:101` 证伪；仓库无 mypy/pyright 配置、注解零消费面，改 `Union` 后没有任何测试会变红，收益≈0。卡片还漏列 `BlockTrading.py` / `Grid.py`。
- **06（统一导入写法）**：**不做，维持 r3 07 现状**。「依赖 02」完全证伪——02 判定不作 deepening、生产代码一行未改，且其 spec 明确把「不统一四种导入写法」列为非目标；06 就是 r3 07（`4477b5d`）明确延后的机械 lint 杂务，ruff 也没有强制「一种正面导入拼写」的现成规则，删除测试是纯文本替换。
- **07（删 replayable 逃生舱）**：**不做**。前提被证伪——`replayable=` 是 2026-11-06 刚复核决定保留、已写进 `README.md:121` 的公开接口，有 `True`（新幂等键例外）与 `False`（带副作用 GET 的 opt-out）两个明确用途；卡片把 `test_retry.py:170` 列为受影响是史实错误（该文件 0 处传 `replayable=`）。删它等于推翻一天前的取舍，且需 ADR-0004 批次与 Migration。

四份复核报告不单独落 spec，结论收在本节；报告 HTML 仍不回写。

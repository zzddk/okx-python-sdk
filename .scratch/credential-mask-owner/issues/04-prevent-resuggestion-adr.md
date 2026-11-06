# 04 · 防重提 ADR-0024

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: —

## 为什么

连续三个候选（01 / 02 / 04）的报告方案都被深挖推翻，且都收敛成更小的真实改进。未来架构评审看到 `consts/__init__.py` 的两份清单、或 `utils` 的三个 `debug` 形参，极易重新提出「DRY 重写」与「pure 化」。按 `ADR-FORMAT` 的「Rejected alternatives when the rejection is non-obvious」，这些 load-bearing 理由需要一处未来的 explorer 能看到的地方。

## 做什么

新增 `docs/adr/0024-review-cards-are-hypotheses.md`，记录：

- 评审卡片是方向性假设、不是施工方案；复核推翻时以复核结论为准。
- 02 被否决的理由：ruff F401 与导入期 `NameError` 已部分守卫两份清单；单清单驱动导入需动态导入、会撞 `consts/__init__.py:55` 的 `_NO_CREDENTIAL` 绑定（候选 01 又加重 `config.py` 对它的依赖）并删除 F401 守卫；合并 20 个端点模块是搬家不是集中；按区命名会动 ~1400 处引用。
- 04 被否决的理由：「为可测性抽出的纯函数」史实反了；「debug 决策一个 owner」与 ADR-0020:5 冲突；ADR-0020:16 的「不改公开签名」是那次修复的 Consequence 注记，破坏性变更归 ADR-0004 管；存在零签名变更的更简解。
- 01 的方案「翻译哨兵 → 空值」单独做会静默失败，最终配 must/can 分离才成立。
- 报告 HTML 保持快照不回写，修正落在各自的 spec / ADR。

## 完成标准

1. `docs/adr/0024-*.md` 存在，编号接续 0023。
2. 不改写任何既有 ADR 正文。
3. 与 `.scratch/credential-mask-owner/spec.md`、`.scratch/no-credential-ws/spec.md` 交叉引用一致。

## Comments

- 2026-11-07 随本次落盘直接完成，未单独提交。

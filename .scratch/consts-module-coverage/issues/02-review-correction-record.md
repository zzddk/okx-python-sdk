# 02 · 复核结论与 ADR-0024 交叉引用

Type: task
Status: resolved
Done in: 0d41ad3
Blocked by: —

## 为什么

Q2 拍板不回写已入库的评审报告，全部修正落进 spec 与 ADR。ADR-0024 在候选 04 那轮已写入 02 的完整否决理由（F401 守卫、动态导入撞 `_NO_CREDENTIAL`、删除测试、~1400 处引用），本轮只需交叉引用，不新增 ADR 编号。

## 做什么

- `spec.md` 记录事实修正（20 端点模块 / 22 `_MODULES` 名 / 279 导出）、F401 与 `NameError` 守卫、动态导入风险、删除测试结论、四种写法批号修正（r3 07 而非 r4）。
- 交叉引用 `docs/adr/0024-review-cards-are-hypotheses.md` 的 02 段落。
- 报告 HTML 保持原样，不修改。

## 完成标准

1. `spec.md` 的判断段覆盖全部复核结论，且与 ADR-0024:16 的 02 段落一致。
2. 未新增 ADR、未修改任何既有 ADR 正文、未修改报告 HTML。

## Comments

- 2026-11-07 随本轮落盘完成。

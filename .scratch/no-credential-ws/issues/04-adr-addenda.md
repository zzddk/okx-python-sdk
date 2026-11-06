# 04 · 两份 ADR 补遗

Type: task
Status: resolved
Done in: 512027b
Blocked by: —

## 为什么

Q6 / Q7 拍板：两个决定本身没被推翻，只是范围与措辞需要补记；仓库有 addendum 先例（ADR-0003:7 `> Update (...)`、ADR-0012:3 补记、ADR-0009:17「补充 ADR-0005，不取代它」），补范围不新开 ADR。Q3 的「`'-1'` 刻意保留」理由分散在 `.scratch/endpoint-params/spec.md:14`、ADR-0010:21、两轮 handoff 与前序评审四处，未来 explorer 需要一处能看到的地方。

## 做什么

- `docs/adr/0014-ws-session-config.md` 加 `> Update (2026-11-07): …`：`session_config` 的 owner 范围从「字段映射」扩到「字段映射 + 空值契约翻译」；决定与「公开接口不变」不变；指向本 spec 与 `GLOSSARY.md`。
- `docs/adr/0010-unset-arguments-dropped-once.md` 加 `> Update (2026-11-07): …`：澄清 `:7`「`None` 是唯一未设置值」只说端点形参；`SubAccount.py:17` 的 `'-1'` 是刻意保留的端点 unset 哨兵，与 `_NO_CREDENTIAL` 不同层、不同解释点、永不交叉；OKX wire 惯例 `-1` 是真实取值（如市价 `orderPx=-1`），不要做「去重所有 `-1`」的重构。

## 完成标准

1. 两份 ADR 均含 `> Update (2026-11-07)` 行，位于正文之后、`## Considered Options` 之前。
2. 不新增 ADR 编号、不改既有决定的正文。
3. ADR-0010 的补遗与 `.scratch/endpoint-params/spec.md:14`、`ADR-0010:21` 的既有记录一致。

## Comments

- 2026-11-07 随本次落盘直接完成，未单独提交。ADR-FORMAT 的「三条件」里，这两条满足「surprising without context」与「real trade-off」，但都是对既有决定的澄清，故以 addendum 而非新 ADR 承载。

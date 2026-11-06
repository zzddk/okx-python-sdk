# 05 · 懒创建 GLOSSARY.md，定名「凭据缺席」

Type: task
Status: resolved
Done in: 2026-11-07
Blocked by: —

## 为什么

`AGENTS.md` 与 `docs/agents/domain.md` 都指向根目录 `GLOSSARY.md`，两轮 handoff（2026-11-05）都记了「文件不存在，未处理」。本次 grilling 把「REST 侧哨兵 / WS 侧空串 / 跨接缝翻译」这组模糊概念磨清，正是 `docs/agents/domain.md:12` 说的「decisions actually get resolved」时刻；Q9 拍板懒创建。

## 做什么

- 根目录新建 `GLOSSARY.md`，按 `domain-modeling` 的 GLOSSARY-FORMAT 写单个 context。
- 只定义「凭据缺席（No credentials）」一个 term，含跨接缝的概念性约束；`_Avoid_` 列出「空凭据 / 匿名 / 未登录 / 无鉴权 / 未设置参数」。
- **不写** `'-1'` 字面量、文件名或实现规则——那是实现细节，留在 spec / ADR。GLOSSARY 不是 spec，也不记录实现决定。

## 完成标准

1. `GLOSSARY.md` 存在、devoid of implementation details、定义不超过两句。
2. `AGENTS.md` / `docs/agents/domain.md` 指向的文件不再缺失。
3. 未来评审若建议「清理所有魔法 `-1`」，能沿 ADR-0010 的 Update 找到反例。

## Comments

- 2026-11-07 随本次落盘直接完成。若后续要把「未设置参数」也定名，另开工单，不要塞进本单。

# 07 · lint 门是装饰

Type: grilling
Status: resolved
Done in: 4477b5d
Blocked by: —

## Question

评审候选 07。`.github/workflows/ci.yml:60-83` 的 lint 任务 `continue-on-error: true`，`pip install ruff` 不锁版本，只跑 `okx/` 且忽略 `E501`。当前 ruff 0.16.8 默认规则下：`okx/` 525 条、全仓 638 条、`ruff format --check` 有 115 个文件会重排。

要定下：**门要不要真的会关、规则集多大、格式化是否纳入。**

## 建议方案

分两步，避免一次开全套后又退回 advisory：

1. 锁 ruff 版本；规则选 `E4,E7,E9,F`（先抓 undefined name 与未使用导入），失败即红。
2. 再谈 `I` / `B` / `UP` 与 formatter。`from .consts import *` 的 F403/F405 先用 per-file-ignore 或显式导入处理。

## 验收标准

1. lint 失败会让 CI 红。
2. ruff 版本锁定，结果可复现。
3. `okx/` 在选定规则集下为 0；星号导入的处理方式写进配置注释。
4. 格式化的去留单独记录（做或不做都行，但不能悬着）。

## Answer

**拍板（2026-11-06）**：第一道门开 E4/E7/E9/F；19 个星号导入模块用 per-file-ignore；格式化暂不做。

- 规则集：语法 + undefined name + unused import + true/false 比较；`okx/` 下只剩 4 处 E712，已手改。
- 星号导入：只对实际使用 `from .consts import *` 的 19 个文件忽略 F403/F405（不是工单里写的 25，25 是 N999 的数量）。F821 仍全局生效；这些文件的常量拼写由契约测试兜底（它调用每个公开方法）。显式导入留作独立机械批次。
- 格式化：59/64 个文件会重排，单独一批，避免纯格式 diff 掩盖本次改动。
- 版本：`ruff==0.16.8` 同时锁在 `dev_requirements.txt` 与 CI；`continue-on-error` 删除，`--ignore=E501` 由 `ruff.toml` 接管。
- 范围：CI 仍只检查 `okx/`，`test/` 未纳入本道门。

**验收对照**：`ruff check okx/` 通过；stdin 注入 undefined name 会被报；同样内容只在被豁免的 API 模块里静默；871 passed / 313 subtests。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 07。
- 2026-11-06 施工完成：4477b5d（master）。新增 ruff.toml、锁版本、删 continue-on-error、修 4 处 E712；全量 871 passed / 313 subtests。

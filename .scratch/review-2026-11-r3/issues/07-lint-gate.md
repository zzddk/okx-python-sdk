# 07 · lint 门是装饰

Type: grilling
Status: needs-triage
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

## 未决

- 是否同时改掉 25 个 API 模块的星号导入？改成显式导入会扩大 diff，但能让 F 规则真正有效。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 07。

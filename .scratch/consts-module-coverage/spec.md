# 端点常量模块覆盖的契约守卫

来源：2026-11-07 架构评审候选 02（`/improve-codebase-architecture`），经 `/grilling` R1 拍板 Q1=A / Q2=不回写。落地见 `.scratch/consts-module-coverage/issues/`。

## 判断

报告卡片说「`consts/__init__.py:9-30` 的 import 块与 `:32` 的 `_MODULES` 是同一组 21 个名字的两份手写副本，没有任何测试守卫，新增 module 漏改 `_MODULES` 常量静默消失」，并建议「让 `_MODULES` 成为唯一清单并驱动导入」。独立复核后两条都站不住。

**事实修正**：端点模块 **20 个**（不含 `__init__.py`），`_MODULES` **22 个**（`http` + `websocket` + 20 端点），`__all__` / `_EXPORTS` **279** 个名字（261 个 `/api/` 字符串）；报告写的 21 / 21 / ~280 不可用。两份「清单」是 `:8` 与 `:9-30` 两条 import 语句（绑定 22 名）与 `:32`（引用同 22 名），集合相等、顺序相同。

**「无守卫、静默消失」被部分否定**：
- 只改 import、漏改 `_MODULES` → `consts/__init__.py` 不在 `ruff.toml:14-32` 豁免内，F401 生效。实测删 `account` 报 `F401 .endpoints.account imported but unused`。
- 只改 `_MODULES`、漏改 import → `:32` 直接 `NameError`，导入即崩。
- 全仓 `test/` 搜 `_MODULES` / `__all__` / `_EXPORTS` / `_collect_exports` / `dir(consts)` 零命中，故 F401 是 CI 的**偶然**守卫。真正无人守卫的只剩「新增模块两个清单都不写」——那是死代码，且报告自己的方案同样封不住。

**报告方案技术上不成立**：让 `_MODULES` 驱动导入必须换成字符串名 + `importlib`，而 22 个模块分属两个包（`okxsdk.consts` 与 `okxsdk.consts.endpoints`），一份清单不干净；还会删掉 F401 守卫，并撞 `:55` 的 `_NO_CREDENTIAL = http._NO_CREDENTIAL`（依赖 `http` 静态绑定、刻意不在 `__all__`）——候选 01 刚让 `config.py:44` 依赖 `consts._NO_CREDENTIAL`，约束更紧。`fc2ea46` 另立硬约束：`vars(consts)` 私有名不得含 `/api/`、循环变量留在函数作用域。

**删除测试**：合并 20 个端点模块后，279 个定义挤进一个文件，消费面（524 处 `c.X` + 886 处裸名 + `transport`/`utils`/`websocket` 的 `c.X`）原封不动——是搬家不是集中，谈不上 deepening。按产品区命名会动约 1400 处引用、需重开 ADR-0011 与 19 条 lint 豁免。

**四种导入写法**（14 相对 `import *` / 5 绝对 `import *` / 2 绝对具名 / 1 相对具名）是 `.scratch/review-2026-11-r3/issues/07-lint-gate.md`（`4477b5d`）明确延后的独立机械批次；报告写成「r4 审查 07」是批号错误，它与单清单正交。

**结论**：候选 02 不作 deepening（Q1=A）。真实缺口只有一条——新增端点模块两处清单都不写时静默。用一条契约测试封住，生产代码形状一点不动。`ADR-0024` 已完整记录上述否决理由，本轮不新增 ADR；报告 HTML 保持快照不回写（Q2），修正全部落在本文。

## 目标形状

`test/unit/okxsdk/test_contract.py` 新增 `test_every_declared_constant_is_exported()`：

- 复用既有 `_const_source_files()`（`:83-86`）与 `_const_assignments()`（`:89-96`）。
- 断言每个源文件里顶层声明的常量名都出现在 `vars(consts)`；缺失时列出 `文件:常量名`。
- 覆盖范围：`consts/http.py` + `consts/endpoints/*.py`（既有枚举边界）。`websocket.py` / `rate_limits.py` 不在枚举内——`RATE_LIMITS` 刻意不导出，扩进去会假阳性。

生产代码（`okxsdk/consts/__init__.py` 及全部端点模块）**一行不改**。

## 非目标

- 不做 DRY 重写、不引入动态导入、不删 `_MODULES`、不改 import 块。
- 不按产品区命名、不动 ADR-0011 快照表与 19 条 lint 豁免。
- 不统一四种导入写法（r3 07 的独立机械批次）。
- 不改 `:55` 的 `_NO_CREDENTIAL` 归属、不动 `__all__`、不动 `vars(consts)` 私有名约束。
- 不回写已入库报告 HTML、不新增 ADR（ADR-0024 已覆盖）。

## 验证

- 基线：`pytest test/unit -q` → 864 passed, 336 subtests。
- 新断言是**不变量 guard，当前即绿**（不同于 01/04 的红→绿主回归）：实跑 22 个源文件、274 个顶层赋值全部已在 `vars(consts)`，`missing = []`；`endpoints/__init__.py` 只有 docstring、endpoints 下无私有常量，无误报。
- 有效性已实证：临时新增未接线的 `consts/endpoints/_drift_probe.py`（含 `PROBE_UNWIRED_PATH`），guard 报 `constants declared but never exported: ['_drift_probe.py:PROBE_UNWIRED_PATH']` 并变红；探针随即删除，未留文件。
- 验收：`pytest test/unit` → **865 passed, 336 subtests**（基线 864 + 1 条新测试）；`ruff check okxsdk/ test/unit/` 全绿；`okxsdk/` 下生产代码一行未改。

## 风险

- guard 只覆盖 `_const_source_files()` 枚举的文件集；加在 `consts/` 根目录的新模块不会被抓到（既有枚举边界，本次不扩）。
- 若将来给端点模块加私有常量（`_` 前缀），`_collect_exports` 会跳过它、断言会假阳性，需在那时同步调整过滤规则。

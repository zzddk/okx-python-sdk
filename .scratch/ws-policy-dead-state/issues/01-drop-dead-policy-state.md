# 01 · 清掉会话上的死策略状态并补 reconnect 常量

Type: task
Status: resolved
Done in: ce3ceb6
Blocked by: —

## 为什么

`WsBaseAsync.py:114-118` 把 5 个连接策略参数存成实例属性，全仓 grep 只有这 5 行赋值、没有任何读取——真正读取都在 `connection.py` 的 `ConnectionSupervisor` 上。另 `reconnect=True` 是唯一没有 `DEFAULT_*` 常量、在两处参数表各写一边的默认值字面量（`connection.py:71`、`WsBaseAsync.py:88`）。候选 03 的卡片方案（factory 造 supervisor）经复核证伪，收敛为零签名最小修复。详见 `spec.md`。

## 做什么

- `connection.py` 在 `:43-46` 常量组新增 `DEFAULT_RECONNECT = True`，`:71` 改为引用它。
- `WsBaseAsync.py` 的 import 组新增 `DEFAULT_RECONNECT`，`:88` 改为引用它；删 `:114-118` 五行死属性赋值。
- `:126-130` 的 5 个策略参数仍原样传给 `ConnectionSupervisor`，一行不动。
- 不改任何签名、默认值、测试调用点、README / CHANGELOG、ADR-0016。

## 完成标准

1. 全仓 `grep -rn "reconnect: bool = True" okxsdk/` 归零；两处参数表都引用 `DEFAULT_RECONNECT`。
2. `WsBaseAsync.py` 不再给 `self.ping_interval` 等 5 个属性赋值；supervisor 构造调用不变。
3. `pytest test/unit` → 865 passed, 336 subtests（与基线一致，零行为变化）；`ruff check` 全绿。
4. `git diff` 只含 `okxsdk/websocket/connection.py` 与 `okxsdk/websocket/WsBaseAsync.py`，无测试改动。

## Comments

- 2026-11-07 建单。零行为变化，故无红→绿回归测试；验证靠全量不回归 + grep 契约 + ruff。
- 2026-11-07 施工：`connection.py` 加 `DEFAULT_RECONNECT = True`（`:47`）、`:72` 改引用；`WsBaseAsync.py` import 组加 `DEFAULT_RECONNECT`（`:49`）、`:89` 改引用、删 `:114-118` 五行死属性。验证：`reconnect: bool = True` 归零、5 属性无残留、`pytest test/unit` → 865 passed, 336 subtests passed（与基线一致）、`ruff check okxsdk/ test/unit/` All checks passed；diff 只含 2 个生产文件 + ADR-0024，无测试改动。

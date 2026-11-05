# 分页校验与行走同属 pagination

Status: resolved
Release: 0.13.0

## 为什么

见 `spec.md` 与 ADR-0013。cursor 校验在两处各写一遍，page 型端点的判定由客户端内省绑定方法；两个入口对同一个错误给出两种文案。

## 做什么

`okx/pagination.py` 拆成 `paginate()`（普通函数，校验后返回生成器）与 `_walk()`；`OkxClient.paginate` 只转发，`okxclient.py` 不再 import `inspect`。

## 完成标准

1. `grep -rn inspect okx/okxclient.py` 无命中。
2. 缺 cursor 在**调用点**抛出，不消费迭代器也算数（用例不调用 `list()`）。
3. 两个入口的 `ValueError` 文案相同，且都包含 callable 名。
4. page 型端点仍得到「call it directly with page=」的专门报错。
5. `pytest test/unit` 全绿，分页用例 16 → 18。

## Comments

2026-11-05 — 已实现。`pagination.paginate` 16 行拆成 `paginate` + `_missing_cursor_message` + `_walk`；`OkxClient.paginate` 22 → 9 行（含 docstring）。`pytest test/unit` 816 passed。

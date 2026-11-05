# 分页的校验与行走同属 pagination

分页有两个入口：`OkxClient.paginate(method, ...)` 与 `pagination.paginate(fetch, ...)`。前者先校验 cursor，再用 `inspect.signature(method).parameters` 判断这是不是 page 型端点（`get_announcements` 这类按页码翻页的端点，给一句专门报错），然后把剩下的活交给后者；后者又校验一遍 cursor——用另一套文案。

于是同一条规则有两份实现，同一个错误有两种说法，而「哪些端点按页码翻页」这个分页领域的事实，由客户端一次内省来回答。

我们决定：**校验与行走都由 `okx.pagination` 拥有**。`paginate()` 是普通函数，校验后返回生成器 `_walk()`；`OkxClient.paginate` 只做一行转发，签名不变。

## Considered Options

- **保留双校验**（客户端前置 + pagination 防御）：防御的是同一条规则，两份文案还会继续漂移；而且 page 判定仍然属于客户端。
- **校验留客户端，pagination 只行走**：page 判定需要端点对象，而 `pagination.paginate` 的入参本来就叫 `fetch`——规则跟一个不属于它的 module 走，只是把重复藏进「职责划分」。
- **删掉 `OkxClient.paginate`**：破坏性改动（0.14.0 的批次），而且没有解决规则该在哪里的问题，只是少了一个入口。
- **用显式标记替代 `inspect.signature`**（`_pages_by_number = True`）：去掉一次内省，代价是三个方法上各一条只对报错有用的约定。收益不够，留作以后内省真出错时的退路。

## Consequences

- **生成器必须拆开。** `pagination.paginate` 原本是生成器函数，校验写进去就变成惰性：`paginate(f)` 不报错，第一次 `next()` 才报。`.scratch/pagination/spec.md` 的完成标准要求「在调用点抛」，所以 `paginate()` 变成普通函数，行走留在 `_walk()`。用例不消费迭代器就断言异常，锁住这条。
- 两个入口的 `ValueError` 文案统一，都带 callable 名（`get_bills`）。异常类型与「调用点失败」的时机不变。
- `inspect.signature` 还在，但只剩一处；签名不可得的 callable 回落到通用文案，不会把 inspect 自己的错误漏给调用方。
- `OkxClient` 不再 import `inspect`，它只剩 `request` / `paginate` / `close` 三个转发与上下文管理。
- 行走语义一字未改：空页停、游标不推进停、短页继续、`begin`/`end` 原样透传。

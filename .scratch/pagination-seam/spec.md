# 分页契约收回 pagination

`OkxClient.paginate` 先校验再转发，`pagination.paginate` 再校验一次；「这是不是 page 型端点」靠 `inspect.signature` 判断，写在客户端里。来源：2026-11-05 架构评审候选 04。

## 判断

- **同一条规则两份**：客户端带方法名的 `cursor is required for X`，pagination 的通用 `cursor is required`。两个入口对同一个错误给出两种文案。
- **page 型端点是分页领域的事实，判断却在客户端**：`inspect.signature(method).parameters` 读的是绑定方法，而这个 module 的入参在有读循环的语境里叫 `method`、在没有的语境里叫 `fetch`——规则跟着一个不属于它的 module 走。
- **删除测试**：删掉客户端的校验，pagination 里那份还在——去掉的只是重复；删掉 pagination 那份，客户端的转发就得重新长出校验。规则只该有一份，位置应该在拥有行走的那个 module。

## 关键实现细节：校验必须前置

`pagination.paginate` 原来是生成器函数（函数体里有 `yield`），调用它一行代码都不会执行。把校验挪进生成器，会把「调用点失败」变成「第一次 `next()` 才失败」——`.scratch/pagination/spec.md` 的完成标准第 2 条正好禁止这件事。

所以拆成两层：`paginate()` 是普通函数，校验后返回 `_walk()`（生成器）。新增的 `test_missing_cursor_is_rejected_before_the_first_page` 不消费迭代器就断言异常，锁住这一点。

## 目标形状

```python
def paginate(fetch, cursor=None, params=None, page_size=100, max_pages=None):
    if not cursor:
        raise ValueError(_missing_cursor_message(fetch))
    return _walk(fetch, cursor, params, page_size, max_pages)
```

- `okx/pagination.py` 拥有：cursor 校验、page 型端点判定、行走。
- `OkxClient.paginate` 一行转发，签名不变（非破坏）。
- 两个入口的报错一致，都带 callable 名。
- `inspect.signature` 只剩一处；签名不可得的 callable（内建类型等）回落到通用文案，不让 inspect 自己的 `ValueError: no signature found` 漏出去。

## 非目标

- 不删 `OkxClient.paginate`：那是破坏性改动，要单独一个批次。
- 不改行走语义（空页停、游标不推进停、短页不停）。
- 不加「端点 → 游标字段」映射表：`.scratch/pagination/spec.md` 已经拒绝过，理由不变。
- 不加 `_pages_by_number` 标记：三个方法各写一行约定，换掉的只是一次内省，收益不够。

## 验证

- `pytest test/unit/okx/test_pagination.py` 16 → 18。
- 客户端用例不改逻辑即通过：缺 cursor 在调用点失败、逐页走、每页都过 `request`。
- `OkxClient` 不再 import `inspect`。

## 风险

- 直接调 `pagination.paginate` 的人会看到带方法名的新文案（异常类型仍是 `ValueError`）。
- `inspect.signature` 仍在，只是有了唯一归处；以后要换成显式标记，只改一个 module。

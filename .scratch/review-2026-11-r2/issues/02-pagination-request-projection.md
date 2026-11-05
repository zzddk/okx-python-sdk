# 02 · 翻页请求的投影

Type: grilling
Status: resolved
Blocked by: —

## Question

评审候选 02，也是评审的 top recommendation。`okx/pagination.py` 的 docstring 声明 `before` 不支持、`limit` 由模块决定，但 `_walk` 只 `pop('after')`，其余 `params` 原样转发（已核对：:61-68）。要定下：**一次合法的翻页请求长什么样，由谁投影？**

需要一起定下的：

1. `params` 里出现 `before`：抛 `ValueError`（在调用点，与 cursor 校验同风格）还是别的处理？
2. `limit` 优先级：显式 `page_size` > `params['limit']` > 默认 100？还是 `params['limit']` 一律拒绝？
3. 投影落点：`paginate()` 还是 `_walk()` 入口——ADR-0013 要求「在调用点抛」，落点要满足它。
4. `after` 由模块接管后，调用方传 `params={'after': ...}` 是继续沿用还是拒绝？
5. 测试补哪两个用例（`before` 拒绝、`limit` 优先级），加在 `test/unit/okx/test_pagination.py`。
6. 是否记 ADR：评审说这是 ADR-0013 的收尾，需要确认「不需要新 ADR」这个判断。


## Answer

**拍板（2026-11-05）**：一次翻页请求由 `paginate()` 整体投影，`_walk()` 只接收已经合法的输入。

1. **`before` 拒绝**：在 `paginate()` 抛 `ValueError`，与 cursor 校验同一落点、同一时机（不消费迭代器也报）。文案带 callable 名并指方向：`before is not supported by paginate(fetch); walk forward with after`。
2. **`limit` 只有一个旋钮**：`params['limit']` 一律拒绝，报错指向 `page_size`。`page_size` 仍是唯一入口——显式传值时决定每页条数；`page_size=None` 保留旧含义「完全不发 `limit`」；默认 100。
3. **`params['after']` 保留**：投影时取出作为起始游标（断点续拉），之后每一步的 `after` 仍由模块推进。
4. **落点**：投影放在 `paginate()` 内、返回 `_walk()` 之前；`_walk()` 不再做任何合法性判断，只按已投影的 filters 与 `after` 行走。
5. **不新写 ADR**：ADR-0013 已定「校验与行走同属 pagination」，本单只是把它执行完整。

**完成标准**：
1. `paginate(fetch, cursor='id', params={'before': 'x'})` 在调用点抛 `ValueError`，用例不消费迭代器即断言。
2. `params={'limit': 10}` 同样在调用点抛，文案包含 `page_size`。
3. `params={'after': '42'}` 仍从 42 之后开始（`test_resumes_from_a_supplied_cursor` 保持绿）。
4. filters（`begin`/`end`/`instType` 等）在每一页都原样带上（`test_filters_are_sent_on_every_page` 保持绿）。
5. 模块 docstring 的「`before` 不支持、`limit` 由本模块决定」与实现逐条对应；补两个用例后 `pytest test/unit/okx/test_pagination.py` 全绿。

**被否的选项**：优先级方案（显式 `page_size` > `params['limit']` > 100）需要哨兵区分「没传」与「传了 100」，而 `page_size=None` 还背着「完全不带 limit」，三态混在一起不如一个旋钮；静默丢弃 `before`/`limit` 会把「拿到错序数据」继续留在线上；`_walk()` 入口校验违反 ADR-0013 的「调用点抛」。

## Comments

- 2026-11-05 施工完成：422adc0（master，合并入 0.15.0 未发布批次）。全量 pytest 853 passed / 46 subtests；完成标准逐条核对见提交说明与测试。

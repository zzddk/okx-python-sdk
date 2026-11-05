# 06 · 订阅表的条目形状与入口校验

Type: grilling
Status: resolved
Blocked by: —

## Question

评审候选 06。`okx/websocket/subscriptions.py` 的接口面几乎与实现等高：`add(params, cb) -> tuple`、`remove(params) -> tuple` 两个返回值无人接收；条目恒为单元素 tuple，只为对齐线上帧形状（:139 再拆回 `[0]`）。而「arg 必须可路由」这条规则写在会话层 `_require_channel`（`WsBaseAsync.py:316-342`），只覆盖 dict，`unsubscribe` 完全不校验。要定下：**订阅表的条目形状，以及 arg 合法性归谁校验。**

需要一起定下的：

1. **条目形状**：`(arg, callback)` 还是 `(kwargs, params, callback)`；线上帧要 `op`/`args`，arg 与 params 的区分在哪一层做。
2. **返回值**：`add`/`remove` 返回什么（`None`？被替换的 callback？）——先确认现有调用方是否真没人接收。
3. **arg 规则**：channel 非空即可，还是也要 channel 白名单／参数形状；`add`/`remove` 两个入口共享同一次校验，`unsubscribe` 自动获得。
4. **会话侧的残留**：`_require_channel` 删除后，会话的 `subscribe`/`unsubscribe` 是否还有别的校验或拼装。
5. **顺序与路由**：`replay()` 的顺序保证、`take()` 的路由键是否受影响。
6. **测试**：表驱动覆盖 `add`/`remove`/`unsubscribe` 的非法 arg（空 channel、非 dict、channel 缺失）。
7. **ADR**：ADR-0009 的收尾，还是新决定。


## Answer

**拍板（2026-11-05）**：订阅表保留序列入口，但把「什么算可路由的 arg」收进表内；条目退化成 `(arg, callback)`，返回值删掉。

**接口**：`add(params, callback=None) -> None`、`remove(params) -> None`。两个入口都先对整批做校验，再写表或删表——`subscribe([好, 坏])` 抛错时表保持干净，docstring 里「表与 socket 都没被碰过」的承诺继续成立。

**条目**：`_entries: Dict[str, Tuple[Dict, Optional[Callback]]]`；`Subscription` 类删除（仓库内除订阅表自身与测试外无人引用）。`replay()` 直接 `[dict(arg) for arg, _ in …]`，不再 `[0]` 拆包。

**校验**：私有 `_require_routable(arg)`——必须是 dict，且 `channel` 是非空字符串，否则 `ValueError`。`add` 与 `remove` 共用；`remove` 对「合法但没订阅过」的 arg 仍是 no-op。`WsBaseAsync._require_channel` 删除，`subscribe` 不再前置校验，`unsubscribe` 因此自动获得同一条规则。

**不变的契约**：路由键仍是 `json.dumps(arg, sort_keys=True)`；`take()` 仍先 arg 后 id，请求条目一次性；`replay()` 仍按首次加入顺序、返回脱离表的副本；同 arg 再订阅仍原位替换 callback。

**公开面变化**（进 CHANGELOG）：`Subscription` 类删除；`add`/`remove` 不再返回元组；非 dict 或空白 channel 从「静默跳过」变为抛 `ValueError`。

**记账**：不新写 ADR，属 ADR-0009 的收尾。

**完成标准**：
1. `grep -rn '_require_channel\|Subscription(' okx/` 无命中；`subscriptions.py` 不再导出 `Subscription`。
2. 批量校验用例：`add([valid, {'channel': '  '}], cb)` 与 `remove([valid, 'x'])` 抛 `ValueError`，且表里没有任何变化。
3. `unsubscribe` 传非法 arg 抛 `ValueError`（今天完全不校验），会话用例锁住。
4. `replay()` 顺序、副本、排除请求不变；`take()` 的路由键与一次性请求不变（现有 `test_subscriptions.py` 用例改写后保持断言）。
5. `pytest test/unit` 全绿。

**被否的选项**：单条 `add(arg, cb)`（丢掉批量原子性，失败的 subscribe 会在表里留下一条从未成功、却会在重连时被重放的订阅）；`add` + `add_many`（多一个方法只为换回原子性，接口反而更宽）；只校验 `add`（`unsubscribe` 继续接受不可路由的 arg，规则仍分裂）。

## Comments

- 2026-11-05 施工完成：3de62d2（master，合并入 0.15.0 未发布批次）。全量 pytest 853 passed / 46 subtests；完成标准逐条核对见提交说明与测试。

# 端点契约表

把「每个端点发什么」从 24 个测试模块的逐方法断言，收成一张表加一次 sweep。来源：2026-11-05 架构评审候选 02。

## 判断

测试面与 implementation 同宽：95 处 `assert_called_once_with` 逐个锁住内部 params dict，而端点真正的接口只有三元组 (method, path, params)。24 个模块、3280 行、约 270 个用例描述 279 个端点，平均每个端点 4 行断言，其中绝大多数是同一件事的重复：method 对、path 对、dict 相等。

候选 01 之后这一点更明显：端点方法退成一行参数清单，测试仍在逐条复述这行清单——规则只是从 136 处搬进了测试。

删除测试：删掉这些断言，复杂度不转移到别处——表里的一行就是原来的断言，而且顺带给出「参数名」这层事实。真正会丢的是「哪些参数不该发送」：那归 `Transport` 与 `test_okxclient` 管。

## 目标形状

`test/unit/okx/endpoints.py` 是唯一描述端点面的地方，279 行：

```python
ENDPOINTS = {
    AccountAPI: {
        'get_positions': (c.GET, c.POSITION_INFO, 'instType instId posId'),
    },
}
```

spec 三种写法：

- `'a b c'`：请求带一个恰好含这些键的 dict
- `'[a b c]'`：请求带一个单元素 list，元素是上述 dict
- `PAYLOAD`：把调用方给的 list/dict 原样转发，没有键名可列

`test/unit/okx/test_endpoint_table.py` 每个端点一个参数化用例：每个形参喂一个哨兵值调用一次，然后

1. 断言 (method, path)；
2. 断言发送的键集合等于表里的名字（`from_` / `froms` → `from` 走一张别名表）；
3. 断言发送的值就是哨兵值——端点不改写参数；
4. 断言表里的名字集合等于`inspect.signature`——参数新增、改名、删除而表没跟，就失败。

再加 `test_the_table_covers_every_public_method`：新端点没进表就失败。

## 删除

保留判据是「表说不出来的事实」：

- **常量字面量**：URL 拼错只有逐条 `assertEqual` 挡得住。
- **取值语义**：`False` / `0` / `[]` / `''` 仍要发送，`None` 不发送。
- **签名契约**：位置参数顺序、`orders_data` / `params` 别名与优先级、缺参抛错。
- **跨端点对称**：`get_account_bills` 与 `get_account_bills_archive` 的参数键一致。

其余删除：7 个整文件（`test_account_v5_batch`、`test_convert_v5_batch`、`test_funding`、`test_public_data`、`test_public_data_v5_batch`、`test_trade_v5_batch`、`test_trading_data`），7 个文件裁到只剩常量与语义用例。共 113 个用例、约 1350 行。

## 非目标

- 不动 `test_contract.py`：它管常量唯一性与「每个声明的 path 都可达」，与参数面正交。
- 不在端点层重复 `Transport` 的 None 省略：`test_okxclient` / `test_transport` 已经锁住。
- 不给 `PAYLOAD` 行做参数名守护：那 6 个方法把调用方对象原样转发，没有名字可拼错。

## 验证

- 三次变异，三次被抓：把 `get_position_risk` 的键改成 `instTypeX`；给 `get_positions` 加一个签名参数但不加进 dict；把它的 path 改成 `POSITION_RISK`。
- `pytest test/unit`：改动前 639 passed，改动后 806 passed（表新增 280 个用例，删除 113 个）。
- `ruff check test/unit`：70 → 19，剩余都在未触碰的文件里。

## 风险

- 表是快照，不是代码的投影。端点变更必须同时改表；漏改会在 sweep 里失败，但「表与代码一起改错」没有第三方校验——这是所有契约测试的共同代价，换来的是每一处变更都必须显式出现在 diff 里。
- 被删的用例里有几个循环遍历（不同 instType / period 的转发）。表只验证一个哨兵值的转发，值类型差异（list vs str）不再单独断言。

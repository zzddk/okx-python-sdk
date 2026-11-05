# 端点参数面

把「未设置的参数不发送」从 136 处调用点收回 `Transport`。来源：2026-11-05 架构评审候选 01。

## 判断

`Transport` 已经是这条规则的持有者：`utils.parse_params_to_str` 丢弃 GET 查询串里的 `None`，`utils.drop_none_params` 丢弃 POST body 里的 `None`（ADR-0001：`None` 是唯一的「未设置」值）。端点 module 却在 136 处用 `if x is not None: params[x] = x` 再实现一遍，分布在 14 个文件。

删除测试：删掉这些分支，复杂度并不转移——`Transport` 的行为保持不变，分支从未产生过不同结果。这是重复删除，不是搬移。保留它们只有一个后果：规则复制 136 次，新增参数时两种写法并存，读者必须先知道 `Transport` 的行为才能判断哪种写法正确。

三处不走纯分支的特例：

- `MarketData.get_tickers` 用 if/else 决定是否写 `uly` 键。合并成一个 dict 后由 `Transport` 丢弃 `None`，线上请求逐字节相同。
- `SubAccount.reset_subaccount_apikey` 的 `if ip != '-1'` 是另一种哨兵（`'-1'` 表示不设置），保留；只合并 `label` / `perm` 两条。合并后 `ip` 在 JSON body 里的键序移到末尾——OKX 不依赖 JSON 键序。
- `Funding.get_deposit_lightning` 的 `if to is not None: params = {'to': to}` 是缺陷：它覆盖整个 dict，默认调用只发 `to`，丢掉 `ccy` 与 `amt`。单独作为 issue 02。

## 目标形状

每个端点方法一个 dict 字面量，原样交给 `request`：

```python
def get_max_order_size(self, instId, tdMode, ccy=None, px=None, tradeQuoteCcy=None):
    params = {'instId': instId, 'tdMode': tdMode, 'ccy': ccy, 'px': px, 'tradeQuoteCcy': tradeQuoteCcy}
    return self.request(GET, MAX_TRADE_SIZE, params)
```

不把 dict 内联进 `request(...)`：长参数列表要换行，两行式与相邻方法一致，diff 也只看参数那一行。

## 非目标

- 不动 `Transport` / `utils`：规则本来就在那里。
- 不碰把 list 直接当 payload 的端点（`orders_data`、`params` 别名），它们不经过 None 省略。
- 不清理 `params = {}` 的空样板（`ConvertAPI.get_support_coin` 等 4 处），与本次无关。
- 不做候选 02（表驱动测试）。本次只让既有用例改用「实际发送的参数」视图，表驱动留给 02。

## 验证

- **线上请求逐字节比对**：遍历 279 个端点 × 3 组参数（只给必填 / 全部给值 / 全部给空串），用 `httpx.MockTransport` 记录 method、URL、body。改动前后 837 条记录相同，唯二差异是 `reset_subaccount_apikey` 的键序与 issue 02 的修复。
- **参数覆盖审计**：遍历所有端点方法，核对每个形参都出现在 params dict 里；剩下的 `from_` / `froms`（别名）与 `orders_data`（list payload）是有意为之。
- 全量单测：改动前 638 passed，改动后 639 passed（新增 issue 02 的用例）。

## 风险

- 测试此前断言的是内部 params dict。51 个用例改为断言「实际发送的参数」（`fakes.sent_params`），因此看不见「漏写参数」——由上文的覆盖审计补上，后续由候选 02 的表驱动测试长期承担。
- 键序可能变化（SubAccount 一处）。OKX 不依赖 JSON 键序，签名对服务端收到的字节计算。

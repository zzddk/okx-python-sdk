# 未设置的参数只在 Transport 丢弃一次

`Transport.request` 的 docstring 早就写着「`None` 表示不发送这个参数」：GET 由 `utils.parse_params_to_str` 丢弃，POST body 由 `utils.drop_none_params` 丢弃。端点方法却各自用 `if x is not None: params[x] = x` 再实现一遍，共 136 处、分布在 14 个文件；`MarketData.get_tickers` 甚至用 if/else 决定要不要写 `uly` 键。

两套写法并存时，读者必须知道 `Transport` 的行为才能判断哪一种正确；新增一个参数时也要重新决定一次。规则复制 136 次，改一次就要找 136 处。

我们决定：**端点方法把每个形参无条件放进 dict，`None` 的省略只在 `Transport` 发生一次**。ADR-0001 的「`None` 是唯一未设置值」原样成立，变的只是谁来执行它。

## Considered Options

- **保留调用点分支**：分支与 `Transport` 的行为从未不同，删除它不转移复杂度。保留的唯一效果是让同一条规则有 136 份副本，并把「这个参数可不可以不传」从签名默认值变成每个方法自行决定。
- **在 `OkxClient.request` 里再过滤一层**：多一层包装，规则仍有两处（`Transport` 与实际发请求前），且端点 dict 是否含 `None` 依旧取决于各方法的写法。
- **端点改传 `**kwargs` 或 `_params(...)` helper**：只把样板换个写法，参数名与值的对应从字面量变成约定，拼写错误不再被一眼看见。
- **把 dict 内联进 `request(...)`**：短参数表能压成一行，但长参数表必须换行，与相邻方法风格不一致，diff 也会盖住真正的改动。

## Consequences

- 端点 module 的 implementation 退化成「参数清单 + 一次转发」；新增参数只加一行，不必再决定要不要写分支。
- `Transport` 成为「`None` 不发送」的唯一所有者。GET 与 POST 的省略分别由 `parse_params_to_str` 与 `drop_none_params` 完成，两者都只丢顶层键。
- 端点单测不再有理由断言内部 params dict。`test/unit/okx/fakes.py` 的 `sent_params` / `assert_request` 把断言挪到「实际发送的参数」上：`None` 视为未发送，与线上行为一致。代价是看不见「漏写参数」，由一次性覆盖审计补上，长期由候选 02 的表驱动测试承担。
- 键序可能变化（`SubAccount.reset_subaccount_apikey` 的 `ip` 移到末尾）。OKX 按收到的请求字节验签，JSON 对象键序不是契约的一部分。
- 顺带发现并修复 `Funding.get_deposit_lightning`：它的分支写的是 `params = {'to': to}`（覆盖整个 dict 而不是写入一个键），默认调用只发 `to`。
- 这次删除没有引入 ADR-0006 那种迁移故事，端点签名与线上请求都不变，因此随 0.13.0 作为非破坏性批次发布。

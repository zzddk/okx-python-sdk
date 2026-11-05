# API 类只暴露 Transport，不再转发配置字段

ADR-0006 决定 `OkxClient` 保留九个只读属性（凭证、`flag`、`debug`、`domain` 与重试策略）并转发到 `Transport`，理由是「迁移成本集中在一处」。一对一的时候这个判断成立：九个属性、九个字段、一个机械的 getter。

问题在于它要求每次给 `Transport` 加字段时都记得补一个 getter。0.11 为 WebSocket 加了 `proxy`，转发面没有跟上——`api.proxy` 不存在，而同一份配置在 `Transport` 上一直都在。没有任何测试会因为漏掉而变红，因为测试断言的是「已有的九个」。

我们决定：**删掉九个转发属性，API 类只暴露 `transport`**。读配置走 `api.transport.X`，配置仍然只有 `Transport` 一份。

## Considered Options

- **只补 `proxy`，保持现状**：修好这一次，下一个字段仍会漏；而且要为此写一条「每个 Transport 字段都有 getter」的反射测试，用测试去维护一份本可以不存在的接口。
- **`__getattr__` 动态转发**：不会漂移，属性体贴删。但它把「API 类暴露什么」变成「Transport 有什么」：接口变成隐式的、IDE 补全消失、typo 落到 `Transport` 上抛出的是另一个对象的 AttributeError；pickle/copy 也会跟着 `__getattr__` 走。用三行魔法换九个 getter，得不偿失。
- **只保留 `flag` 与 `debug` 这类常用字段**：留下的是任意子集，读者仍要判断「这个字段在不在」，而判断依据只有记忆。
- **保留属性但标废弃**：ADR-0001 的立场是不为旧名保留别名；留着就会一直活到 1.0，每个新读者要学两套名字。

## Consequences

- **破坏性改动，随 0.14.0 发布**（ADR-0004：一批共享同一个迁移故事的改动对应一个 minor）。迁移是逐字段改名：`api.X` → `api.transport.X`，九个名字一次列清。
- **取代 ADR-0006 的最后一条后果**（「`OkxClient` 保留只读属性并转发」）。0006 的其余结论不变：Transport 持有配置、`client=` 删除、`request` 是唯一接缝。
- `api.transport` 是受支持的读入口；`_t` 仍然是私有的，但不再是非读配置的唯一途径。
- 仓库内零调用点：端点方法与 WS 代码只读 `Transport`；README 与 example 从未用过这些属性。唯一要改的是两条测试。
- 新增一条守卫：九个名字在 API 实例上必须 `hasattr` 为 False——防止有人再把它们加回来。

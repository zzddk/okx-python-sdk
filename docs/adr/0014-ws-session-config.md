# Transport 到 WS 会话配置只解析一次

两个 WS 客户端都从 REST 的 `Transport` 构造：`WsPrivateAsync.from_transport` 与 `WsPublicAsync.from_transport`。两个方法各自做了同一件事——校验参数是 `Transport`、读 `flag` 判断模拟盘、把五个字段搬进构造参数、回落 `debug`、透传 `proxy`——只是主机表不同。两边的 demo 判定甚至已经长得不一样：一处抽成变量再查表，一处内联进三元表达式。

结果是一条规则有两份实现：`Transport` 每加一个 WS 该继承的字段，要改两个文件；两处漏掉一处，用户拿到的是静默缺失的配置。

我们决定：**解析只做一次**。`okx/websocket/config.py` 的 `session_config(transport, hosts, url=None, debug=None)` 返回构造参数，`hosts` 是「是否模拟盘 → 主机」的表；`require_transport` 是共用的类型检查。每个客户端只声明自己的主机表（Public 还声明 channel → 表）。

> Update (2026-11-07): `session_config` 的所有者范围从「字段映射」扩到「字段映射 + 空值契约翻译」。REST 侧把凭据缺席表示为 `consts/http.py` 定义的哨兵，WS 会话侧却用空串，两套空值契约在接缝处对立；裸拷贝会让私有会话把哨兵当成三个合法凭据上送登录。现在由 `session_config` 把哨兵翻成空串，下游只剩一个空值契约、由会话的凭据谓词唯一解释。本文的决定（解析只做一次、唯一所有者）与 Consequences 的「公开接口不变」均不变；术语见根目录 `GLOSSARY.md` 的「凭据缺席」，落地见 `.scratch/no-credential-ws/spec.md`。

## Considered Options

- **把 `from_transport` 提到 `WsBaseAsync`**：Private 会很干净，但 Public 的 `channel` 无处安放——塞进 `**options` 会让 `WsPublicAsync.from_transport` 的公开签名消失，重写又回到两份实现。两个客户端里总有一个要特殊处理，那就不如让共享部分只做共享的事。
- **只抽共用主机选择**（`ws_url(transport, live, demo)`）：字段拷贝与 demo 判定仍各写一遍，Transport 加字段照样要改两处，正是这次要解决的问题。
- **`WsConfig` 值对象**：有名字、字段可断言，但本质仍是那几个键，多一层类型与 `as_kwargs()` 转换，收益只在类型检查上。
- **不动**：现状能工作，只是加字段时靠记忆；等下一次真的漏了再说——那时要同时排查两个文件。

## Consequences

- `Transport` 新增 WS 该继承的字段，只改 `session_config` 一处；两个客户端的 `from_transport` 各自 1–3 行。
- 主机表成了唯一的主机事实：`_HOSTS = {False: …, True: …}`，Public 多一层 channel。加 channel 是加一行数据，不是加一段分支。
- `WsPublicAsync` 先校验 transport 再校验 channel，保持「TypeError 优先」的既有顺序；`session_config` 内部的校验是幂等的。
- `session_config` 可脱离客户端测试：字段映射、demo 选择、url/debug 覆盖各有用例。客户端表另有结构守卫（两个键、互不相同）。
- 公开接口不变：两个 `from_transport` 的参数、默认值、异常类型与文案都不动；`okx/websocket/config.py` 是新增的可导入模块。

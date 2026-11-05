# WS 会话配置只解析一次

两个 `from_transport` 各自把 `Transport` 摊成 WS 构造参数。来源：2026-11-05 架构评审候选 05。

## 判断

- **isinstance 校验两份**，文案逐字相同——复制留下的指纹。
- **demo 判定形状已经不同**：Public 抽成 `demo` 变量再查 host 表，Private 把 `str(transport.flag) == '1'` 内联进三元表达式。同一个事实两种写法，说明没有共同的所有者。
- **5 个字段逐个拷贝两份**（apiKey / passphrase / secretKey / debug / proxy）。Transport 每加一个 WS 该继承的字段，要改两个文件，漏一个就是静默丢配置。
- 主机表本身不是重复：Public 有 channel 维度，Private 没有。这部分该留在客户端。

删除测试：把共享部分收成一处后，客户端只剩「我的主机表是什么」。规则不再随客户端数量线性增长。

## 目标形状

`okx/websocket/config.py`：

```python
Hosts = Mapping[bool, str]              # 是否模拟盘 -> 主机

def require_transport(value) -> Transport
def session_config(transport, hosts, url=None, debug=None) -> dict
```

客户端：

```python
class WsPrivateAsync:
    _HOSTS = {False: WS_PRIVATE_URL, True: WS_PRIVATE_DEMO_URL}

    @classmethod
    def from_transport(cls, transport, url=None, debug=None):
        return cls(**session_config(transport, cls._HOSTS, url=url, debug=debug))

class WsPublicAsync:
    _CHANNELS = {'public': {False: …, True: …}, 'business': {False: …, True: …}}

    @classmethod
    def from_transport(cls, transport, channel='public', url=None, debug=None):
        require_transport(transport)
        try:
            hosts = cls._CHANNELS[channel]
        except KeyError:
            raise ValueError(f"channel must be 'public' or 'business', got {channel!r}") from None
        return cls(**session_config(transport, hosts, url=url, debug=debug))
```

Public 里 `require_transport` 先于 channel 校验：参数顺序上 transport 在前，错误优先级保持不变。`session_config` 内部会再校验一次，幂等。

## 非目标

- 不把 `from_transport` 提到基类：Public 的 `channel` 要么塞进 `**options`（公开签名变模糊），要么整个重写（重复又回来）。见 ADR-0014。
- 不改构造参数、默认主机、代理规则。
- 不合并两个 `__init__`：它们本来就只转发，签名不同（Private 的凭证必填）。

## 验证

- `test/unit/okx/websocket/test_ws_config.py` 17 → 23：新增 6 条直接测 `session_config`（字段映射、demo 选择、url 覆盖、debug 覆盖、类型拒绝、主机表结构）。
- 既有 `TestFromTransport` 与 `TestProxyInheritance` 一行不改即通过。
- `grep -rn "isinstance(transport, Transport)" okx/websocket/` 只命中 `config.py`。

## 风险

- `_HOSTS` / `_CHANNELS` 是私有类属性，测试直接读它们；改名要同步测试。
- 新增一个 WS 客户端只需要给表，但它的 `__init__` 必须接受 `session_config` 的 6 个键（url、apiKey、passphrase、secretKey、debug、proxy）。

# Transport 保留 proxy

Status: resolved
Release: 0.10.1
Done in: 0.11.0

## 为什么

`Transport.__init__` 收下 `proxy`，转手交给 `_make_http` 就不再保留（`okx/transport.py:44,58`）。结果是「这个 transport 走哪个代理」这个事实在对象上不可读，WS 层想继承 REST 的代理设置无从取。`ws-hardening/issues/04` 的验收标准「`from_client` 能继承 REST 的 proxy」因此无法实现。

## 做什么

在 `Transport` 上保存 `self.proxy = proxy`，作为只读配置的一部分，与 `flag` / `domain` 并列。不改变任何请求行为，纯增量。

## 完成标准

1. `Transport(proxy='http://127.0.0.1:8080').proxy` 返回该字符串；未给时为 `None`。
2. 注入 `http=` 时 `proxy` 仍然如实记录（它只是配置的可读副本，不影响「注入 http 就不解析环境代理」的既有规则）。
3. `OkxClient` **不**新增 `proxy` 转发属性。`from_transport` 只收 `Transport`（ADR-0008），多一个门面属性没有消费者，还会让「代理配置的唯一持有者是 Transport」变得含糊。
4. `env -u ALL_PROXY … python -m pytest test/unit -q` 602 passed，数目不变。

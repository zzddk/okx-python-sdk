# API 类的配置面

把 Transport 的 9 个字段从 API 类上撤掉，只留 `transport` 一个读入口。来源：2026-11-05 架构评审候选 06。

## 判断

- ADR-0006 决定「`OkxClient` 保留只读属性并转发」，当时的理由是破坏性最小：9 个属性对 9 个字段，一对一。
- 之后 Transport 加了 `proxy`（0.11 通行 WS），转发面没跟上——`api.proxy` 不存在。这就是「两份接口」的失效方式：不是一次大错，是每次加字段时的一次遗忘。
- 内部零使用：`grep` 显示 `okx/` 里没有任何端点或 WS 代码读这些属性；唯一的消费者是 `test_okxclient` 自己。
- 删除测试：删掉转发，用户仍能从构造时传入的 Transport 读到全部配置——信息没有消失，只是不再有第二个入口。

## 目标形状

```python
class OkxClient:
    @property
    def transport(self) -> Transport: ...   # 唯一读入口
    def request(method, path, params=None, *, replayable=None): ...
    def paginate(method, cursor=None, ...): ...
    def close(self): ...
    def __enter__ / __exit__
```

删除的九个属性：`API_KEY`、`API_SECRET_KEY`、`PASSPHRASE`、`flag`、`debug`、`domain`、`raise_on_error`、`max_retries`、`retry_backoff`。

## 破坏性与迁移

- 随 0.14.0 发布（ADR-0004：一批破坏性改动对应一个 minor）。
- 迁移是逐字段改名：`api.X` → `api.transport.X`。
- 受影响面是所有 `*API` 类（都继承 `OkxClient`）；仓库内无调用点，README 与 example 也没用过这些属性。

## 非目标

- 不动 `request` / `paginate` / `close` 与上下文管理。
- 不加 `__getattr__` 兜底：那会把「API 类暴露什么」变成「Transport 有什么」，接口重新变成隐式的，而且 typo 会落到 Transport 上报错。
- 不改 Transport 的字段，也不加新字段。

## 验证

- `hasattr(api, name)` 对九个名字全为 False（一条用例逐名断言）。
- `api.transport is transport`——同一个对象，不是拷贝。
- 全量 822 → 821（删 3 条旧用例，加 2 条），其余用例不动。

## 风险

- 外部代码读 `api.flag` 之类会 AttributeError。这是本批唯一的破坏点，由迁移表覆盖。
- 有人把 API 实例当配置容器传来传去：现在要传 `api.transport`。

# 传输层接缝

把 REST 层的横切逻辑从「基类的私有方法」挪到「可注入的传输模块」。来源：2026-11-05 设计评审。

拆成两个工单：`issues/01-transport-internal.md`（非破坏，先做）、`issues/02-transport-api.md`（破坏窗口）。验收线写在各自的「完成标准」里。

## 判断

`_request(method, path, params)` 已经是深模块：签名、序列化、重试、限流、错误映射都在它后面，46 个文件共用。缺陷是它挂在 `OkxClient` 的私有属性上，而 `OkxClient` 继承 `httpx.Client`：

- 没有任何端点方法用 `self.get(` / `self.post(`；继承只借了构造函数，却把 httpx 的约 20 个公开方法算进了每个 API 类的接口。
- `client=` 用 11 行字段拷贝模拟共享连接池，外层的 `_send` / `_limiter` / `domain` 因此是死的。
- `test/unit` 有 122 处 `patch.object(..., '_request_with_params')`，契约测试用 `object.__new__(cls)`——测试想跨这道接缝，得先逃出这道接缝。

## 目标形状

**T1 不破坏。** `OkxClient` 改成普通类，内部持有 `okx/transport.py` 的 `Transport`。构造参数、`_request`、`paginate` 原样保留，httpx 只出现在 `transport.py`。接口只有 `request(method, path, params, *, replayable=None)` 与 `close()`。

**T2 破坏窗口。** API 类改收 `Transport`，9 个配置参数从 API 类移到 `Transport`，删 `client=`。

## 非目标

- **不删 `_request_with_params` / `_request_without_params`**：与 `_request` 同签名，但 122 个用例把它当 patch 目标；改名零收益，改测试 122 处。等 T2 重写测试时一起做。
- **不动 `paginate` 的 `inspect.signature` 探测**：它只为两个 page 型端点换来一句更准的报错，代价是客户类反过来读自己子类的方法签名。要改就改成「删掉反射、只留通用报错」，是独立取舍。
- **不合并端点方法里的 `params={}` 样板**：机械 diff 281 处、零行为收益。
- **不动 `consts/rate_limits.py` 的旁表。**

## 风险

- `OkxClient` 不再是 `httpx.Client`：依赖 `.get()` / `.close()` / 上下文管理器的人会静默坏掉。已核对仓库内无此用法，README 与 example 也未展示。降级方案：`close()` 与 `__enter__/__exit__` 在 `OkxClient` 上保留一行转发。
- `http=` 注入改变代理解析路径：显式传 transport 时 httpx 不读环境代理。文档里要说明「显式注入 transport = 自己负责代理」。
- `Transport` 在 T1 就会被测试导入，等于提前公开。若不想承诺这个名字，T1 用 `okx/_transport.py`，T2 再改为公开。

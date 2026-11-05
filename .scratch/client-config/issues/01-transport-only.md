# API 类只暴露 Transport，不再转发配置字段

Status: resolved
Release: 0.14.0

## 为什么

见 `spec.md` 与 ADR-0015。ADR-0006 让 `OkxClient` 转发九个配置字段；0.11 给 Transport 加了 `proxy` 之后转发面没跟上，两份接口开始漂移。

## 做什么

删除九个转发属性，加一个 `transport` 只读属性；`test_okxclient` 与 `test_retry` 的相应断言改成读 `client.transport`。

## 完成标准

1. `OkxClient` 的公开面：`transport`、`request`、`paginate`、`close`、上下文管理。
2. 九个名字在 API 实例上 `hasattr` 为 False。
3. `api.transport is transport`（不是拷贝）。
4. 全量测试全绿；改动只落在 `okx/okxclient.py`、两个测试文件、CHANGELOG、ADR。
5. CHANGELOG 给出 0.14.0 的 Removed 与迁移表。

## Comments

2026-11-05 — 已实现。`okxclient.py` 89 → 62 行（删九个 property 体、加一个带 docstring 的 `transport`）。`pytest test/unit` 821 passed；新增一条逐名 `hasattr` 守卫。

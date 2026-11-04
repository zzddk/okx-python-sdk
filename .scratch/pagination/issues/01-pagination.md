# 分页迭代器

Status: resolved
Release: 0.7.0
Done in: 0.7.0

## 为什么

50 个端点用 `after` 向前翻页，调用方各自手写循环，普遍缺少「游标未推进」的防死循环判断。

## 做什么

见 `spec.md`。实现为 `OkxClient.paginate` 与 `okx.pagination.paginate`。

## 完成标准

- 每页请求都走 `_request`，因此重试与限流自动生效。
- 缺少 `cursor` 在调用点抛 `ValueError`，而不是在第一次 `next()` 时。
- 服务端忽略 `after` 时迭代会停下，不死循环。

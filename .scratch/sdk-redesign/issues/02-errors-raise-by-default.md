# 请求失败默认抛异常

Status: ready-for-agent
Release: 0.5.0

## 为什么

`OkxClient._request` 无条件 `return response.json()`（`okx/okxclient.py:58`），从不检查 HTTP 状态码或业务码 `code != '0'`；`okx/exceptions.py` 里的三个异常类从未被抛出。结果是「订单被拒」和「下单成功」在调用侧看起来一样。

## 做什么

HTTP ≥ 400 或 `code != '0'` 时抛 `OkxAPIException`，构造时带 `code` / `message` / `status_code` / 原始 response；新增 `raise_on_error=False` 参数退回返回 dict 的旧行为。见 ADR-0002。

## 完成标准

失败请求默认抛异常；`raise_on_error=False` 下返回值与 0.4.4 完全一致；异常对象能区分网络错误与业务拒绝。

## Comments

- 2026-11-05: moved from 0.4.5 to 0.5.0. Raising by default changes caller-visible behaviour, so users on `~=0.4` would receive it in a patch release. The implementation is specified and ready; it ships with the other breaking changes.

## Comments

- 2026-11-05: implemented in 0.5.0. `OkxAPIException` now accepts a pre-parsed payload and always exposes `code`/`message`/`status_code`/`response`; `_request` raises on HTTP `>= 400` or non-`'0'` code, and `raise_on_error=False` returns the payload unchanged. Network errors are not wrapped. Unit tests cover success, business rejection, HTTP error, non-JSON error bodies, opt-out, and network propagation.

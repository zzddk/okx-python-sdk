# 去掉 WS 端点上的退役 8443 端口

Status: resolved
Done in: 45b86f9

## 为什么

OKX 于 2026-10-31 停止公网 WebSocket 的 8443 端口（Colo 2026-11-16），六个 WS 主机常量仍带 `:8443`，连接会失败。详见 `spec.md`。

## 做什么

- `okxsdk/consts/websocket.py`：六个常量删除 `:8443`，保留主机、路径与 `brokerId=9999`；模块 docstring 记下退役日期与 ADR-0025。
- `test/unit/okxsdk/test_network_hosts.py`：更新 `EXPECTED_HOSTS`；新增 `test_network_hosts_use_the_default_port`。
- `test/test_ws_public_async.py`、`test/test_ws_private_async.py`：同步去掉 `:8443`，删除 `wspap.okex.com` 过期注释。

## 完成标准

- `pytest test/unit/` 全绿（866 passed）。
- `ruff check okxsdk/ test/unit/` 全绿。

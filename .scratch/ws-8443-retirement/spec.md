# WebSocket 端点迁移到默认 443

来源：2026-11-12 对「OKX 下线 8443」消息的核实（`/grill-with-docs`，逐轮拍板）。落地见 `.scratch/ws-8443-retirement/issues/`。

## 判断

OKX 官方公告（help 公告 2026-09-30、API changelog 2026-10-22）确认：**公网 8443 端口于 2026-10-31 停止接受 WebSocket 连接，Colo 于 2026-11-16 停止**。之后连接 8443 直接失败；只需从 URL 删除 `:8443`，域名与路径不变，`wss://` 默认走 443。REST 不受影响。

用户消息里的三处「仓库事实」与本仓库对不上：没有 `config.yaml` / `websocket_url`，没有不带端口的脚本，也没有 vendored 上游 SDK；`okxsdk/` 本身就是本项目的 SDK 实现。真正过时的是 `okxsdk/consts/websocket.py:8-15` 六个 WS 主机常量（实盘 3 + 模拟盘 3，全部带 `:8443`）。它们经 `okxsdk/consts/__init__.py` 重导出，属于公共契约。实盘与模拟盘都受影响，且 `Transport` 的 `flag` 默认是 `'1'`（模拟盘）。

## 目标

- 六个常量去掉 `:8443`，主机、路径、`?brokerId=9999` 保持不变。
- 更新 `test/unit/okxsdk/test_network_hosts.py` 的逐字节期望表。
- 新增不变量测试：任何 WS 主机常量不得带非默认端口（`urlparse(value).port in (None, 443)`）。
- 同步更新不被 CI 收集、但会被直接复制运行的手工脚本 `test/test_ws_public_async.py`、`test/test_ws_private_async.py`。

## 非目标

- 不新增 EEA（`wseea.okx.com`、`wseeapap.okx.com`）与 US（`wsus.okx.com`、`wsuspap.okx.com`）域名常量；仓库从未提供区域域名。
- 不动 `.scratch/bug-hunt-2026-11-06/hunt.py`：它是 11-06 bug 狩猎的历史快照，保持当时的值，重跑报红属预期。
- 不碰仓库外的调用方脚本 / 配置。调用方若通过 `url=` 显式传地址，由调用方自行迁移。
- 不改版本号、不写 CHANGELOG、不打 tag：遵循 `.scratch/release-batch/spec.md` 的「现在别动版本号」，发版时在 `### Fixed` 下补一条。

## 完成标准

- CI：`pytest test/unit/`（866 passed）与 `ruff check okxsdk/ test/unit/` 全绿。
- `git grep 8443` 只命中说明性文字（注释、spec、ADR），不再命中任何 URL 字面量。

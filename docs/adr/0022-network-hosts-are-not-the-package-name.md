# 网络主机名不是包名

0.17.0 把 import 包从 `okx` 改名为 `okxsdk`（4daa4c6，ADR-0019）时，替换覆盖了整个仓库，连 `okxsdk/consts/http.py` 的 `API_URL` 与 `okxsdk/consts/websocket.py` 的六个 WS 主机字面量一起改了：`https://www.okx.com` 变成 `https://www.okxsdk.com`，`ws.okx.com` / `wspap.okx.com` 变成 `*.okxsdk.com`。这些域不存在，已发布的 0.17.0 所有 REST 与 WebSocket 请求都发不出去。当时的测试只断言 `startswith('wss://')` 与 `'wspap' in url`，所以 846 条全绿。

我们决定：**网络主机名是外部事实，不是包名的一部分，任何包重命名都不得触及它们。** 把 `API_URL` 与六个 WS 端点恢复为真实 OKX 地址，并由 `test/unit/okxsdk/test_network_hosts.py` 钉住两条不变量：任何 URL 字面量都不得含有 `okxsdk`，且 host 必须是 `okx.com` 或其子域；同时逐字节断言七个常量的值与其调用点。

## Considered Options

- **恢复字面量 + 加不变量测试（采纳）**：最小修复，且把「改名不能碰到主机名」变成会变红的测试，而不是靠人记住。
- **把主机名抽成独立模块 / 配置，改名时显式跳过**：多一层结构，也就多一个要维护的地方；不变量测试已经足够，不必为一次性风险加抽象。
- **保留 `okxsdk.com` 并注册该域名**：域名不是项目资产，且会改变 SDK 的对外行为，排除。
- **只靠 code review 清单**：人总会漏，本次事故正是这么发生的，排除。

## Consequences

- 今后任何「把 A 改名成 B」的改动，必须先区分字面量里哪些是**标识符**（模块名、导入、目录、发行名）与哪些是**外部事实**（域名、URL 路径、HTTP header 名、常量取值）；后者逐项核对，不进全局替换。
- `test_network_hosts.py` 同时钉住常量与 `Transport` / `WsPublicAsync` / `WsPrivateAsync` 的调用点；盲改会同时踩中「值」与「不含 okxsdk」两条断言。
- 这是已发布版本的错误修复，不引入新 API，不需要 Migration；0.17.1 之类的修复版节拍按 ADR-0004 另议。
- 历史 ADR 与 `.scratch` 工单里的 `okx/` 路径按 ADR-0019 保留为当时的记录，不回写。

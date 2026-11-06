# 04 · REST 签名路径没有测试

Type: task
Status: resolved
Done in: 1439a54
Blocked by: —

## Question

评审候选 04。REST 签名分支（`okx/transport.py:148-150`）与 `utils.get_header`（`okx/utils.py:26-37`）覆盖率为 0；全仓测试没有一处断言 `OK-ACCESS-SIGN` 或 `OK-ACCESS-TIMESTAMP`。登录签名有固定向量（`test/unit/okx/websocket/test_login.py:29`），REST 没有。

## 证据

- `pytest --cov=okx`：`transport.py` 漏 148-150；`utils.py` 漏 26-37。
- `grep -rn 'OK-ACCESS\|get_header\|pre_hash' test/unit` 只命中无关的凭证构造，没有 header 断言。
- `pre_hash` 比登录多拼 method、query string 与 POST body，这三处没有回归保护。

## 建议方案

把时间戳来源从 `_send()` 抽成可注入 clock（默认 `utils.get_timestamp`），用固定时间戳断言：

1. GET + 多个 query 参数（顺序与编码）。
2. POST + JSON body（签名用的 body 与实际发送的 body 逐字节一致）。
3. `OK-ACCESS-KEY / SIGN / TIMESTAMP / PASSPHRASE`、`x-simulated-trading` 全部断言。

## 验收标准

1. 两个新用例覆盖 GET 与 POST 的签名 header，时间戳固定，可重复。
2. `okx/transport.py:148-150` 与 `okx/utils.py:26-37` 覆盖率不再为 0。
3. 不触网、不需要真实私钥。
4. `pytest test/unit` 全绿。

## Answer

**拍板（2026-11-06）**：不加 clock 参数，测试直接 patch `okx.utils.get_timestamp`；生产代码零改动。

- `Transport._send()` 在调用时解析 `utils.get_timestamp`，patch 模块即可固定时间；签名流水线（method、query、body、header）照常走。
- 不给 `Transport.__init__` 加第 13 个参数：固定时钟在线上是误用口（签名过期 50102），而测试只需要一个 time double。
- 向量：GET 带 query、POST 带 body 各一条；期望的 base64 用 stdlib `hmac`/`hashlib` 独立算出，不调用 `utils.sign`，避免自证。
- 变异检查：从 `pre_hash` 删掉 body，只有 POST 用例红，GET 仍绿——证明向量确实钉住了 body 拼接。

**验收对照**：`transport.py:148-150` 与 `utils.py:26-37` 不再为 0（`utils.py` 只剩 debug 分支未覆盖）；866 passed / 313 subtests；不触网、不需要真实私钥。

**未决**：若将来要做服务器时间对齐（50102），再考虑显式的 time source；那是一个功能，不是测试接缝。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 04。
- 2026-11-06 施工完成：1439a54（master）。两个固定向量用例；变异检查（删 body）只让 POST 红；全量 866 passed / 313 subtests。

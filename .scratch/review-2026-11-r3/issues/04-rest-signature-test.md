# 04 · REST 签名路径没有测试

Type: task
Status: needs-triage
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

## 未决

- clock 注入放在 `Transport.__init__` 还是模块级函数替换？建议构造参数，和 `login_payload(timestamp=)` 同构。

## Comments

- 2026-11-06 评审提出：`architecture-review-20261106-202110.html` 候选 04。

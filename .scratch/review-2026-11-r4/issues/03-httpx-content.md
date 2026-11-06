# 03 · POST 改用 content=，消掉 httpx 弃用告警

Type: task
Status: resolved
Done in: a464c12
Blocked by: —

## Question

`Transport._send` 用 `data=` 传 JSON 字符串发 POST，httpx 已弃用这个用法。改成 `content=`。

## 证据

- `okxsdk/transport.py:161`：`response = self._http.post(full_path, data=body, headers=header)`，`body` 是 `json.dumps(...)` 的字符串。
- `pytest` 摘要里 12 条 warning 全部是 `DeprecationWarning: Use 'content=<...>' to upload raw bytes/text content.`（`test_retry.py` 10、`test_transport.py` 1、`test_okxclient.py` 1）。
- `python -W error::DeprecationWarning` 下调用一次 POST 即可稳定复现该告警。
- 本机 httpx 0.28.1（`Requires-Python: >=3.8`）；`data=<str>` 目前仍按 raw content 处理，但弃用意味着后续版本会改义或移除。
- `okxsdk/transport.py:75-81` 已有针对旧版 httpx `proxy` / `proxies` 的兼容分支，说明依赖下限较宽，更该避开已弃用参数。
- 现有断言 `test/unit/okxsdk/test_okxclient.py:83`（`json.loads(request.content)`）与 `test_transport.py:162`（`assertEqual(seen[0].content, POST_BODY)`）读的都是 `.content`，两种写法都满足。

## 建议方案

把 `data=body` 改成 `content=body`，一行；其余不动。不加兼容分支、不引入新参数、不改公开 API。
可选项（单独评估）：CI 里加 `pytest -W error::DeprecationWarning` 防回归；若与 pytest-asyncio 自身的 `asyncio_default_fixture_loop_scope` 告警冲突，则只在 `test_transport.py` 范围内收紧，不强行全仓。

## 验收标准

1. `pytest -W error::DeprecationWarning` 下这 12 条告警消失（或明确记录剩余告警来源及豁免理由）。
2. `test_transport.py`、`test_okxclient.py` 的 POST body 断言仍通过。
3. `ruff check okxsdk/` 通过；`pytest` 全绿。
4. 不写 ADR：内部实现修复，不涉公共契约（参照 r3/01 的先例）。

## Answer

**施工完成（2026-11-06，已提交 `a464c12`）。**

- `okxsdk/transport.py:161` 的 `data=body` 改为 `content=body`，一行；其余不动。
- 新增 `test/unit/okxsdk/test_transport.py::TestPostBodyEncoding.test_post_does_not_emit_the_httpx_data_deprecation`：用 `warnings.catch_warnings` 捕获 POST 期间的 DeprecationWarning，断言不含 httpx 的 `content=<...>` 告警。**改动前红**（捕到 `Use 'content=<...>' to upload raw bytes/text content.`），**改动后绿**——TDD 先行。
- 验收：`pytest` 852 passed / 336 subtests；`ruff check okxsdk/` 通过；普通跑法已无 warnings summary（原 12 条 httpx 告警全消失）；`pytest -q -W error::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning` 全仓 852 passed。
- 裸 `-W error::DeprecationWarning` 会撞上 pytest-asyncio 在 `pytest_configure` 阶段的 `asyncio_default_fixture_loop_scope` 未设置告警（`INTERNALERROR`），与被测代码无关；按本单预留的豁免口径记录，未改 `pytest.ini`。
- 已提交于 `a464c12`，Status 转 `resolved`，`Done in:` 见文件头。

## Comments

- 2026-11-06 审查提出：P1。修复最小、零测试改动。
- 2026-11-06 用户确认机械项，直接施工；TDD 红→绿，已提交 `a464c12`。

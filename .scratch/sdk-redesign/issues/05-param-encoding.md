# 修复 GET 参数编码

Status: ready-for-agent
Release: 0.4.5

## 为什么

`utils.parse_params_to_str`（`okx/utils.py:42`）手工拼接查询串：不做 URL 编码，bool 序列化成 `True`，含空格或 `&` 的参数值会被静默截断。

## 做什么

用 `urllib.parse.urlencode` 或等价实现替换，bool 转 `true`/`false`。不改动 `''` 被丢弃的现有语义——那条留到 0.5.0。

## 完成标准

构造含空格、`&`、bool 的参数时，请求路径可被正确解析；新增对应单测。

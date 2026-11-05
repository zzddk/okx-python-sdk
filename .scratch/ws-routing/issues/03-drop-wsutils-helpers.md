# 删除 WsUtils 的订阅参数校验死代码

Status: ready-for-agent
Release: 0.14.0（原定 0.12.0）

## 为什么

`WsUtils.py` 的 `checkSocketParams` / `initSubscribeSet` / `getParamKey` 在生产代码里零调用：`grep -rn "checkSocketParams\|initSubscribeSet\|getParamKey" --include=*.py okx/` 无输出。唯一的使用者是 `test_ws_hardening.py:21-33`，直接测这些函数本身。`getParamKey` 用 `"@" + str(arg[k])` 拼键且跳过 `channel`，不同频道同形参数会碰撞；`checkSocketParams` 先 `.strip()` 再判空，`channel` 缺失时抛的是 `KeyError` 而不是 `ValueError`。与其修，不如删——路由现在由 `Subscriptions` 负责，这里不再有第二套订阅语义。

## 做什么

删除 `WsUtils.checkSocketParams`、`initSubscribeSet`、`getParamKey`、`isNotBlankStr`（仅被前者与测试使用）。`WsUtils.py` 只留 `initLoginParams` 与 `getLocalTime`。删除 `test_ws_hardening.py` 的 `TestIsNotBlankStr` 整个类。

## 完成标准

1. `grep -rn "checkSocketParams\|initSubscribeSet\|getParamKey\|isNotBlankStr" --include=*.py okx/ test/` 无命中。
2. `WsUtils.py` 只导出 `initLoginParams`、`getLocalTime`；文件不再 import `Optional`/`Set` 中已不用的名字。
3. `test_ws_hardening.py` 少 4 个用例，其余登录相关用例不改。
4. `env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy python -m pytest test/unit -q`：617 - 4 = 613 passed（若 01 已合并则加上其新增数）。

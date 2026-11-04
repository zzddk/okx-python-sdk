# 拆分 consts 为子包

Status: resolved
Release: 0.5.0
Done in: 0.5.0

## 为什么

`okx/consts.py` 345 行混了 HTTP 头名、GET/POST、凭证哨兵和全部端点路径，重名冲突正是发生在这里。

## 做什么

拆为 `okx/consts/` 子包（`http.py`、`endpoints/*.py`），`okx/consts/__init__.py` 继续 re-export 全部名字，保持 `import *` 与 `c.POSITION_RISK` 可用。

## 完成标准

外部 `from okx import consts as c; c.POSITION_RISK` 不变；重名会在 `__init__.py` 里变成显式错误而不是静默覆盖。

## Comments

- 2026-11-05: done in 0.5.0. `okx/consts.py` split into `okx/consts/http.py` + `okx/consts/endpoints/*.py`; `__init__.py` merges with duplicate detection. All 293 previous names remain resolvable (`_NO_CREDENTIAL` stays private but is still exposed as `consts._NO_CREDENTIAL`). Contract test now scans the package and checks cross-module uniqueness.

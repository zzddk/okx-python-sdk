# 清除可变默认参数

Status: resolved
Release: 0.4.5
Done in: 0.5.0

## 为什么

12 处 `def f(..., x=[])`（`Trade.py:175`、`Trade.py:196`、`Trade.py:229`、`Grid.py:83`、`SubAccount.py:63`、`Finance/FlexibleLoan.py:19`、`Finance/StakingDefi.py:17`、`Account.py:163`、`BlockTrading.py:13`、`BlockTrading.py:23`、`BlockTrading.py:31`、`BlockTrading.py:35`）共享同一个 list 实例。当前调用方没有就地修改，所以还没炸，但这是定时炸弹。

## 做什么

默认值改 `None`，函数体内按需替换为 `[]`。

## 完成标准

`grep -rnE 'def .*=\[\]' okx/` 无输出；现有单测全部通过。

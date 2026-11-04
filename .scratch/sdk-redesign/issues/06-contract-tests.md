# 建立 contract 测试层

Status: resolved
Release: 0.4.5
Done in: 0.5.0

## 为什么

现有单测只 mock `_request_with_params` 并断言传进去的 dict，没有一层测试「整个调用最终打到哪个 path」。所以 01 里的常量覆盖 bug 至今没被发现。

## 做什么

参数化遍历所有 `*API` 类的方法，断言解析出的 `(HTTP method, path)` 落在常量值集合内；并断言常量名唯一。

## 完成标准

人为制造一个重名常量或错误 path，测试必须失败。

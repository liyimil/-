# expression_engine

课题 C：规则分析与表达式引擎模块。

职责：

- 解析 SKILL 中的 `expression`。
- 支持时间窗口、同设备约束和告警组合判断。
- 输出规则是否触发、命中条件和原因。

第一版优先支持：

```text
A & B & C within Ns on same_device
```


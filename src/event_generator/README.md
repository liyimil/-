# event_generator

课题 D：标准事件生成模块。

职责：

- 根据 C 的规则判定结果生成标准事件对象。
- 生成事件摘要。
- 输出前端可展示的事件结果。

主要输入：

```text
rule_results
rules.json 中的 event_type / event_level / output_format
matched_alarms
matched_features
```

主要输出：

```text
StandardEvent
```

标准事件格式以 `contracts/module_contracts.md` 为准。

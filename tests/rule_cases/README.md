# rule_cases

课题 C 使用本目录维护表达式解析与求值用例。

建议按表达式形态组织用例：

```text
AND_OR_GROUP
NOT_CONDITION
SINGLE_FEATURE
LONG_COMBINATION
```

用例应覆盖：

- `feature.expression`
- `rule.expression`
- `signal_mapping_states -> feature_states`
- `feature_states -> rule_results`


# expression_engine

课题 C：规则分析与表达式引擎模块。

职责：

- 解析并求值 `feature.expression`。
- 解析并求值全量 `rule.expression`。
- 基于 B 输出的 `signal_mapping_states` 计算 `feature_states`。
- 基于 `feature_states` 计算 `rule_results`。
- 支持 `&`、`|`、`!`、括号、`@1=1` 等表达式。

主要输入：

```text
signal_mapping_states
Feature SKILL
Rule SKILL
```

主要输出：

```text
feature_states
rule_results
```

注意：

- `rule.expression` 里的 `@n` 对应 `features.feature_id=@n`。
- `feature.expression` 里的 `@n` 对应该 feature 内部的 `signal_mappings.index=@n`。

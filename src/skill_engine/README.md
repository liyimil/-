# skill_engine

课题 B：SKILL 规则管理与智能匹配模块。

职责：

- 读取 `features.json` 和 `rules.json`。
- 管理 `skills/` 下的 Feature SKILL / Rule SKILL。
- 将具体告警与 feature 内部的 `signal_mappings` 做运行时语义匹配。
- 输出 `signal_mapping_states`。
- 输出候选 Feature SKILL / Rule SKILL。

主要输入：

```text
A 的结构化告警
data/samples/samples-md/features.json
data/samples/samples-md/rules.json
```

主要输出：

```text
candidate_feature_skills
candidate_rule_skills
signal_mapping_states
```

注意：

- `signal_mapping_states` 的外层 key 是 `feature_id`。
- 内层 key 是该 feature 内部的 `signal_mappings.index`。

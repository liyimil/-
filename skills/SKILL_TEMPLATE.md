# SKILL 模板

当前系统建议使用两类 SKILL：Feature SKILL 和 Rule SKILL。

## Feature SKILL 模板

````markdown
# FEATURE SKILL: 特征名称

## metadata

- skill_id:
- source_feature_id:
- type: feature
- scope:
- valid_time:
- priority:

## source

- source_file: features.json

## expression

```text
@1=1
```

## signal_mappings

| index | object_type | object_name | signal_feature | feature_desc |
|---|---|---|---|---|
| @1 |  |  |  |  |

## explanation

解释该特征代表的业务含义。
````

## Rule SKILL 模板

````markdown
# RULE SKILL: 规则名称

## metadata

- skill_id:
- source_rule_id:
- type: event_rule
- event_level:
- event_type:
- valid_time:
- enabled:

## source

- source_file: rules.json

## expression

```text
(@1|@2)&@3&(@4|@5|@6)
```

## output_format

```text
$LINE 线路故障（远方手合）
```

## explanation

解释该规则触发后表示什么业务事件。
````

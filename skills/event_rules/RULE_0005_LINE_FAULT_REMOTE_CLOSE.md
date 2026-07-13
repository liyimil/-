# RULE SKILL: [精准]20kV线路故障（远方手合）

## metadata

- skill_id: RULE_0005_LINE_FAULT_REMOTE_CLOSE
- source_rule_id: "5"
- type: event_rule
- event_level: 事故
- event_type: 2-跳闸事件
- valid_time: 10
- sub_type: 综合事件规则
- run_mode: "@ULL/"
- enabled: true

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

## variable_mapping_status

当前数据集中 `feature_refs` 为空，因此本规则中 `@1`、`@2`、`@3`、`@4`、`@5`、`@6` 与特征或告警信号的映射关系需要进一步向企业确认。

第一版实现中，该 SKILL 主要用于验证表达式解析、SKILL 加载和事件输出格式。

## explanation

该规则用于识别 20kV 线路故障中的远方手合场景。表达式表示：`@1` 或 `@2` 至少满足一个，同时 `@3` 必须满足，并且 `@4`、`@5`、`@6` 至少满足一个。满足后输出事件类型为跳闸事件，事件等级为事故。


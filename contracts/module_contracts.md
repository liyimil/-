# A/B/C/D 模块接口契约

本文件用于约定四个课题之间的数据接口。当前接口基于 `data/samples/samples-md` 中的真实样例设计。

## 1. A 输出：结构化告警

```json
{
  "dataset_id": "samples-md",
  "alarms": [
    {
      "alarm_id": "ALM-004",
      "station_name": "示例厂站",
      "device_name": "",
      "voltage_level": "",
      "signal_value": 1,
      "raw_signal_name": "2023年08月29日 17:09:11 20kV示范变电站 101开关 分闸",
      "parsed": {
        "alarm_time": "2023-08-29 17:09:11",
        "station_name": "20kV示范变电站",
        "voltage_level": "20kV",
        "object_name": "101开关",
        "action": "分闸"
      }
    }
  ]
}
```

## 2. B 输出：候选 SKILL

```json
{
  "dataset_id": "samples-md",
  "candidate_feature_skills": [
    {
      "skill_id": "FEATURE_012",
      "source_feature_id": "@12",
      "feature_name": "特征_694",
      "skill_path": "skills/features/FEATURE_012.md",
      "match_score": 0.82,
      "match_reason": "候选告警包含保护装置A网通信中断相关文本"
    }
  ],
  "candidate_rule_skills": [
    {
      "skill_id": "RULE_0005",
      "source_rule_id": "5",
      "rule_name": "[精准]20kV线路故障（远方手合）",
      "skill_path": "skills/event_rules/RULE_0005.md",
      "match_score": 0.76,
      "match_reason": "规则类型为线路故障，表达式结构清晰，适合作为首批验证规则"
    }
  ],
  "signal_mapping_states": {
    "@1": {
      "@1": true,
      "@2": false,
      "@3": false,
      "@4": true,
      "@5": true,
      "@6": false
    },
    "@2": {
      "@1": false
    }
  }
}
```

说明：外层 `@1` 是 `feature_id`，内层 `@1/@2` 是该 feature 内部 `signal_mappings.index`。

## 3. C 输出：表达式求值结果

```json
{
  "dataset_id": "samples-md",
  "feature_states": {
    "@1": true,
    "@2": false,
    "@3": true,
    "@4": true,
    "@5": false,
    "@6": false
  },
  "rule_results": [
    {
      "source_rule_id": "5",
      "rule_name": "[精准]20kV线路故障（远方手合）",
      "expression": "(@1|@2)&@3&(@4|@5|@6)",
      "triggered": true,
      "matched_variables": ["@1", "@3", "@4"],
      "unmatched_variables": [],
      "event_level": "事故",
      "event_type": "2-跳闸事件",
      "output_format": "$LINE 线路故障（远方手合）",
      "reason": "表达式求值结果为 true。"
    }
  ]
}
```

## 4. D 输出：标准事件

```json
{
  "events": [
    {
      "event_id": "EVT-0001",
      "source_rule_id": "5",
      "event_type": "2-跳闸事件",
      "event_level": "事故",
      "output_text": "线路故障（远方手合）",
      "matched_alarms": ["ALM-001", "ALM-002"],
      "matched_features": ["@1", "@3", "@4"],
      "summary": "系统根据规则 [精准]20kV线路故障（远方手合）识别出跳闸事件。"
    }
  ]
}
```

## 5. 接口变更规则

- 新字段可以追加，但不要删除已有字段。
- 原始字段必须保留，例如 `raw_signal_name`、`source_rule_id`。
- 解析字段放入 `parsed`，不要覆盖原始告警。
- 老师已确认：`rules.expression` 中的 `@n` 直接对应 `features.json` 中 `feature_id=@n` 的特征。
- 老师已确认：`feature.expression` 中的 `@n` 是 feature 内部局部索引，对应该 feature 的 `signal_mappings.index=@n`。
- C 模块先基于 B 输出的 `signal_mapping_states` 求值 `feature.expression` 得到 `feature_states`，再基于 `feature_states` 求值 `rules.expression`。

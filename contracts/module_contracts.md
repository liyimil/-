# A/B/C/D 模块接口契约

本文件用于约定四个课题之间的数据接口。除非组长统一更新，所有模块优先保持这些字段不变。

## 1. A 输出：结构化告警序列

```json
{
  "sequence_id": "SEQ_001",
  "scenario": "线路故障",
  "alarms": [
    {
      "alarm_id": "A001",
      "timestamp": "2026-07-07 10:00:01",
      "device_id": "LINE_01",
      "device_name": "10kV 一线",
      "alarm_code": "CURRENT_OVER_LIMIT",
      "alarm_name": "线路电流越限",
      "alarm_level": "重要",
      "status": "发生",
      "source_system": "SCADA"
    }
  ],
  "features": {
    "alarm_codes": ["CURRENT_OVER_LIMIT"],
    "device_ids": ["LINE_01"],
    "time_span_seconds": 1,
    "alarm_count": 1
  }
}
```

## 2. B 输出：候选 SKILL

```json
{
  "sequence_id": "SEQ_001",
  "candidate_skills": [
    {
      "skill_id": "EVENT_LINE_FAULT",
      "skill_name": "线路故障事件识别",
      "skill_path": "skills/event_rules/EVENT_LINE_FAULT.md",
      "match_score": 0.95,
      "match_reason": "告警序列包含线路故障相关告警代码"
    }
  ]
}
```

## 3. C 输出：规则判定结果

```json
{
  "sequence_id": "SEQ_001",
  "rule_results": [
    {
      "skill_id": "EVENT_LINE_FAULT",
      "triggered": true,
      "matched_conditions": [
        "CURRENT_OVER_LIMIT",
        "PROTECTION_ACTION",
        "BREAKER_TRIP"
      ],
      "unmatched_conditions": [],
      "constraints": {
        "within_seconds": 30,
        "same_device": true
      },
      "actual": {
        "time_span_seconds": 8,
        "device_id": "LINE_01"
      },
      "confidence": 0.93,
      "reason": "同一设备在 8 秒内满足线路故障事件规则。"
    }
  ]
}
```

## 4. D 输出：标准事件

```json
{
  "events": [
    {
      "event_id": "E001",
      "event_type": "线路故障事件",
      "event_level": "高",
      "push_priority": "优先推送",
      "start_time": "2026-07-07 10:00:01",
      "end_time": "2026-07-07 10:00:08",
      "device_id": "LINE_01",
      "matched_alarms": ["A001", "A002", "A003"],
      "matched_skill": "EVENT_LINE_FAULT",
      "summary": "同一线路在 8 秒内连续出现电流越限、保护动作和开关跳闸，判定为线路故障事件。"
    }
  ]
}
```

## 5. 接口变更规则

- 字段变更必须先同步组长。
- 新字段可以追加，但不要随意删除已有字段。
- 每个模块必须保留可独立测试的输入输出样例。
- 集成时优先使用 `tests/golden_cases` 中的样例。


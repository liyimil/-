# SKILL: 线路故障事件识别

## metadata

- skill_id: EVENT_LINE_FAULT
- type: event_rule
- domain: power_grid_alarm
- priority: high
- related_alarm_codes:
  - CURRENT_OVER_LIMIT
  - PROTECTION_ACTION
  - BREAKER_TRIP

## description

用于识别同一线路在短时间内连续出现电流越限、保护动作和开关跳闸时形成的线路故障事件。

## trigger_conditions

- 时间窗口：30 秒内
- 设备约束：同一 device_id
- 必要告警：
  - CURRENT_OVER_LIMIT
  - PROTECTION_ACTION
  - BREAKER_TRIP
- 可选告警：无
- 排除条件：关键告警来自不同设备，或告警时间跨度超过 30 秒

## expression

```text
CURRENT_OVER_LIMIT & PROTECTION_ACTION & BREAKER_TRIP within 30s on same_device
```

## output

- event_type: 线路故障事件
- event_level: 高
- push_priority: 优先推送

## explanation

当同一线路短时间内连续出现电流越限、保护动作和开关跳闸，通常说明该线路存在较严重故障，需要优先推送给调度人员并进行人工确认。


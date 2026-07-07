# SKILL: 规则名称

## metadata

- skill_id:
- type: event_rule
- domain: power_grid_alarm
- priority:
- related_alarm_codes:
  -

## description

说明该 SKILL 用于识别什么告警模式或事件类型。

## trigger_conditions

- 时间窗口：
- 设备约束：
- 必要告警：
- 可选告警：
- 排除条件：

## expression

```text
A & B & C within Ns on same_device
```

## output

- event_type:
- event_level:
- push_priority:

## explanation

用自然语言解释为什么这些告警组合会形成该事件，以及该事件为什么需要关注。


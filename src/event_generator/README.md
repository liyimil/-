# event_generator

课题 D：标准事件生成模块。

## 负责范围

- 读取 C 模块输出的 `rule_results`。
- 只对 `triggered=true` 的规则生成标准事件。
- 根据 `output_format` 渲染事件文本，例如 `$LINE 线路故障（远方手合）`。
- 汇总 `matched_alarms`、`matched_features`、事件等级和事件类型，输出给编排层和前端。

## 当前文件

- `event_generator.py`：事件生成主逻辑。
- `__init__.py`：导出 `generate_events`。

## 输入

主要来自 C 模块：

```json
{
  "rule_results": [
    {
      "source_rule_id": "5",
      "triggered": true,
      "matched_variables": ["@1", "@3", "@4"],
      "event_level": "事故",
      "event_type": "2-跳闸事件",
      "output_format": "$LINE 线路故障（远方手合）",
      "matched_alarms": ["ALM-001", "ALM-004"]
    }
  ]
}
```

## 输出

```json
{
  "events": [
    {
      "event_id": "EVT-0001",
      "source_rule_id": "5",
      "event_type": "2-跳闸事件",
      "event_level": "事故",
      "output_text": "20kV示范变电站101线路 线路故障（远方手合）",
      "matched_alarms": ["ALM-001", "ALM-004"],
      "matched_features": ["@1", "@3", "@4"]
    }
  ]
}
```

标准事件字段以 `contracts/module_contracts.md` 为准。

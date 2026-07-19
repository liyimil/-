# FEATURE SKILL: 10kV线路保护通道全部退出

## metadata

- skill_id: FEATURE_001
- source_feature_id: @1
- type: feature
- scope: 同间隔
- valid_time: 300
- priority: 0

## source

- source_file: features.json

## expression

```text
(@1&@2&@4&@5)|(@3&@6)
```

## signal_mappings

| index | object_type | device_name | object_name | signal_feature | feature_desc |
|---|---|---|---|---|---|
| @1 | 第一套线路保护 | 第一套线路保护 | 保护通道A异常 | 10kV线路保护通道全部退出 | 10kV线路保护通道全部退出 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「10kV线路保护通道全部退出」场景。

作用域为「同间隔」。

当告警信号涉及以下对象时触发：保护通道A异常。

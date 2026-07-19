# FEATURE SKILL: 特征_809

## metadata

- skill_id: FEATURE_006
- source_feature_id: @6
- type: feature
- scope: 同间隔
- valid_time: 300
- priority: 0

## source

- source_file: features.json

## expression

```text
@1=1
```

## signal_mappings

| index | object_type | device_name | object_name | signal_feature | feature_desc |
|---|---|---|---|---|---|
| @1 | 第二套线路保护 | 第二套线路保护 | 保护通道异常 | 特征_809 | 特征_809 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「特征_809」场景。

作用域为「同间隔」。

当告警信号涉及以下对象时触发：保护通道异常。

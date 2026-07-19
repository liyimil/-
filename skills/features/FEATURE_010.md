# FEATURE SKILL: 特征_801

## metadata

- skill_id: FEATURE_010
- source_feature_id: @10
- type: feature
- scope: 同厂站
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
| @1 | 空 | 空 | 直流系统充电机交流输入故障 | 特征_801 | 特征_801 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「特征_801」场景。

作用域为「同厂站」。

当告警信号涉及以下对象时触发：直流系统充电机交流输入故障。

# FEATURE SKILL: 特征_141

## metadata

- skill_id: FEATURE_022
- source_feature_id: @22
- type: feature
- scope: 同20kV主变
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
| @1 | 断路器位置 | 断路器位置 | 开关C相 | 特征_141 | 特征_141 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「特征_141」场景。

作用域为「同20kV主变」。

当告警信号涉及以下对象时触发：开关C相。

# FEATURE SKILL: 特征_280

## metadata

- skill_id: FEATURE_280
- source_feature_id: 280
- type: feature
- scope:
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
| @1 | 空 | 空 | 失灵保护出口 | 特征_280 | 特征_280 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「特征_280」场景。

当告警信号涉及以下对象时触发：失灵保护出口。

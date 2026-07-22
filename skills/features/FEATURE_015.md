# FEATURE SKILL: 特征_697

## metadata

- skill_id: FEATURE_015
- source_feature_id: @15
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
| @1 | 空 | 空 | 保护装置B网通信中断 | 特征_697 | 特征_697 |

说明：这里的 `@N` 是该 Feature SKILL 内部的局部 signal_mapping 索引，对应该 feature 的 `signal_mappings.index=@N`。

## explanation

该特征用于识别「特征_697」场景。

作用域为「同厂站」。

当告警信号涉及以下对象时触发：保护装置B网通信中断。

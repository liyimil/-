# alarm_generator

课题 A：告警数据生成模块。

职责：

- 基于 `data/samples/samples-md/alarms.json` 的真实格式生成扩展告警数据。
- 输出到 `data/generated/`。
- 生成的数据字段应尽量保持与原始 `alarms.json` 一致。

注意：

- 第一优先级是配合 `perception_agent` 解析真实样例。
- 数据生成是后续扩展，不要改变原始样例文件。

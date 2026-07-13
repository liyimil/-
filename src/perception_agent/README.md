# perception_agent

课题 A：感知预处理模块。

职责：

- 读取 `data/samples/samples-md/alarms.json`。
- 保留原始 `signal_name`。
- 从 `signal_name` 中解析时间、厂站、电压等级、设备对象、动作状态。
- 输出符合 `contracts/module_contracts.md` 的结构化告警 JSON。

主要输入：

```text
data/samples/samples-md/alarms.json
```

主要输出：

```text
StructuredAlarm
```

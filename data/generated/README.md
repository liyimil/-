# generated 目录说明

用于存放模拟数据生成器输出的数据。

建议命名：

```text
SEQ_001_line_fault.json
SEQ_002_noise.json
SEQ_003_timeout.json
```

---

## 结构化告警输出格式（`structured_alarms.json`）

课题 A 的 `perception_agent` 解析 `alarms.json` 后输出到此。
输出采用**双层兼容**：保留契约字段（`raw_signal_name` + `parsed`），同时提供扁平字段（`device`、`signal_type`、`time_delta`）供 `@N` 索引直接取用。

### 顶层结构

```json
{
  "dataset_id": "samples-md",
  "source_file": "alarms.json",
  "total_count": "<告警总数>",
  "valid_count": "<有效告警数>",
  "generated_at": "<ISO 8601 时间戳>",
  "alarms": [ ... ]
}
```

### 单条告警结构（双层兼容）

```json
{
  "alarm_id": "<原始ID>",
  "_contract_fields": "── 契约字段（contracts/module_contracts.md）──",
  "station_name": "<原始厂站>",
  "device_name": "<原始设备>",
  "voltage_level": "<原始电压等级>",
  "signal_value": 1,
  "raw_signal_name": "<原始 signal_name 文本>",
  "parsed": {
    "alarm_time": "YYYY-MM-DDTHH:MM:SS",
    "station_name": "<解析后厂站>",
    "voltage_level": "<解析后电压等级>",
    "object_name": "<解析后设备名>",
    "action": "<解析后动作>"
  },
  "_flat_fields": "── 扁平字段（课题 B/C 用 @N 直接索引）──",
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "device": "<设备名>",
  "signal_type": "<标准化枚举>",
  "action": "<中文动作>",
  "station": "<厂站>",
  "is_valid": true,
  "raw_signal": "<原始 signal_name>",
  "time_delta": 5.0
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `alarm_id` | string | 原始告警 ID |
| `timestamp` | string\|null | 解析后时间，`YYYY-MM-DDTHH:MM:SS`（ISO 8601） |
| `device` | string\|null | 设备/对象名，课题 B/C 用 `@N.device` 索引 |
| `signal_type` | string | 标准化信号枚举，课题 B/C 用 `@N.signal_type` 匹配 |
| `action` | string\|null | 中文动作描述 |
| `station` | string\|null | 厂站全名（含电压前缀） |
| `voltage_level` | string\|null | 电压等级，如 `20kV` |
| `raw_value` | int | 原始信号值 |
| `is_valid` | bool | 是否通过合法性校验，下游应过滤 `is_valid=False` 的告警 |
| `raw_signal` | string | 原始 `signal_name` 文本，供课题 B 语义匹配 |
| `time_delta` | float\|null | 距上一条有效告警的秒数，课题 C 用 `@N.time_delta` 做时间窗口 |

### `signal_type` 枚举表

| 枚举值 | 含义 | 触发条件 |
|---|---|---|
| `NETWORK_A_DOWN` | A网中断 | action 含 `A网中断`（优先级最高） |
| `NETWORK_B_DOWN` | B网中断 | action 含 `B网中断` |
| `NETWORK_C_DOWN` | C网中断 | action 含 `C网中断` |
| `BREAKER_OPEN` | 开关分闸 | 设备含"开关" + 分闸 |
| `BREAKER_CLOSE` | 开关合闸 | 设备含"开关" + 合闸 |
| `DISCONNECTOR_OPEN` | 刀闸分闸 | 设备含"刀闸" + 分闸 |
| `DISCONNECTOR_CLOSE` | 刀闸合闸 | 设备含"刀闸" + 合闸 |
| `PROTECTION_TRIP` | 保护动作 | 设备含"保护" + 动作 |
| `PROTECTION_RESET` | 保护复归 | 设备含"保护" + 复归 |
| `CTRL_ACTIVE` | 测控动作 | 设备含"测控" + 动作 |
| `CTRL_RESET` | 测控复归 | 设备含"测控" + 复归 |
| `GENERAL_TRIP` | 通用动作 | 兜底匹配 |
| `UNKNOWN` | 未识别 | 无设备或无动作 |

### 接口约定

- 同时保留契约字段（`raw_signal_name` + `parsed`）和扁平字段，B 按契约读取、C 优先使用 `@N.device` / `@N.signal_type` / `@N.time_delta`。
- `is_valid=False` 的告警（如"测试信号1"）已被标记，下游应过滤。
- `raw_signal_name` 保留原始文本，供课题 B 做 `signal_mappings` 语义匹配。
- 数组按 `timestamp` 升序排列（`null` 在最前）。


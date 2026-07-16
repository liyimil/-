# perception_agent

课题 A：感知预处理模块。

职责：

- 读取 `data/samples/alarms.json`。
- 保留原始 `signal_name`。
- 从 `signal_name` 中解析时间、厂站、电压等级、设备对象、动作状态。
- 输出符合 `contracts/module_contracts.md` 的结构化告警 JSON。
- 同时输出扁平字段（`device`、`signal_type`、`time_delta`）供 `@N` 索引使用。

主要输入：

```text
data/samples/alarms.json（默认）
```

主要输出：

```text
data/generated/structured_alarms.json

双层兼容格式：
- 契约字段：alarm_id / station_name / device_name / voltage_level /
            signal_value / raw_signal_name / parsed{...}
- 扁平字段：timestamp / device / signal_type / action / station /
            voltage_level / is_valid / raw_signal / time_delta
```

---

## `signal_name` 解析规则

### 解析流程

```text
原始 signal_name 文本
  │
  ├─ 步骤1: 正则匹配时间 → 提取 alarm_time，移除时间片段
  │   格式: YYYY年MM月DD日 HH:MM:SS
  │   输出: "YYYY-MM-DDTHH:MM:SS"（ISO 8601，兼容 Python 3.10+）
  │
  ├─ 步骤2: 正则匹配厂站名 → 提取 station_name 和 voltage_level
  │   模式: [电压前缀] + "变电站"
  │   示例: "XXkV某变电站" → station_name="XXkV某变电站", voltage="XXkV"
  │
  ├─ 步骤3: 尾部匹配动作词 → 提取 action
  │   按长度降序匹配，确保 "动作(全数据判定)" 优先于 "动作"
  │
  └─ 步骤4: 剩余文本 → object_name
       去除时间、厂站、动作后的中间部分即为设备/对象名
```

### 正则规则

| 步骤 | 正则表达式 | 说明 |
|---|---|---|
| 时间提取 | `(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(\d{1,2}):(\d{2}):(\d{2})` | 匹配中文日期格式，标准化为 `YYYY-MM-DDTHH:MM:SS`（ISO 8601） |
| 厂站提取 | `(\d+kV)?\s*([\u4e00-\u9fa5]+变电站)` | 匹配可选电压前缀 + 以"变电站"结尾的中文名 |
| 电压补充 | `(\d+kV)` | 独立匹配电压等级，厂站提取失败时兜底 |

### 动作词表（按长度降序，长匹配优先）

```text
动作(全数据判定)
  > 测控A网中断 / 测控B网中断 / 测控C网中断
  > 保护A网中断 / 保护B网中断 / 保护C网中断
  > A网中断 / B网中断 / C网中断
  > 动作 / 复归 / 分闸 / 合闸
  > 异常 / 故障 / 投入 / 退出 / 告警 / 恢复 / 接通 / 断开
```

策略：`rfind` 从文本末尾查找，同位置取更长词。

### 解析示例

| 输入 signal_name（模板） | alarm_time | station_name | voltage | object_name | action |
|---|---|---|---|---|---|
| `{时间} XXkV某变电站 某线路保护A网中断 动作(全数据判定)` | YYYY-MM-DDTHH:MM:SS | XXkV某变电站 | XXkV | 某线路保护A网中断 | 动作(全数据判定) |
| `{时间} XXkV某变电站 某开关 分闸` | YYYY-MM-DDTHH:MM:SS | XXkV某变电站 | XXkV | 某开关 | 分闸 |
| `{时间} XXkV某变电站 某开关 合闸` | YYYY-MM-DDTHH:MM:SS | XXkV某变电站 | XXkV | 某开关 | 合闸 |
| `测试信号N`（占位数据） | null | null | null | 测试信号N | null |

### 边界情况

| 情况 | 处理方式 |
|---|---|
| 无时间字段 | `alarm_time` 为 `null`，继续解析 |
| 无"变电站"后缀 | `station_name` 为 `null`，从全文提取 `voltage_level` |
| 无匹配动作词 | `action` 为 `null`，不做猜测（避免误吞设备名末尾字符） |
| 剩余文本为空 | 回退到从原始文本剔除时间、厂站、动作后推断 |
| 电压等级缺失 | 从原始 `signal_name` 全文搜 `\d+kV` 补充 |

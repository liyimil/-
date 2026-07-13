# 项目实施计划：基于 AI Agent 的电网告警事件分析系统

整理日期：2026-07-13  
当前依据：`data/samples/samples-md` 数据集

## 1. 项目目标

实现一个面向电网告警事件分析的原型系统，围绕真实数据集中的 `alarms.json`、`features.json` 和 `rules.json`，完成告警解析、特征映射、SKILL 规则管理、表达式求值、多智能体编排和标准事件生成。

最终闭环：

```text
导入 alarms/features/rules
  -> 解析告警 signal_name
  -> 告警与 signal_mappings 运行时语义匹配
  -> 求值 feature.expression 形成 feature_states
  -> 加载 Feature SKILL / Rule SKILL
  -> 求值 rule.expression
  -> 输出事件类型、等级和格式化结果
  -> 前端展示和报告输出
```

## 2. 系统架构

```text
┌──────────────────────────────────────────┐
│ A. 告警数据感知与预处理                    │
│ 读取 alarms.json，解析 signal_name，结构化告警 │
└──────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│ B. SKILL 规则管理与智能匹配                │
│ 管理 Feature SKILL / Rule SKILL，筛选候选规则 │
└──────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│ C. 规则分析与表达式引擎                    │
│ 解析 @n、&、|、!、括号和 valid_time 等规则     │
└──────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│ D. 事件生成、调度编排与可视化               │
│ 编排 A/B/C，生成标准事件和分析报告           │
└──────────────────────────────────────────┘
```

## 3. 数据输入

### 3.1 alarms.json

用途：提供原始告警采样数据。

关键字段：

```text
alarm_id
station_name
device_name
signal_name
signal_value
voltage_level
alarm_time
alarm_level
```

第一版重点处理 `signal_name`，从中抽取时间、厂站、设备、动作状态等信息。

### 3.2 features.json

用途：提供特征定义。

关键字段：

```text
feature_id
feature_name
expression
scope
valid_time
signal_mappings
```

`signal_mappings` 是 feature 内部的信号模式模板。运行时需要将具体告警 `alarm.signal_name` 与这些模板做语义匹配，得到 feature 内部局部变量状态，再由 `feature.expression` 计算该 feature 是否触发。

### 3.3 rules.json

用途：提供事件规则。

关键字段：

```text
rule_id
rule_name
expression
event_level
event_type
output_format
valid_time
enabled
```

规则表达式是 C 模块的核心输入。

## 4. 课题 A：告警数据感知与预处理

### 4.1 目标

读取 `alarms.json`，清洗原始告警字段，并从 `signal_name` 中抽取结构化信息。

### 4.2 功能

- 加载 `alarms.json`。
- 校验字段完整性。
- 解析 `signal_name`。
- 抽取告警时间、厂站、电压等级、设备对象、动作状态。
- 保留原始告警文本。
- 输出结构化告警列表。
- 后续基于真实格式扩展模拟数据。

### 4.3 输出示例

```json
{
  "alarm_id": "ALM-004",
  "raw_signal_name": "2023年08月29日 17:09:11 20kV示范变电站 101开关 分闸",
  "parsed": {
    "alarm_time": "2023-08-29 17:09:11",
    "station_name": "20kV示范变电站",
    "voltage_level": "20kV",
    "object_name": "101开关",
    "action": "分闸"
  },
  "signal_value": 1
}
```

### 4.4 交付物

- 告警字段说明。
- `signal_name` 解析规则。
- 结构化告警输出格式。
- 基于真实样本的数据扩展方案。

## 5. 课题 B：SKILL 规则管理与智能匹配

### 5.1 目标

将 `features.json` 和 `rules.json` 中的特征、规则封装为可加载的 SKILL，并建立索引以支持候选特征和候选规则筛选。

### 5.2 功能

- 设计 Feature SKILL 模板。
- 设计 Rule SKILL 模板。
- 将 `features.json` 中的特征定义转为 Feature SKILL。
- 将 `rules.json` 中的事件规则转为 Rule SKILL。
- 根据告警文本、对象类型、动作状态与 `signal_mappings` 做运行时语义匹配，输出 `signal_mapping_states`。
- 输出候选 Feature SKILL / Rule SKILL。

### 5.3 SKILL 类型

```text
Feature SKILL：
  来源 features.json
  重点封装 feature_name、expression、scope、valid_time、signal_mappings

Rule SKILL：
  来源 rules.json
  重点封装 rule_name、expression、event_level、event_type、output_format、valid_time
```

### 5.4 交付物

- SKILL 文件规范。
- Feature SKILL 样例。
- Rule SKILL 样例。
- SKILL 索引格式。
- 候选 SKILL 匹配结果格式。

## 6. 课题 C：规则分析与表达式引擎

### 6.1 目标

实现特征表达式和事件规则表达式的解析与求值，判断特征是否成立、事件规则是否触发。

### 6.2 功能

- 解析 `@1=1`。
- 解析 `&`、`|`、`!`。
- 支持括号优先级。
- 处理英文括号和中文括号。
- 支持 `valid_time` 时间窗口。
- 输出命中条件、未命中条件、触发结果。
- 将 `rules.expression` 中的 `@n` 直接绑定到 `features.json` 中 `feature_id=@n` 的特征。
- 区分两层变量：`feature.expression` 中的 `@n` 是 feature 内部局部 signal_mapping 索引；`rule.expression` 中的 `@n` 是全局 feature_id。
- 基于 `signal_mapping_states` 求值 `feature.expression`，得到 `feature_states`。
- 基于 `feature_states` 求值 `rule.expression`，得到事件规则触发结果。

### 6.3 第一版优先支持

```text
@1=1
@1&@2
@1|@2
!@1
(@1|@2)&@3
(@1|@2)&@3&(@4|@5|@6)
```

### 6.4 输出示例

```json
{
  "rule_id": "5",
  "rule_name": "[精准]20kV线路故障（远方手合）",
  "expression": "(@1|@2)&@3&(@4|@5|@6)",
  "triggered": true,
  "matched_variables": ["@1", "@3", "@4"],
  "unmatched_variables": [],
  "event_level": "事故",
  "event_type": "2-跳闸事件",
  "reason": "表达式中各逻辑分支均满足触发条件。"
}
```

### 6.5 交付物

- 表达式语法说明。
- 表达式解析器。
- 表达式求值结果格式。
- 异常表达式处理说明。

## 7. 课题 D：事件生成、调度编排与可视化

### 7.1 目标

基于 QwenPaw 多智能体框架或等价调度流程，串联 A/B/C 模块，将规则判定结果转为标准事件，并在前端展示。

### 7.2 功能

- 编排告警解析、SKILL 匹配、表达式求值、事件生成。
- 根据 `event_type`、`event_level`、`output_format` 生成事件对象。
- 展示原始告警、解析结果、命中特征、命中规则、事件结果。
- 生成简洁分析报告。

### 7.3 标准事件输出

```json
{
  "event_id": "EVT-0001",
  "source_rule_id": "5",
  "event_type": "2-跳闸事件",
  "event_level": "事故",
  "output_text": "线路故障（远方手合）",
  "matched_alarms": ["ALM-001", "ALM-002"],
  "matched_features": ["@1", "@3", "@4"],
  "summary": "系统根据规则 [精准]20kV线路故障（远方手合）识别出跳闸事件。"
}
```

## 8. 接口约定

接口细节以 `contracts/module_contracts.md` 为准。

当前优先固定三类对象：

```text
StructuredAlarm
CandidateSkill
RuleEvaluationResult
StandardEvent
```

## 9. 测试与验证

测试应覆盖全量规则加载和多类表达式解析。告警侧可先从真实数据集中选取：

- `ALM-001`：保护 A 网中断动作
- `ALM-002`：保护 A 网中断动作
- `ALM-004`：101 开关分闸
- `ALM-011`：101 开关合闸
- `ALM-013`：测控 A 网中断动作

规则侧应加载 `rules.json` 中全部 461 条规则，并统计表达式解析结果。Rule 5 可作为示例：

```text
rule_id: 5
expression: (@1|@2)&@3&(@4|@5|@6)
```

## 10. 已确认与待确认问题

### 10.1 已确认

老师已确认：

```text
rules.expression 中的 @1/@2/@3
直接对应 features.json 中 feature_id 为 @1/@2/@3 的特征。
```

例如：

```text
rule_id=5
expression=(@1|@2)&@3&(@4|@5|@6)
```

表示：

```text
特征 @1 或 @2 触发
且特征 @3 触发
且特征 @4/@5/@6 任一触发
```

老师还说明了完整链路：

```text
alarm 具体告警实例
  ↑ 运行时语义匹配
signal_mapping 信号模式模板，定义在 feature 内
  ↑ @N 局部索引
feature.expression 特征逻辑表达式
  ↑ feature_id
rule.expression 事件判定表达式
```

### 10.2 待确认

1. 运行时语义匹配的规则：`alarm.signal_name` 与 `signal_mappings.object_name / signal_feature / feature_desc` 具体按哪些字段匹配。
2. `valid_time` 的单位是否统一为秒。
3. `scope` 中的 `同厂站`、`同间隔`、`同20kV主变` 如何计算。
4. `run_mode: @ULL/` 的业务含义是什么。
5. `output_format` 中 `$LINE`、`$DEV`、`$TR`、`$BUS` 如何替换。

在这些问题确认前，第一版可以先完成：

```text
Feature SKILL / Rule SKILL 加载
feature.expression 与 rule.expression 解析
基于 mock signal_mapping 状态计算 feature_states
基于 feature_states 求值 rules.expression
```

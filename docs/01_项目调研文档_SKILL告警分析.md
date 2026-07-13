# 项目调研文档：基于 AI Agent 的电网告警事件分析系统

整理日期：2026-07-13  
当前依据：`data/samples/samples-md` 数据集

## 1. 项目背景

电力系统运行过程中会产生大量告警信息。单条告警通常不能直接说明故障类型，真实业务中需要把一段时间内的告警、特征和规则结合起来，判断是否形成某类事件。

当前数据集已经明确给出三层结构：

```text
alarms.json   原始告警采样数据
features.json 特征定义数据
rules.json    事件规则数据
```

因此项目主线应从抽象的“模拟告警 code”调整为：

```text
原始告警 signal_name
  -> 告警字段解析
  -> signal_mappings 匹配形成特征
  -> rules.expression 规则表达式求值
  -> 输出 event_type / event_level / output_format
  -> Agent 生成可解释事件报告
```

## 2. 数据集概览

### 2.1 alarms.json

`alarms.json` 是告警采样数据，共 16 条。

主要字段：

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

当前数据中，最关键的信息主要藏在 `signal_name` 字段中，例如：

```text
2023年08月29日 17:09:11 20kV示范变电站 101开关 分闸
```

这说明感知预处理需要从 `signal_name` 中抽取：

- 告警时间
- 厂站名称
- 电压等级
- 设备或间隔名称
- 信号对象
- 动作状态，例如动作、复归、分闸、合闸

### 2.2 features.json

`features.json` 是特征定义数据，共 32 条。

主要字段：

```text
feature_id
feature_name
expression
feature_type
special_attr
scope
valid_time
threshold
time_limit
priority
signal_mappings
```

其中 `signal_mappings` 描述告警信号如何映射为特征，例如：

```text
object_type: 第一套线路保护
object_name: 保护通道A异常
value_source: 告警
signal_feature: 10kV线路保护通道全部退出
```

当前特征表达式大多为：

```text
@1=1
```

也存在复杂组合特征：

```text
(@1&@2&@4&@5)|(@3&@6)
```

### 2.3 rules.json

`rules.json` 是事件规则数据，共 461 条。

主要字段：

```text
rule_id
rule_name
rule_type
expression
event_level
event_type
output_format
valid_time
sub_type
run_mode
enabled
alarm_method
feature_refs
```

规则表达式主要由以下符号组成：

```text
@1 @2 @3 ...
&
|
!
()
```

示例：

```text
(@1|@2)&@3&(@4|@5|@6)
@1&@2&(@3|@4)&@5
@1&(!@2|!@3)
```

事件等级分布以 `事故` 为主，其次为 `严重`、`告知`、`危急` 和 `一般`。事件类型中数量最多的是 `2-跳闸事件`。

## 3. 关键发现

### 3.1 规则表达式中的变量需要确认映射关系

当前 `rules.json` 中的 `feature_refs` 全部为空，而表达式大量使用 `@1/@2/@3`。

因此不能简单认为：

```text
rules.expression 中的 @1 == features.json 中 feature_id 为 @1 的特征
```

更合理的初步判断是：

```text
rules.expression 中的 @1/@2/@3 可能是每条规则内部的局部条件编号
```

后续必须向老师或企业导师确认：

```text
rules.expression 中的 @n 如何绑定到 features.json 或具体告警信号？
```

这是项目能否准确落地的关键问题。

### 3.2 项目重点不是生成虚构告警 code

之前假设的抽象告警 code 只能作为概念说明，不应继续作为主文档里的核心样例。现在要以真实字段为准：

```text
signal_name
signal_mappings
feature_id / feature_name
rule_id / rule_name / expression
event_type / event_level / output_format
```

### 3.3 表达式引擎是核心难点

规则数据表明，第一版表达式引擎至少要支持：

- `&` 与
- `|` 或
- `!` 非
- 括号优先级
- `@1=1` 特征条件
- `valid_time` 时间窗口

后续再根据企业确认结果支持更多业务语法。

## 4. 技术路线

```text
告警采样数据 alarms.json
  -> 解析 signal_name
  -> 生成结构化告警
  -> 根据 signal_mappings 匹配特征
  -> 加载 feature SKILL / rule SKILL
  -> 解析 features.expression 和 rules.expression
  -> 判断规则是否触发
  -> 生成标准事件
  -> Agent 生成解释和报告
```

## 5. SKILL 机制的定位

SKILL 不负责“猜测结果”，而负责封装规则知识。

建议拆成两类：

```text
Feature SKILL：封装 features.json 中的特征定义和 signal_mappings
Rule SKILL：封装 rules.json 中的事件规则、表达式和输出格式
```

Agent 按需加载 SKILL 后，可以读取：

- 规则名称
- 表达式
- 生效时间
- 事件等级
- 事件类型
- 输出模板
- 业务解释

确定性判断仍应由表达式引擎完成，大模型主要负责规则解释、报告生成和模糊情况辅助分析。

## 6. 当前风险

| 风险 | 说明 | 应对 |
|---|---|---|
| 规则变量映射不明 | `rules.expression` 的 `@n` 与特征/告警关系未明确 | 优先向企业确认映射规则 |
| 告警样本较少 | `alarms.json` 只有 16 条 | 基于真实格式做数据扩展 |
| 信号信息藏在文本中 | `signal_name` 包含时间、厂站、设备、动作 | A 模块先做文本解析 |
| 表达式存在多种形态 | 包含 `&`、`|`、`!`、括号和 `@1=1` | C 模块分阶段实现语法 |
| 规则数量较多 | `rules.json` 有 461 条 | B 模块先做索引与筛选 |

## 7. 调研结论

当前项目应以真实数据结构为中心，路线为：

```text
告警文本解析 + 特征映射 + SKILL 规则管理 + 表达式引擎 + 多 Agent 编排 + 标准事件输出
```

其中最关键的前置工作是确认：

```text
告警 -> 特征 -> 规则变量 -> 事件
```

这条映射链路。

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
  -> 运行时语义匹配 signal_mappings
  -> feature.expression 计算特征是否触发
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
2026年07月13日 09:00:05 演示变电站 演示开关01 分闸
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

其中 `signal_mappings` 描述特征内部的信号模式模板，例如：

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

这里要注意：`features.expression` 中的 `@1/@2` 是特征内部的局部索引，对应同一个 feature 内 `signal_mappings.index`。它和 `rules.expression` 中引用 `feature_id` 的 `@1/@2` 不是同一层含义。

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

### 3.1 规则表达式变量已确认直接对应特征

老师已确认：`rules.json` 中 `expression` 里的 `@1`、`@2` 等变量，直接对应 `features.json` 中同名的 `feature_id`。

例如 `rule_id=5`：

```text
expression: (@1|@2)&@3&(@4|@5|@6)
```

其含义为：

```text
features.@1 或 features.@2 触发
且 features.@3 触发
且 features.@4 / features.@5 / features.@6 任一触发
```

因此规则到特征的映射链路可以确定为：

```text
rules.expression.@N
  -> features.feature_id == @N
  -> feature.expression
  -> feature.signal_mappings.index == @M
  -> alarm.signal_name 运行时语义匹配
```

这意味着 C 模块可以直接把规则表达式中的变量绑定到 Feature SKILL，不需要额外规则引用表。

### 3.2 特征内部也有一层局部表达式

老师进一步说明：

```text
alarm 具体告警实例
  ↑ 运行时语义匹配
signal_mapping 信号模式模板，定义在 feature 内
  ↑ @N 局部索引
feature.expression 特征逻辑表达式
  ↑ feature_id
rule.expression 事件判定表达式
```

因此系统中有两类变量：

| 位置 | 含义 | 例子 |
|---|---|---|
| `rule.expression` 的 `@1` | 全局特征编号，对应 `features.feature_id=@1` | Rule 5 的 `@1` 对应 Feature `@1` |
| `feature.expression` 的 `@1` | 特征内部局部信号编号，对应该 feature 的 `signal_mappings.index=@1` | Feature `@2` 的 `@1=1` 对应该特征内部第一条 signal_mapping |

### 3.3 项目重点不是生成虚构告警 code

之前假设的抽象告警 code 只能作为概念说明，不应继续作为主文档里的核心样例。现在要以真实字段为准：

```text
signal_name
signal_mappings
feature_id / feature_name
rule_id / rule_name / expression
event_type / event_level / output_format
```

### 3.4 表达式引擎是核心难点

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
  -> 告警与 signal_mappings 运行时语义匹配，得到 signal_mapping_states
  -> 求值 feature.expression，得到 feature_states
  -> 加载 feature SKILL / rule SKILL
  -> 求值 rules.expression，判断事件是否触发
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
| 告警样本较少 | `alarms.json` 只有 16 条 | 基于真实格式做数据扩展 |
| 信号信息藏在文本中 | `signal_name` 包含时间、厂站、设备、动作 | A 模块先做文本解析 |
| 表达式存在多种形态 | 包含 `&`、`|`、`!`、括号和 `@1=1` | C 模块分阶段实现语法 |
| 规则数量较多 | `rules.json` 有 461 条 | B 模块先做索引与筛选 |

## 7. 调研结论

当前项目应以真实数据结构为中心，路线为：

```text
告警文本解析 + 特征映射 + SKILL 规则管理 + 表达式引擎 + 多 Agent 编排 + 标准事件输出
```

当前已确认的核心映射链路是：

```text
alarm -> signal_mapping -> feature.expression -> feature_id -> rule.expression -> 标准事件
```

后续开发应围绕这条链路推进。

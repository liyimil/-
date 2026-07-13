# 基于 AI Agent 的电网告警事件分析系统

本仓库用于学校与企业项目式实习，当前方向为：

```text
真实样例数据导入
  -> 感知预处理
  -> SKILL 规则管理
  -> 表达式解析与求值
  -> QwenPaw 多智能体调度编排
  -> 标准事件生成
  -> 前端可视化展示
```

当前仓库只搭建项目框架和文档约定，不包含具体实现代码。

## 课题分工

| 课题 | 名称 | 主要职责 |
|---|---|---|
| A | 告警数据感知与预处理 | 解析 `alarms.json` 和 `signal_name`，输出结构化告警 |
| B | SKILL 规则管理与智能匹配 | 管理 `features/rules` 的 SKILL，输出候选特征、候选规则和 `signal_mapping_states` |
| C | 规则分析与表达式引擎 | 解析 `@n`、`&`、`|`、`!`、括号，输出规则触发结果 |
| D | 事件生成、调度编排与可视化 | 串联 A/B/C，生成标准事件并展示 |

## 主链路目标

项目目标是直接面向 `rules.json` 中的 461 条规则建立通用处理链路：

```text
A 解析 alarms.json 中的 signal_name
  -> B 用 signal_mappings 匹配告警，输出 signal_mapping_states
  -> C 求值 feature.expression 和 rule.expression
  -> D 生成标准事件并展示
```

示例规则：

```text
rule_id=5
expression=(@1|@2)&@3&(@4|@5|@6)
```

该规则仅作为文档示例，不作为唯一处理目标。实现时应按统一接口支持全量规则加载、索引、表达式解析和事件生成。

## 仓库目录

```text
data/                 数据目录
  samples/            真实样例和脱敏样本说明
  generated/          模拟生成数据
  labels/             标准答案和标注结果

skills/               SKILL 规则目录
  features/           特征定义 SKILL
  event_rules/        事件规则 SKILL

contracts/            A/B/C/D 模块接口契约

src/                  后续代码目录，目前只放模块说明
  alarm_generator/    课题 A：模拟数据生成
  perception_agent/   课题 A：感知预处理
  skill_engine/       课题 B：SKILL 管理与匹配
  expression_engine/  课题 C：表达式引擎
  orchestrator/       课题 D：调度编排
  event_generator/    课题 D：事件生成

frontend/             前端可视化目录
tests/                测试说明与规则用例
docs/                 项目文档
```

## 分工前先看

每个人先看：

1. `docs/03_课题分工与接口规范.md`
2. `contracts/module_contracts.md`

需要背景时再看：

1. `docs/01_项目调研文档_SKILL告警分析.md`
2. `docs/02_项目实施计划_SKILL告警分析.md`

`skills/event_rules/RULE_0005_LINE_FAULT_REMOTE_CLOSE.md` 仅作为 Rule SKILL 示例。实际实现目标是处理 `rules.json` 中的全量规则。

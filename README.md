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
| A | 告警数据生成与感知预处理 | 导入/生成、清洗、结构化告警数据 |
| B | SKILL 规则管理与智能匹配 | 管理规则 SKILL，匹配候选规则 |
| C | 规则分析与表达式引擎 | 解析表达式，判断事件是否触发 |
| D | 事件生成、调度编排与可视化 | 编排流程，生成事件，展示结果 |

## 最小主链路

第一阶段先跑通一个最小案例：

```text
A 解析 alarms.json 中的 signal_name
  -> B 从 features/rules 中加载候选 SKILL
  -> C 解析 rules.expression 并判断规则触发
  -> D 生成标准事件并展示
```

示例目标：

```text
输入：
ALM-004 的 signal_name 为：
2023年08月29日 17:09:11 20kV示范变电站 101开关 分闸

规则：
rule_id=5
expression=(@1|@2)&@3&(@4|@5|@6)

目标：
完成告警解析、SKILL 加载、表达式求值和标准事件输出。
```

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
tests/                测试与 golden cases
docs/                 项目文档
```

## 推荐阅读顺序

1. `docs/01_项目调研文档_SKILL告警分析.md`
2. `docs/02_项目实施计划_SKILL告警分析.md`
3. `docs/03_课题分工与接口规范.md`
4. `contracts/module_contracts.md`
5. `skills/event_rules/RULE_0005_LINE_FAULT_REMOTE_CLOSE.md`

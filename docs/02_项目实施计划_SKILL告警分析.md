# 项目实施计划：基于 AI Agent 的电网告警事件分析系统

整理日期：2026-07-07

## 1. 项目目标

实现一个面向电网告警事件分析的原型系统，支持模拟告警数据生成、告警预处理、SKILL 规则管理、表达式解析求值、多智能体调度编排、标准事件生成和前端可视化展示。

最终形成完整闭环：

```text
生成/导入告警数据
  -> 清洗与结构化
  -> 提取告警特征
  -> 匹配候选 SKILL
  -> 解析规则表达式
  -> 判断事件是否触发
  -> 生成标准事件
  -> 前端展示和报告输出
```

## 2. 系统架构

```text
┌──────────────────────────────────────┐
│ A. 模拟告警数据生成与感知预处理         │
│ 数据生成、清洗、结构化、初步分类          │
└──────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ B. SKILL 规则管理与智能匹配             │
│ SKILL 文件、规则索引、候选规则匹配        │
└──────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ C. 规则分析与表达式引擎                 │
│ 表达式解析、规则求值、事件触发判断        │
└──────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ D. 事件生成、调度编排与可视化            │
│ 多智能体编排、标准事件、报告、前端展示     │
└──────────────────────────────────────┘
```

## 3. 课题 A：模拟告警数据生成与感知预处理

### 3.1 目标

设计并实现模拟告警数据生成引擎，构造典型电网告警序列，并完成数据清洗、结构化和初步分类。

### 3.2 功能

- 设计告警数据 schema。
- 根据设备、时间、告警类型生成模拟告警。
- 支持正常噪声、典型故障、干扰告警、多事件并发。
- 生成标准答案标签。
- 清洗告警字段。
- 按时间排序。
- 按时间窗口聚合。
- 提取初步特征。

### 3.3 输出

```json
{
  "sequence_id": "SEQ_001",
  "scenario": "线路故障",
  "alarms": [],
  "features": {
    "alarm_codes": ["CURRENT_OVER_LIMIT", "PROTECTION_ACTION", "BREAKER_TRIP"],
    "device_count": 1,
    "time_span_seconds": 8,
    "has_noise": false
  }
}
```

### 3.4 交付物

- 告警数据 schema。
- 模拟数据生成器。
- 数据清洗模块。
- 感知预处理模块。
- 测试数据集。

## 4. 课题 B：SKILL 规则管理与智能匹配

### 4.1 目标

构建系统知识中枢，用 SKILL 文件管理告警识别模式和事件规则，替代传统 RAG 向量检索方案。

### 4.2 功能

- 设计 SKILL 文件模板。
- 将特征定义封装为 SKILL。
- 将事件规则封装为 SKILL。
- 建立 SKILL 元数据索引。
- 根据告警特征匹配候选 SKILL。
- 支持 Agent 按需加载 SKILL。
- 输出候选规则和匹配原因。

### 4.3 SKILL 示例

```markdown
# SKILL: 线路故障事件识别

## metadata
- skill_id: EVENT_LINE_FAULT
- type: event_rule
- related_alarm_codes:
  - CURRENT_OVER_LIMIT
  - PROTECTION_ACTION
  - BREAKER_TRIP

## expression
CURRENT_OVER_LIMIT & PROTECTION_ACTION & BREAKER_TRIP within 30s on same_device

## output
- event_type: 线路故障事件
- event_level: 高
- push_priority: 优先推送
```

### 4.4 输出

```json
{
  "sequence_id": "SEQ_001",
  "candidate_skills": [
    {
      "skill_id": "EVENT_LINE_FAULT",
      "skill_path": "skills/event_line_fault.md",
      "match_reason": "包含线路故障相关告警代码"
    }
  ]
}
```

### 4.5 交付物

- SKILL 文件规范。
- SKILL 样例库。
- SKILL 管理模块。
- SKILL 匹配模块。
- Agent 加载接口。

## 5. 课题 C：规则分析与表达式引擎

### 5.1 目标

实现特征表达式的解析与求值引擎，结合 QwenPaw Agent 加载 SKILL 规则并完成复杂规则判定。

### 5.2 功能

- 解析 SKILL 中的 expression。
- 支持 AND、OR、NOT。
- 支持 within 时间窗口。
- 支持 same_device 同设备约束。
- 支持 before 顺序约束。
- 支持 count 计数条件。
- 输出命中条件和未命中条件。
- 对模糊规则调用大模型辅助理解。

### 5.3 表达式示例

```text
CURRENT_OVER_LIMIT & PROTECTION_ACTION & BREAKER_TRIP within 30s on same_device
```

### 5.4 输出

```json
{
  "skill_id": "EVENT_LINE_FAULT",
  "triggered": true,
  "matched_conditions": [
    "CURRENT_OVER_LIMIT",
    "PROTECTION_ACTION",
    "BREAKER_TRIP"
  ],
  "actual_time_span": 8,
  "confidence": 0.93,
  "reason": "同一设备在 8 秒内满足三类关键告警组合条件"
}
```

### 5.5 交付物

- 表达式语法设计。
- 表达式解析器。
- 规则求值引擎。
- QwenPaw Agent 调用流程。
- 规则判定结果结构。

## 6. 课题 D：事件生成、调度编排与可视化

### 6.1 目标

基于 QwenPaw 多智能体框架搭建整体流程，实现事件标准化生成、调度编排和前端展示。

### 6.2 功能

- 编排 A/B/C 模块。
- 实现调度智能体。
- 实现生成智能体。
- 生成标准事件对象。
- 生成事件摘要和分析报告。
- 开发前端监控界面。
- 展示告警流、SKILL 命中、规则判断和事件结果。

### 6.3 标准事件输出

```json
{
  "event_id": "E001",
  "event_type": "线路故障事件",
  "event_level": "高",
  "push_priority": "优先推送",
  "start_time": "2026-07-07 10:00:01",
  "end_time": "2026-07-07 10:00:08",
  "device_id": "LINE_01",
  "matched_alarms": ["A001", "A002", "A003"],
  "matched_skill": "EVENT_LINE_FAULT",
  "summary": "同一线路在 8 秒内连续出现电流越限、保护动作和开关跳闸，命中线路故障事件规则。"
}
```

### 6.4 前端页面

- 数据导入与模拟页面。
- 告警流监控页面。
- SKILL 规则管理页面。
- 规则命中结果页面。
- 事件结果看板。
- Agent 执行状态页面。

### 6.5 交付物

- 多智能体编排流程。
- 标准事件生成模块。
- 分析报告生成模块。
- 前端可视化界面。
- 系统演示 Demo。

## 7. 接口约定

### 7.1 A 输出给 B/C

```json
{
  "sequence_id": "SEQ_001",
  "alarms": [],
  "features": {},
  "metadata": {}
}
```

### 7.2 B 输出给 C

```json
{
  "sequence_id": "SEQ_001",
  "candidate_skills": [
    {
      "skill_id": "EVENT_LINE_FAULT",
      "skill_path": "skills/event_line_fault.md"
    }
  ]
}
```

### 7.3 C 输出给 D

```json
{
  "sequence_id": "SEQ_001",
  "skill_id": "EVENT_LINE_FAULT",
  "triggered": true,
  "confidence": 0.93,
  "reason": "满足同设备、30秒窗口和三类关键告警条件"
}
```

### 7.4 D 最终输出

```json
{
  "event_id": "E001",
  "event_type": "线路故障事件",
  "event_level": "高",
  "push_priority": "优先推送",
  "summary": "检测到线路故障事件"
}
```

## 8. 测试案例

### 案例 1：正常噪声告警

输入普通告警，不满足任何事件规则。系统应不生成高优先级事件。

### 案例 2：线路故障事件

同一线路 30 秒内出现电流越限、保护动作、开关跳闸。系统应识别为线路故障事件。

### 案例 3：设备不一致

告警类型满足，但来自不同设备。系统不应触发同一事件。

### 案例 4：时间超窗

告警类型满足，但时间跨度超过规则窗口。系统不应触发事件。

### 案例 5：多事件并发

不同设备同时出现多组告警。系统应分开生成多个事件。

## 9. 评测指标

- 告警数据生成完整性。
- SKILL 匹配准确率。
- 表达式求值准确率。
- 事件识别准确率。
- 误报率。
- 漏报率。
- 标准事件字段完整性。
- 前端展示完整性。
- Agent 输出稳定性。

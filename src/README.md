# src 目录说明

本目录用于实现 A/B/C/D 各模块代码。当前已提供一条可运行的 DEMO 主链路，便于在真实 QwenPaw 框架和全量规则接入前完成接口联调。

模块对应关系：

```text
alarm_generator/    课题 A：模拟数据生成
perception_agent/   课题 A：感知预处理
skill_engine/       课题 B：SKILL 管理与智能匹配
expression_engine/  课题 C：表达式解析与求值
orchestrator/       课题 D：QwenPaw 多智能体调度编排
event_generator/    课题 D：标准事件生成
```

## 当前运行方式

```bash
python src/orchestrator/orchestrator.py --adapter demo
```

`demo` 模式会依次调用：

```text
alarm_generator -> perception_agent -> skill_engine -> expression_engine -> event_generator
```

`mock` 模式用于 D 模块单独调试，`real` 模式预留给后续真实 QwenPaw 接入。

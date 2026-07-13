# orchestrator

课题 D：调度智能体与多智能体编排模块。

职责：

- 串联 A/B/C/D。
- 管理 QwenPaw 多智能体流程。
- 统一任务输入、状态和输出。
- 为前端提供任务执行结果。

主要输入：

```text
A 输出的结构化告警
B 输出的候选 SKILL / signal_mapping_states
C 输出的 feature_states / rule_results
```

主要输出：

```text
完整任务结果
标准事件列表
前端展示数据
```

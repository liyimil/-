# orchestrator

课题 D：调度编排模块。

## 负责范围

- 串联 A/B/C/D 的输入输出。
- 使用 adapter 层屏蔽不同运行来源：`demo` 串联本地 A/B/C/D，`mock` 用于 D 单模块调试，`real` 预留给真实 QwenPaw。
- 调用 `src/event_generator/event_generator.py` 生成标准事件。
- 汇总 `agent_steps`、输入统计、事件统计和前端展示数据。

## 当前文件

- `orchestrator.py`：编排入口和命令行运行脚本。
- `qwenpaw_adapter.py`：QwenPaw 适配层，当前提供 demo/mock/real 三种模式，后续真实框架接入时只改这里。
- `workflow_config.py`：A/B/C/D 多智能体流程配置。
- `__init__.py`：导出 `run_pipeline`。

## 本地运行

```bash
python src/orchestrator/orchestrator.py --adapter demo
```

如需保存运行结果：

```bash
python src/orchestrator/orchestrator.py --adapter demo --output data/generated/d_module_result.json
```

当前默认使用 demo adapter，会串联本地 A/B/C/D 模块。D 模块单独调试时可切换为：

```bash
python src/orchestrator/orchestrator.py --adapter mock
```

本地存在样例数据时，可验证全量规则加载：

```bash
python src/orchestrator/orchestrator.py --adapter demo --sample-dir data/samples/samples-md
```

该命令只读取本地 ignored 数据，不会把样例提交到仓库。

后续真实 QwenPaw 接入时，目标命令形态如下：

```bash
python src/orchestrator/orchestrator.py --adapter real
```

真实调用逻辑集中写在 `qwenpaw_adapter.py` 的 `RealQwenPawAdapter`，不要散落到 `orchestrator.py`。

## 等 A/B/C 接入时怎么改

- A 模块把结构化告警放入 `structured_alarms.alarms`。
- B 模块把候选 SKILL 和信号命中状态放入 `skill_match`。
- C 模块把 `feature_states`、`feature_hits`、`rule_results` 放入 `expression_result`。
- D 模块保持读取这些字段，不需要关心 A/B/C 内部如何实现。

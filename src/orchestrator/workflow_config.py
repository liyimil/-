from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AgentSpec:
    module: str
    name: str
    input_key: str
    output_key: str
    description: str


WORKFLOW: List[AgentSpec] = [
    AgentSpec(
        module="A",
        name="perception_agent",
        input_key="raw_alarms",
        output_key="structured_alarms",
        description="模拟告警数据生成与感知预处理",
    ),
    AgentSpec(
        module="B",
        name="skill_engine",
        input_key="structured_alarms",
        output_key="skill_match",
        description="SKILL 规则管理与智能匹配",
    ),
    AgentSpec(
        module="C",
        name="expression_engine",
        input_key="skill_match",
        output_key="expression_result",
        description="规则分析与表达式求值",
    ),
    AgentSpec(
        module="D",
        name="event_generator",
        input_key="expression_result",
        output_key="event_result",
        description="事件生成、调度编排与可视化",
    ),
]

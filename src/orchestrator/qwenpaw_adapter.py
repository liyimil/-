from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from .workflow_config import AgentSpec, WORKFLOW


@dataclass
class AgentRunResult:
    agent: str
    module: str
    status: str
    output_key: str
    output_count: int
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseQwenPawAdapter:
    """Adapter boundary for the QwenPaw multi-agent workflow."""

    def run_workflow(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class MockQwenPawAdapter(BaseQwenPawAdapter):
    """Use existing mock A/B/C outputs to simulate a QwenPaw workflow."""

    def run_workflow(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        outputs: Dict[str, Any] = {
            "structured_alarms": payload.get("structured_alarms") or {},
            "skill_match": payload.get("skill_match") or {},
            "expression_result": payload.get("expression_result") or {},
        }

        agent_steps = [
            self._build_step(spec, outputs.get(spec.output_key), status="mocked")
            for spec in WORKFLOW
            if spec.output_key != "event_result"
        ]

        return {
            "mode": "mock",
            "workflow": [asdict(spec) for spec in WORKFLOW],
            "agent_steps": [step.to_dict() for step in agent_steps],
            "outputs": outputs,
        }

    def _build_step(self, spec: AgentSpec, output: Any, status: str) -> AgentRunResult:
        return AgentRunResult(
            agent=spec.name,
            module=spec.module,
            status=status,
            output_key=spec.output_key,
            output_count=_count_output(output),
            message=spec.description,
        )


class RealQwenPawAdapter(BaseQwenPawAdapter):
    """Placeholder for the real QwenPaw SDK/runtime integration."""

    def __init__(self, client: Any = None) -> None:
        self.client = client

    def run_workflow(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError(
            "Real QwenPaw integration is not wired yet. Keep orchestrator stable and "
            "implement QwenPaw agent calls inside RealQwenPawAdapter.run_workflow()."
        )


def create_qwenpaw_adapter(mode: str = "mock") -> BaseQwenPawAdapter:
    if mode == "mock":
        return MockQwenPawAdapter()
    if mode == "real":
        return RealQwenPawAdapter()
    raise ValueError(f"Unsupported QwenPaw adapter mode: {mode}")


def append_event_step(agent_steps: List[Dict[str, Any]], event_count: int) -> List[Dict[str, Any]]:
    steps = list(agent_steps)
    steps.append(
        AgentRunResult(
            agent="event_generator",
            module="D",
            status="completed",
            output_key="event_result",
            output_count=event_count,
            message="事件生成、调度编排与可视化",
        ).to_dict()
    )
    return steps


def _count_output(output: Any) -> int:
    if isinstance(output, Mapping):
        for key in ("alarms", "rule_results", "candidate_rule_skills", "events"):
            value = output.get(key)
            if isinstance(value, list):
                return len(value)
        return len(output)
    if isinstance(output, list):
        return len(output)
    return 0 if output is None else 1

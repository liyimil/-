from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from src.alarm_generator import generate_demo_alarms
from src.expression_engine import DEMO_FEATURES, DEMO_RULES, evaluate_rules
from src.perception_agent import preprocess_alarms
from src.skill_engine import match_skills

from .qwenpaw_runtime import QwenPawRuntimeBridge
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


class DemoQwenPawAdapter(BaseQwenPawAdapter):
    """Run the local A/B/C modules as a complete demo multi-agent workflow."""

    def run_workflow(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raw_alarms = payload.get("raw_alarms") or generate_demo_alarms()
        structured_alarms = preprocess_alarms(raw_alarms)
        skill_match = match_skills(
            structured_alarms,
            features=payload.get("features") or DEMO_FEATURES,
            rules=payload.get("rules") or DEMO_RULES,
        )
        expression_result = evaluate_rules(skill_match)

        outputs: Dict[str, Any] = {
            "raw_alarms": raw_alarms,
            "structured_alarms": structured_alarms,
            "skill_match": skill_match,
            "expression_result": expression_result,
        }

        agent_steps = [
            AgentRunResult(
                agent=spec.name,
                module=spec.module,
                status="completed",
                output_key=spec.output_key,
                output_count=_count_output(outputs.get(spec.output_key)),
                message=spec.description,
            ).to_dict()
            for spec in WORKFLOW
            if spec.output_key != "event_result"
        ]

        return {
            "mode": "demo",
            "workflow": [asdict(spec) for spec in WORKFLOW],
            "agent_steps": agent_steps,
            "outputs": outputs,
        }


class RealQwenPawAdapter(BaseQwenPawAdapter):
    """Run A/B/C through QwenPaw Agent tool calls."""

    def __init__(self, runtime: QwenPawRuntimeBridge | None = None) -> None:
        self.runtime = runtime

    def run_workflow(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        runtime = self.runtime or QwenPawRuntimeBridge.from_environment()

        raw_alarms = payload.get("raw_alarms") or generate_demo_alarms()
        outputs: Dict[str, Any] = {
            "raw_alarms": raw_alarms,
        }

        def run_perception_agent() -> Mapping[str, Any]:
            """A module: parse raw alarm payload into structured alarms."""
            outputs["structured_alarms"] = preprocess_alarms(raw_alarms)
            return _tool_summary("structured_alarms", outputs["structured_alarms"])

        def run_skill_engine() -> Mapping[str, Any]:
            """B module: match structured alarms against Feature/Rule SKILLs."""
            structured_alarms = outputs.get("structured_alarms")
            if not structured_alarms:
                raise RuntimeError("run_perception_agent must be called before run_skill_engine.")
            outputs["skill_match"] = match_skills(
                structured_alarms,
                features=payload.get("features") or DEMO_FEATURES,
                rules=payload.get("rules") or DEMO_RULES,
            )
            return _tool_summary("skill_match", outputs["skill_match"])

        def run_expression_engine() -> Mapping[str, Any]:
            """C module: evaluate feature and event rule expressions."""
            skill_match = outputs.get("skill_match")
            if not skill_match:
                raise RuntimeError("run_skill_engine must be called before run_expression_engine.")
            outputs["expression_result"] = evaluate_rules(skill_match)
            return _tool_summary("expression_result", outputs["expression_result"])

        agent_decision = runtime.run_agent_workflow(
            {
                "run_perception_agent": run_perception_agent,
                "run_skill_engine": run_skill_engine,
                "run_expression_engine": run_expression_engine,
            },
            {
                "alarm_count": _raw_alarm_count(raw_alarms),
                "feature_count": _payload_count(payload.get("features"), "features"),
                "rule_count": _payload_count(payload.get("rules"), "rules"),
            },
        )

        missing_outputs = [
            key for key in ("structured_alarms", "skill_match", "expression_result")
            if key not in outputs
        ]
        if missing_outputs:
            raise RuntimeError(
                "QwenPaw Agent did not complete required module calls: "
                + ", ".join(missing_outputs)
            )

        agent_steps = []
        for spec in WORKFLOW:
            if spec.output_key == "event_result":
                continue
            output = outputs.get(spec.output_key)
            step = runtime.build_step(spec, output, _count_output(output))
            step["message"] = f"QwenPaw Agent invoked tool for {spec.module}: {spec.name}"
            agent_steps.append(step)

        return {
            "mode": "real",
            "runtime": {
                "package": runtime.info.package,
                "version": runtime.info.version,
                "agent": "QwenPawAgent",
                "decision": agent_decision.get("response", ""),
            },
            "workflow": [asdict(spec) for spec in WORKFLOW],
            "agent_steps": agent_steps,
            "outputs": outputs,
        }


def create_qwenpaw_adapter(mode: str = "mock") -> BaseQwenPawAdapter:
    if mode == "mock":
        return MockQwenPawAdapter()
    if mode == "demo":
        return DemoQwenPawAdapter()
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


def _tool_summary(output_key: str, output: Any) -> Dict[str, Any]:
    return {
        "output_key": output_key,
        "output_count": _count_output(output),
        "output_type": "mapping" if isinstance(output, Mapping) else type(output).__name__,
        "status": "completed",
    }


def _payload_count(payload: Any, key: str) -> int:
    if isinstance(payload, Mapping) and isinstance(payload.get(key), list):
        return len(payload[key])
    return 0


def _raw_alarm_count(raw_alarms: Any) -> int:
    if isinstance(raw_alarms, Mapping):
        alarms = raw_alarms.get("alarms")
        if isinstance(alarms, list):
            return len(alarms)
    if isinstance(raw_alarms, list):
        return len(raw_alarms)
    return 0

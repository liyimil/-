import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.event_generator import generate_events
from src.orchestrator.qwenpaw_adapter import append_event_step, create_qwenpaw_adapter


def run_pipeline(payload: Mapping[str, Any], adapter_mode: str = "mock") -> Dict[str, Any]:
    adapter = create_qwenpaw_adapter(adapter_mode)
    workflow_result = adapter.run_workflow(payload)
    workflow_outputs = workflow_result["outputs"]

    structured_alarms = workflow_outputs.get("structured_alarms") or {}
    skill_match = workflow_outputs.get("skill_match") or {}
    expression_result = workflow_outputs.get("expression_result") or {}

    alarms = structured_alarms.get("alarms") or []
    rule_results = expression_result.get("rule_results") or []
    feature_hits = expression_result.get("feature_hits") or {}

    event_result = generate_events(
        rule_results=rule_results,
        alarms=alarms,
        feature_hits=feature_hits,
        context=payload.get("context") or {},
    )

    agent_steps = append_event_step(workflow_result["agent_steps"], event_result["event_count"])

    return {
        "task_id": payload.get("task_id", "TASK-UNKNOWN"),
        "dataset_id": payload.get("dataset_id", expression_result.get("dataset_id", "")),
        "status": "completed",
        "adapter_mode": workflow_result["mode"],
        "workflow": workflow_result["workflow"],
        "agent_steps": agent_steps,
        "inputs": {
            "alarm_count": len(alarms),
            "rule_result_count": len(rule_results),
            "triggered_rule_count": event_result["event_count"],
        },
        "events": event_result["events"],
        "event_stats": {
            "event_count": event_result["event_count"],
            "level_stats": event_result["level_stats"],
            "type_stats": event_result["type_stats"],
        },
        "frontend_data": {
            "agent_steps": agent_steps,
            "alarms": alarms,
            "rule_results": rule_results,
            "events": event_result["events"],
            "event_stats": event_result["level_stats"],
        },
    }


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run D module orchestration with mock A/B/C outputs.")
    parser.add_argument(
        "--mock",
        default=str(PROJECT_ROOT / "tests" / "mock_outputs" / "d_module_mock.json"),
        help="Path to mock pipeline payload.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path for writing orchestration result JSON.",
    )
    parser.add_argument(
        "--adapter",
        choices=["mock", "real"],
        default="mock",
        help="QwenPaw adapter mode. Use mock before the real QwenPaw SDK is wired.",
    )
    args = parser.parse_args()

    result = run_pipeline(load_json(Path(args.mock)), adapter_mode=args.adapter)
    if args.output:
        save_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

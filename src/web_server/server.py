import argparse
import json
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DEFAULT_SAMPLE_DIR = PROJECT_ROOT / "data" / "samples" / "samples-md"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator.orchestrator import load_sample_payload, run_pipeline, save_json
from src.orchestrator.qwenpaw_runtime import QwenPawRuntimeUnavailable


class DashboardState:
    def __init__(self, adapter: str, sample_dir: Optional[Path], output: Optional[Path]) -> None:
        self.adapter = adapter
        self.sample_dir = sample_dir
        self.output = output
        self.last_result: Optional[Dict[str, Any]] = None
        self.last_error: Optional[str] = None

    def run(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "task_id": "WEB-DASHBOARD",
            "dataset_id": "demo-dataset",
            "context": {},
        }
        if self.sample_dir:
            payload.update(load_sample_payload(self.sample_dir))
            payload["dataset_id"] = self.sample_dir.name

        result = run_pipeline(payload, adapter_mode=self.adapter)
        self.last_result = to_frontend_data(result)
        self.last_error = None
        if self.output:
            save_json(self.output, result)
        return self.last_result

    def dashboard(self) -> Dict[str, Any]:
        if self.last_result is None:
            return self.run()
        return self.last_result


class DashboardHandler(SimpleHTTPRequestHandler):
    state: DashboardState

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(FRONTEND_ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/dashboard":
            self._handle_json(lambda: self.state.dashboard())
            return
        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "adapter": self.state.adapter})
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/run":
            self._handle_json(lambda: self.state.run())
            return
        self.send_error(HTTPStatus.NOT_FOUND, "API endpoint not found")

    def _handle_json(self, producer: Any) -> None:
        try:
            self._send_json(producer())
        except FileNotFoundError as exc:
            self.state.last_error = str(exc)
            self._send_json({"status": "error", "message": f"sample file not found: {exc}"}, HTTPStatus.BAD_REQUEST)
        except QwenPawRuntimeUnavailable as exc:
            self.state.last_error = str(exc)
            self._send_json({"status": "error", "message": f"QwenPaw runtime unavailable: {exc}"}, HTTPStatus.BAD_GATEWAY)
        except Exception as exc:  # noqa: BLE001 - API should surface unexpected demo failures as JSON.
            self.state.last_error = str(exc)
            self._send_json({"status": "error", "message": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _send_json(self, payload: Mapping[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def to_frontend_data(result: Mapping[str, Any]) -> Dict[str, Any]:
    frontend = result.get("frontend_data") if isinstance(result.get("frontend_data"), dict) else {}
    alarms = list(frontend.get("alarms") or [])
    rules = list(frontend.get("rule_results") or [])
    events = list(result.get("events") or frontend.get("events") or [])

    return {
        "taskId": result.get("task_id", ""),
        "datasetId": result.get("dataset_id", ""),
        "status": result.get("status", ""),
        "adapterMode": result.get("adapter_mode", ""),
        "runtime": result.get("runtime", {}),
        "metrics": {
            "alarmCount": int(result.get("inputs", {}).get("alarm_count") or len(alarms)),
            "ruleResultCount": int(result.get("inputs", {}).get("rule_result_count") or len(rules)),
            "triggeredRuleCount": int(result.get("inputs", {}).get("triggered_rule_count") or len(events)),
            "eventCount": int(result.get("event_stats", {}).get("event_count") or len(events)),
        },
        "workflow": [_workflow_item(item, result.get("agent_steps", [])) for item in result.get("workflow", [])],
        "events": [_event_item(item) for item in events],
        "rules": [_rule_item(item) for item in rules],
        "alarms": [_alarm_item(item) for item in alarms],
        "deliverables": [
            ["A -> B", "structured_alarms", "runtime output: structured_alarms"],
            ["B -> C", "skill_match", "runtime output: skill_match"],
            ["C -> D", "expression_result", "runtime output: expression_result"],
            ["D -> Frontend", "dashboard json", "/api/dashboard"],
        ],
    }


def _workflow_item(item: Mapping[str, Any], agent_steps: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    module = str(item.get("module", ""))
    step = next((entry for entry in agent_steps if str(entry.get("module")) == module), {})
    return {
        "module": module,
        "name": item.get("name", ""),
        "title": _module_title(module),
        "input": item.get("input_key", ""),
        "output": item.get("output_key", ""),
        "status": step.get("status", "completed"),
        "count": step.get("output_count", 0),
        "description": item.get("description", ""),
    }


def _event_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "eventId": item.get("event_id", ""),
        "sourceRuleId": str(item.get("source_rule_id", "")),
        "ruleName": item.get("rule_name", ""),
        "eventType": item.get("event_type", ""),
        "eventLevel": item.get("event_level", ""),
        "outputText": item.get("output_text", ""),
        "matchedAlarms": list(item.get("matched_alarms") or []),
        "matchedFeatures": list(item.get("matched_features") or []),
        "reason": item.get("reason", ""),
        "summary": item.get("summary", ""),
        "generatedAt": item.get("generated_at", ""),
    }


def _rule_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "sourceRuleId": str(item.get("source_rule_id", "")),
        "ruleName": item.get("rule_name", ""),
        "expression": item.get("expression", ""),
        "triggered": bool(item.get("triggered")),
        "matchedVariables": list(item.get("matched_variables") or []),
        "unmatchedVariables": list(item.get("unmatched_variables") or []),
        "eventType": item.get("event_type", ""),
        "eventLevel": item.get("event_level", ""),
        "outputFormat": item.get("output_format", ""),
        "matchedAlarms": list(item.get("matched_alarms") or []),
    }


def _alarm_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = item.get("parsed") if isinstance(item.get("parsed"), dict) else {}
    return {
        "alarmId": item.get("alarm_id", ""),
        "time": item.get("timestamp", "") or item.get("time", ""),
        "station": item.get("station_name", "") or parsed.get("station_name", ""),
        "objectName": item.get("object_name", "") or parsed.get("object_name", "") or item.get("device_name", ""),
        "action": item.get("action", "") or parsed.get("action", "") or item.get("signal_type", ""),
        "raw": item.get("raw_signal_name", "") or item.get("signal_name", "") or item.get("raw", ""),
    }


def _module_title(module: str) -> str:
    return {
        "A": "感知预处理",
        "B": "SKILL 匹配",
        "C": "表达式求值",
        "D": "事件生成",
    }.get(module, module)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the frontend dashboard and orchestration API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--adapter", choices=["mock", "demo", "real"], default="real")
    parser.add_argument("--sample-dir", default=str(DEFAULT_SAMPLE_DIR))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "generated" / "last_orchestration_result.json"))
    args = parser.parse_args()

    sample_dir = Path(args.sample_dir) if args.sample_dir else None
    if sample_dir and not sample_dir.exists():
        sample_dir = None
    output = Path(args.output) if args.output else None

    DashboardHandler.state = DashboardState(args.adapter, sample_dir, output)
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    print(f"Adapter: {args.adapter}; sample_dir: {sample_dir or 'demo payload'}")
    server.serve_forever()


if __name__ == "__main__":
    main()

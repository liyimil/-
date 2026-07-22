import unittest
from importlib import metadata
from unittest.mock import patch

from src.alarm_generator import generate_demo_alarms
from src.expression_engine import DEMO_FEATURES, DEMO_RULES, evaluate_expression, evaluate_rules
from src.orchestrator import run_pipeline
from src.orchestrator.qwenpaw_adapter import RealQwenPawAdapter
from src.orchestrator.qwenpaw_runtime import (
    QwenPawRuntimeBridge,
    QwenPawRuntimeInfo,
    QwenPawRuntimeUnavailable,
)
from src.perception_agent import preprocess_alarms
from src.skill_engine import match_skills
from src.web_server.server import to_frontend_data


class DemoPipelineTest(unittest.TestCase):
    def test_expression_engine_supports_boolean_operations(self):
        states = {"@1": True, "@2": False, "@3": True, "@4": False}

        self.assertTrue(evaluate_expression("(@1|@2)&@3", states))
        self.assertFalse(evaluate_expression("@2&@3", states))
        self.assertTrue(evaluate_expression("!@2&@1", states))
        self.assertTrue(evaluate_expression("@1=1", states))
        self.assertTrue(evaluate_expression("@2=0", states))
        self.assertTrue(evaluate_expression("[2,(@1,@2,@3)]", states))
        self.assertFalse(evaluate_expression("[3,(@1,@2,@3)]", states))

    def test_a_b_c_modules_produce_rule_results(self):
        raw = generate_demo_alarms()
        structured = preprocess_alarms(raw)
        skill_match = match_skills(structured, features=DEMO_FEATURES, rules=DEMO_RULES)
        expression_result = evaluate_rules(skill_match)

        self.assertEqual(len(structured["alarms"]), 3)
        self.assertEqual(structured["alarms"][0]["station_name"], "演示变电站")
        self.assertEqual(structured["alarms"][0]["parsed"]["voltage_level"], "20kV")
        self.assertTrue(skill_match["signal_mapping_states"]["@1"]["@1"])
        self.assertTrue(expression_result["feature_states"]["@1"])

        rule_5 = next(item for item in expression_result["rule_results"] if item["source_rule_id"] == "5")
        self.assertTrue(rule_5["triggered"])
        self.assertIn("@1", rule_5["matched_variables"])

    def test_external_features_and_rules_can_be_loaded(self):
        structured = {
            "dataset_id": "unit-dataset",
            "alarms": [
                {
                    "alarm_id": "UNIT-ALM-001",
                    "raw_signal_name": "2026年07月13日 09:00:00 测试站 测试开关 分闸",
                    "parsed": {"object_name": "测试开关", "action": "分闸"},
                }
            ],
        }
        features = {
            "features": [
                {
                    "feature_id": "@1",
                    "feature_name": "测试开关分闸",
                    "expression": "@1=1",
                    "signal_mappings": [{"index": "@1", "object_name": "测试开关"}],
                }
            ]
        }
        rules = {
            "rules": [
                {
                    "rule_id": "9001",
                    "rule_name": "测试事件",
                    "expression": "@1",
                    "event_level": "告知",
                    "event_type": "测试",
                    "output_format": "$DEV 测试事件",
                }
            ]
        }

        expression_result = evaluate_rules(match_skills(structured, features=features, rules=rules))

        self.assertEqual(len(expression_result["rule_results"]), 1)
        self.assertTrue(expression_result["rule_results"][0]["triggered"])

    def test_bad_rule_expression_does_not_stop_batch_evaluation(self):
        expression_result = evaluate_rules(
            {
                "dataset_id": "unit-dataset",
                "features": [{"feature_id": "@1", "expression": "@1=1"}],
                "rules": [{"rule_id": "bad", "expression": "(@1|&@2)"}],
                "signal_mapping_states": {"@1": {"@1": True}},
            }
        )

        self.assertFalse(expression_result["rule_results"][0]["triggered"])
        self.assertIn("表达式解析失败", expression_result["rule_results"][0]["reason"])

    def test_orchestrator_demo_generates_standard_event(self):
        payload = {
            "task_id": "TEST-TASK",
            "context": {
                "LINE": "演示变电站一号线路",
                "BAY": "演示变电站一号间隔",
                "DEV": "演示开关01",
            },
        }
        result = run_pipeline(payload, adapter_mode="demo")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["adapter_mode"], "demo")
        self.assertEqual(result["dataset_id"], "demo-dataset")
        self.assertEqual(result["event_stats"]["event_count"], 1)
        self.assertEqual(result["events"][0]["source_rule_id"], "5")
        self.assertIn("线路故障", result["events"][0]["output_text"])

    def test_real_adapter_requires_qwenpaw_package(self):
        with patch(
            "src.orchestrator.qwenpaw_runtime.metadata.version",
            side_effect=metadata.PackageNotFoundError("qwenpaw"),
        ):
            with self.assertRaises(QwenPawRuntimeUnavailable):
                RealQwenPawAdapter().run_workflow({})

    def test_real_adapter_runs_with_qwenpaw_runtime_bridge(self):
        runtime = QwenPawRuntimeBridge(QwenPawRuntimeInfo(package="qwenpaw", version="test-version"))
        result = RealQwenPawAdapter(runtime=runtime).run_workflow({})

        self.assertEqual(result["mode"], "real")
        self.assertEqual(result["runtime"]["package"], "qwenpaw")
        self.assertEqual(result["runtime"]["version"], "test-version")
        self.assertEqual(result["agent_steps"][0]["runtime"], "qwenpaw")
        self.assertEqual(len(result["outputs"]["expression_result"]["rule_results"]), 2)

    def test_orchestrator_result_can_feed_frontend_dashboard(self):
        result = run_pipeline({"task_id": "TEST-TASK"}, adapter_mode="demo")
        frontend_data = to_frontend_data(result)

        self.assertEqual(frontend_data["taskId"], "TEST-TASK")
        self.assertEqual(frontend_data["adapterMode"], "demo")
        self.assertEqual(frontend_data["metrics"]["eventCount"], 1)
        self.assertEqual(frontend_data["events"][0]["eventId"], "EVT-0001")
        self.assertIn("sourceRuleId", frontend_data["rules"][0])
        self.assertIn("alarmId", frontend_data["alarms"][0])


if __name__ == "__main__":
    unittest.main()

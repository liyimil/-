from typing import Any, Dict, List


def generate_demo_alarms() -> Dict[str, Any]:
    """Generate a deterministic demo alarm sequence for local integration tests."""
    alarms: List[Dict[str, Any]] = [
        {
            "alarm_id": "DEMO-ALM-001",
            "station_name": "演示变电站",
            "device_name": "一号线路保护",
            "signal_name": "2026年07月13日 09:00:01 演示变电站 一号线路保护A网中断 动作",
            "signal_value": 1,
            "voltage_level": "20kV",
        },
        {
            "alarm_id": "DEMO-ALM-002",
            "station_name": "演示变电站",
            "device_name": "演示开关01",
            "signal_name": "2026年07月13日 09:00:05 演示变电站 演示开关01 分闸",
            "signal_value": 1,
            "voltage_level": "20kV",
        },
        {
            "alarm_id": "DEMO-ALM-003",
            "station_name": "演示变电站",
            "device_name": "演示开关01",
            "signal_name": "2026年07月13日 09:02:10 演示变电站 演示开关01 合闸",
            "signal_value": 1,
            "voltage_level": "20kV",
        },
    ]
    return {
        "dataset_id": "demo-dataset",
        "scenario": "demo_line_fault_remote_close",
        "alarms": alarms,
    }

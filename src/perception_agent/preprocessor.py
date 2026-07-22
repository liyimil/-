from typing import Any, Dict, List, Mapping

from .perception_agent import map_to_signal_type, parse_signal_name


def preprocess_alarms(raw_payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize raw alarms into the A-module structured alarm contract."""
    structured: List[Dict[str, Any]] = []
    for alarm in raw_payload.get("alarms", []):
        structured.append(_parse_alarm(alarm))

    return {
        "dataset_id": raw_payload.get("dataset_id", "demo-dataset"),
        "alarms": structured,
    }


def _parse_alarm(alarm: Mapping[str, Any]) -> Dict[str, Any]:
    raw_signal_name = str(alarm.get("signal_name") or alarm.get("raw_signal_name") or "")
    parsed = parse_signal_name(raw_signal_name)
    voltage_level = str(parsed.get("voltage_level") or alarm.get("voltage_level", ""))
    object_name = parsed.get("object_name") or ""
    action = parsed.get("action") or ""
    signal_type = map_to_signal_type(object_name, action)
    return {
        "alarm_id": alarm.get("alarm_id", ""),
        "station_name": alarm.get("station_name", ""),
        "device_name": alarm.get("device_name", ""),
        "voltage_level": voltage_level,
        "signal_value": alarm.get("signal_value", 1),
        "raw_signal_name": raw_signal_name,
        "parsed": {
            "alarm_time": parsed.get("alarm_time"),
            "station_name": parsed.get("station_name"),
            "voltage_level": voltage_level,
            "object_name": object_name,
            "action": action,
        },
        "timestamp": parsed.get("alarm_time"),
        "device": object_name,
        "signal_type": signal_type,
        "action": action,
        "station": parsed.get("station_name"),
        "raw_value": alarm.get("signal_value", 1),
        "is_valid": bool(parsed.get("alarm_time") and object_name),
        "raw_signal": raw_signal_name,
        "time_delta": None,
    }

import re
from typing import Any, Dict, Iterable, List, Mapping


TIME_PATTERN = re.compile(
    r"(?P<year>\d{4})年(?P<month>\d{2})月(?P<day>\d{2})日\s+"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
)


def preprocess_alarms(raw_payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize raw demo alarms into the A-module structured alarm contract."""
    structured: List[Dict[str, Any]] = []
    for alarm in raw_payload.get("alarms", []):
        structured.append(_parse_alarm(alarm))

    return {
        "dataset_id": raw_payload.get("dataset_id", "demo-dataset"),
        "alarms": structured,
    }


def _parse_alarm(alarm: Mapping[str, Any]) -> Dict[str, Any]:
    raw_signal_name = str(alarm.get("signal_name") or alarm.get("raw_signal_name") or "")
    parsed = _parse_signal_name(raw_signal_name)
    voltage_level = str(alarm.get("voltage_level", ""))
    if not parsed.get("voltage_level"):
        parsed["voltage_level"] = voltage_level
    return {
        "alarm_id": alarm.get("alarm_id", ""),
        "station_name": alarm.get("station_name", ""),
        "device_name": alarm.get("device_name", ""),
        "voltage_level": voltage_level,
        "signal_value": alarm.get("signal_value", 1),
        "raw_signal_name": raw_signal_name,
        "parsed": parsed,
    }


def _parse_signal_name(signal_name: str) -> Dict[str, str]:
    time_match = TIME_PATTERN.search(signal_name)
    alarm_time = ""
    remaining = signal_name
    if time_match:
        alarm_time = (
            f"{time_match.group('year')}-{time_match.group('month')}-{time_match.group('day')} "
            f"{time_match.group('hour')}:{time_match.group('minute')}:{time_match.group('second')}"
        )
        remaining = signal_name[time_match.end():].strip()

    tokens = remaining.split()
    station_name = tokens[0] if len(tokens) >= 1 else ""
    action = tokens[-1] if len(tokens) >= 1 else ""
    object_name = "".join(tokens[1:-1]) if len(tokens) >= 3 else ""

    return {
        "alarm_time": alarm_time,
        "station_name": station_name,
        "voltage_level": _infer_voltage_level(signal_name),
        "object_name": object_name,
        "action": action,
    }


def _infer_voltage_level(text: str) -> str:
    match = re.search(r"\d+kV", text)
    return match.group(0) if match else ""

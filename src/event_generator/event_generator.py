import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional


PLACEHOLDER_PATTERN = re.compile(r"\$([A-Z_][A-Z0-9_]*)")


def generate_events(
    rule_results: Iterable[Mapping[str, Any]],
    alarms: Optional[Iterable[Mapping[str, Any]]] = None,
    feature_hits: Optional[Mapping[str, List[str]]] = None,
    context: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Convert triggered rule results into frontend-friendly standard events."""
    alarm_list = list(alarms or [])
    event_context = _build_context(context or {}, alarm_list)
    hit_index = dict(feature_hits or {})

    events: List[Dict[str, Any]] = []
    for rule_result in rule_results:
      if not rule_result.get("triggered"):
          continue

      event_no = len(events) + 1
      matched_features = list(rule_result.get("matched_variables") or [])
      matched_alarms = _resolve_matched_alarms(rule_result, matched_features, hit_index)
      output_text = _render_output_text(
          str(rule_result.get("output_format") or rule_result.get("rule_name") or "未命名事件"),
          event_context,
      )

      event = {
          "event_id": f"EVT-{event_no:04d}",
          "source_rule_id": str(rule_result.get("source_rule_id", "")),
          "rule_name": rule_result.get("rule_name", ""),
          "event_type": rule_result.get("event_type", ""),
          "event_level": rule_result.get("event_level", ""),
          "output_text": output_text,
          "matched_alarms": matched_alarms,
          "matched_features": matched_features,
          "summary": _build_summary(rule_result, output_text),
          "reason": rule_result.get("reason", ""),
          "generated_at": datetime.now().isoformat(timespec="seconds"),
      }
      events.append(event)

    return {
        "events": events,
        "event_count": len(events),
        "level_stats": _count_by(events, "event_level"),
        "type_stats": _count_by(events, "event_type"),
    }


def _build_context(base_context: Mapping[str, str], alarms: List[Mapping[str, Any]]) -> Dict[str, str]:
    context = {key: str(value) for key, value in base_context.items() if value}
    if "DEV" not in context:
        context["DEV"] = _first_alarm_field(alarms, ("device_name", "object_name")) or ""
    if "LINE" not in context:
        context["LINE"] = _infer_line_name(alarms) or context.get("DEV", "")
    if "BAY" not in context:
        context["BAY"] = context.get("LINE") or context.get("DEV", "")
    return context


def _first_alarm_field(alarms: List[Mapping[str, Any]], field_names: Iterable[str]) -> str:
    for alarm in alarms:
        parsed = alarm.get("parsed") if isinstance(alarm.get("parsed"), dict) else {}
        for field_name in field_names:
            value = alarm.get(field_name) or parsed.get(field_name)
            if value:
                return str(value)
    return ""


def _infer_line_name(alarms: List[Mapping[str, Any]]) -> str:
    for alarm in alarms:
        text = str(alarm.get("raw_signal_name") or alarm.get("signal_name") or "")
        match = re.search(r"(\d+kV[^ ]*线路\d*|\d+kV\d+线路\d*|\d+线路\d*)", text)
        if match:
            return match.group(1)
    return ""


def _resolve_matched_alarms(
    rule_result: Mapping[str, Any],
    matched_features: List[str],
    feature_hits: Mapping[str, List[str]],
) -> List[str]:
    explicit = rule_result.get("matched_alarms")
    if explicit:
        return _unique_strings(explicit)

    alarm_ids: List[str] = []
    for feature_id in matched_features:
        alarm_ids.extend(feature_hits.get(feature_id, []))
    return _unique_strings(alarm_ids)


def _render_output_text(template: str, context: Mapping[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, "")

    rendered = PLACEHOLDER_PATTERN.sub(replace, template)
    return _normalize_space(rendered)


def _build_summary(rule_result: Mapping[str, Any], output_text: str) -> str:
    rule_name = rule_result.get("rule_name") or f"规则 {rule_result.get('source_rule_id', '')}"
    event_type = rule_result.get("event_type") or "告警事件"
    return f"系统根据规则“{rule_name}”识别出{event_type}：{output_text}。"


def _count_by(events: List[Mapping[str, Any]], field_name: str) -> Dict[str, int]:
    stats: Dict[str, int] = {}
    for event in events:
        key = str(event.get(field_name) or "未分类")
        stats[key] = stats.get(key, 0) + 1
    return stats


def _unique_strings(values: Iterable[Any]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

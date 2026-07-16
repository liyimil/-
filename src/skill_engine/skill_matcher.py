from typing import Any, Dict, List, Mapping, Optional


DEMO_FEATURES: List[Dict[str, Any]] = [
    {
        "feature_id": "@1",
        "feature_name": "线路保护A网中断",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["保护", "A网中断", "动作"],
                "feature_desc": "线路保护A网中断动作",
            }
        ],
    },
    {
        "feature_id": "@2",
        "feature_name": "线路保护B网中断",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["保护", "B网中断", "动作"],
                "feature_desc": "线路保护B网中断动作",
            }
        ],
    },
    {
        "feature_id": "@3",
        "feature_name": "保护异常确认",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["保护", "中断"],
                "feature_desc": "保护通信异常确认",
            }
        ],
    },
    {
        "feature_id": "@4",
        "feature_name": "开关分闸",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["开关", "分闸"],
                "feature_desc": "开关分闸动作",
            }
        ],
    },
    {
        "feature_id": "@5",
        "feature_name": "开关合闸",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["开关", "合闸"],
                "feature_desc": "开关合闸动作",
            }
        ],
    },
    {
        "feature_id": "@6",
        "feature_name": "远方操作确认",
        "expression": "@1=1",
        "signal_mappings": [
            {
                "index": "@1",
                "keywords": ["远方", "操作"],
                "feature_desc": "远方操作确认",
            }
        ],
    },
]


DEMO_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "5",
        "rule_name": "[精准]20kV线路故障（远方手合）",
        "expression": "(@1|@2)&@3&(@4|@5|@6)",
        "event_level": "事故",
        "event_type": "2-跳闸事件",
        "output_format": "$LINE 线路故障（远方手合）",
        "enabled": True,
    },
    {
        "rule_id": "902",
        "rule_name": "[基础]开关合上",
        "expression": "(@6)",
        "event_level": "告知",
        "event_type": "6-一般告知",
        "output_format": "$BAY 开关投入运行",
        "enabled": True,
    },
]


def match_skills(
    structured_alarms: Mapping[str, Any],
    features: Optional[Mapping[str, Any] | List[Dict[str, Any]]] = None,
    rules: Optional[Mapping[str, Any] | List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    alarms = structured_alarms.get("alarms", [])
    signal_mapping_states: Dict[str, Dict[str, Any]] = {}
    candidate_features = []
    feature_defs = _extract_items(features, "features") or DEMO_FEATURES
    rule_defs = _extract_items(rules, "rules") or DEMO_RULES

    for feature in feature_defs:
        feature_id = str(feature.get("feature_id", ""))
        if not feature_id:
            continue
        mapping_state: Dict[str, Any] = {}
        matched_alarms: List[str] = []
        for mapping in feature.get("signal_mappings", []):
            mapping_index = str(mapping.get("index", ""))
            if not mapping_index:
                continue
            matched_ids = _match_mapping(alarms, mapping)
            mapping_state[mapping_index] = bool(matched_ids)
            matched_alarms.extend(matched_ids)

        unique_alarm_ids = _unique(matched_alarms)
        if unique_alarm_ids:
            mapping_state["_matched_alarms"] = unique_alarm_ids
            candidate_features.append(_candidate_feature(feature, unique_alarm_ids))
        signal_mapping_states[feature_id] = mapping_state

    candidate_rules = [_candidate_rule(rule) for rule in rule_defs if _is_enabled(rule)]
    return {
        "dataset_id": structured_alarms.get("dataset_id", "demo-dataset"),
        "features": feature_defs,
        "rules": rule_defs,
        "candidate_feature_skills": candidate_features,
        "candidate_rule_skills": candidate_rules,
        "signal_mapping_states": signal_mapping_states,
    }


def _extract_items(payload: Optional[Mapping[str, Any] | List[Dict[str, Any]]], key: str) -> List[Dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    items = payload.get(key, [])
    return items if isinstance(items, list) else []


def _match_mapping(alarms: List[Mapping[str, Any]], mapping: Mapping[str, Any]) -> List[str]:
    matched = []
    keywords = [str(keyword) for keyword in mapping.get("keywords", []) if str(keyword)]
    candidates = _mapping_candidates(mapping)
    for alarm in alarms:
        text = _alarm_text(alarm)
        if keywords and all(keyword in text for keyword in keywords):
            matched.append(str(alarm.get("alarm_id", "")))
        elif not keywords and any(candidate in text for candidate in candidates):
            matched.append(str(alarm.get("alarm_id", "")))
    return matched


def _candidate_feature(feature: Mapping[str, Any], alarm_ids: List[str]) -> Dict[str, Any]:
    feature_id = str(feature.get("feature_id", ""))
    return {
        "skill_id": f"FEATURE_{feature_id.lstrip('@').zfill(3)}",
        "source_feature_id": feature_id,
        "feature_name": feature.get("feature_name", ""),
        "skill_path": f"skills/features/FEATURE_{feature_id.lstrip('@').zfill(3)}.md",
        "match_score": 1.0,
        "match_reason": f"命中告警：{', '.join(alarm_ids)}",
    }


def _candidate_rule(rule: Mapping[str, Any]) -> Dict[str, Any]:
    rule_id = str(rule.get("rule_id", ""))
    return {
        "skill_id": f"RULE_{rule_id.zfill(4)}",
        "source_rule_id": rule_id,
        "rule_name": rule.get("rule_name", ""),
        "skill_path": f"skills/event_rules/RULE_{rule_id.zfill(4)}.md",
        "match_score": 1.0,
        "match_reason": "规则已加载，可用于表达式求值",
    }


def _mapping_candidates(mapping: Mapping[str, Any]) -> List[str]:
    fields = ("object_name", "signal_feature", "feature_desc", "device_name", "object_type", "bay_name")
    candidates: List[str] = []
    for field in fields:
        value = str(mapping.get(field, "")).strip()
        if value and value not in {"空", "无", "-", "null", "None"} and len(value) >= 2:
            candidates.append(value)
    return _unique(candidates)


def _alarm_text(alarm: Mapping[str, Any]) -> str:
    parsed = alarm.get("parsed") or {}
    parts = [
        alarm.get("raw_signal_name", ""),
        alarm.get("station_name", ""),
        alarm.get("device_name", ""),
        alarm.get("voltage_level", ""),
        parsed.get("station_name", "") if isinstance(parsed, Mapping) else "",
        parsed.get("object_name", "") if isinstance(parsed, Mapping) else "",
        parsed.get("action", "") if isinstance(parsed, Mapping) else "",
    ]
    return " ".join(str(part) for part in parts if part)


def _is_enabled(rule: Mapping[str, Any]) -> bool:
    value = rule.get("enabled", True)
    if isinstance(value, str):
        return value.lower() not in {"false", "0", "停用", "disabled"}
    return bool(value)


def _unique(values: List[str]) -> List[str]:
    result = []
    seen = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result

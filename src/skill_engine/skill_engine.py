"""
SKILL 规则管理与智能匹配引擎 —— 课题 B：skill_engine。

职责：
1. 加载 features.json / rules.json（或接受外部传入）
2. 将 A 模块输出的结构化告警与 feature 内部的 signal_mappings 做运行时语义匹配
3. 输出 signal_mapping_states（双层 @n 索引）
4. 输出候选 Feature SKILL / Rule SKILL

两层 @n 映射关系（已确认）：
- rule.expression 中的 @n  → features.json 中 feature_id=@n 的全局特征
- feature.expression 中的 @n → 该 feature 内部 signal_mappings.index=@n 的局部信号

匹配策略：
- 优先级1：在告警 raw_signal_name + parsed 字段中精确包含 signal_mapping 的 object_name
- 优先级2：token 级分词匹配（按中文语义边界拆分）
- 优先级3：signal_type 枚举辅助匹配（NETWORK_A_DOWN → "A网" 类特征）
- 对 "特征_NNN" 等纯编号标记不做匹配，仅当其他字段有实际语义时才参与
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# 项目根目录
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# signal_type → 语义提示映射（辅助匹配，不替代关键词匹配）
# ---------------------------------------------------------------------------
SIGNAL_TYPE_HINTS: Dict[str, List[str]] = {
    "NETWORK_A_DOWN": ["A网", "通信中断", "保护A网"],
    "NETWORK_B_DOWN": ["B网", "通信中断", "保护B网"],
    "NETWORK_C_DOWN": ["C网", "通信中断", "保护C网"],
    "BREAKER_OPEN": ["开关", "分闸"],
    "BREAKER_CLOSE": ["开关", "合闸"],
    "DISCONNECTOR_OPEN": ["刀闸", "分闸"],
    "DISCONNECTOR_CLOSE": ["刀闸", "合闸"],
    "PROTECTION_TRIP": ["保护", "动作"],
    "PROTECTION_RESET": ["保护", "复归"],
    "CTRL_ACTIVE": ["测控", "动作"],
    "CTRL_RESET": ["测控", "复归"],
    "GENERAL_TRIP": ["动作"],
    "GENERAL_RESET": ["复归"],
    "GENERAL_FAULT": ["异常", "故障"],
}

# ---------------------------------------------------------------------------
# 忽略词（在 signal_mapping 中出现但没有实际匹配价值的占位文本）
# ---------------------------------------------------------------------------
_IGNORE_VALUES = {"空", "无", "-", "null", "None", ""}

# 纯编号特征名（如 "特征_805"），不作为匹配词
_FEATURE_ID_PATTERN = re.compile(r"^特征_\d+$")


def load_json(path: Path) -> Dict[str, Any]:
    """加载 JSON 文件。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(payload: Mapping[str, Any], path: Path) -> None:
    """保存 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ===================================================================
# 核心匹配函数
# ===================================================================


def match_skills(
    structured_alarms: Mapping[str, Any],
    features: Optional[Mapping[str, Any] | List[Dict[str, Any]]] = None,
    rules: Optional[Mapping[str, Any] | List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """B 模块主入口：将结构化告警与 Feature/Rule 定义做语义匹配。

    Args:
        structured_alarms: A 模块输出的结构化告警（含 parsed + 扁平字段）
        features: features.json 的整体内容 或 feature 列表；None 则自动从默认路径加载
        rules: rules.json 的整体内容 或 rule 列表；None 则自动从默认路径加载

    Returns:
        包含 candidate_feature_skills、candidate_rule_skills、
        signal_mapping_states 的字典，同时返回 features 和 rules
        供下游 C 模块直接消费
    """
    # ── 加载 features / rules ──
    feature_defs = _resolve_items(features, "features", "features.json")
    rule_defs = _resolve_items(rules, "rules", "rules.json")

    alarms = list(structured_alarms.get("alarms", []))

    # ── 按 feature_id 建立快速索引 ──
    feature_index: Dict[str, Dict[str, Any]] = {}
    for feature in feature_defs:
        feature_id = str(feature.get("feature_id", ""))
        if feature_id:
            feature_index[feature_id] = feature

    # ── 核心匹配：对每个 feature 逐 signal_mapping 匹配告警 ──
    signal_mapping_states: Dict[str, Dict[str, bool]] = {}
    feature_hit_alarms: Dict[str, List[str]] = {}  # feature_id → alarm_id list

    for feature_id, feature in feature_index.items():
        mapping_states, matched_ids = _match_feature(feature, alarms)
        signal_mapping_states[feature_id] = mapping_states
        if matched_ids:
            feature_hit_alarms[feature_id] = matched_ids

    # ── 构建候选 Feature SKILL ──
    candidate_feature_skills = _build_candidate_features(
        feature_index, feature_hit_alarms
    )

    # ── 构建候选 Rule SKILL ──
    candidate_rule_skills = _build_candidate_rules(rule_defs, feature_index)

    return {
        "dataset_id": structured_alarms.get("dataset_id", "samples-md"),
        "source": {
            "feature_count": len(feature_defs),
            "rule_count": len(rule_defs),
            "alarm_count": len(alarms),
            "matched_feature_count": len(candidate_feature_skills),
            "matched_rule_count": len(candidate_rule_skills),
        },
        "features": feature_defs,
        "rules": rule_defs,
        "candidate_feature_skills": candidate_feature_skills,
        "candidate_rule_skills": candidate_rule_skills,
        "signal_mapping_states": signal_mapping_states,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# ===================================================================
# Feature 级匹配
# ===================================================================


def _match_feature(
    feature: Dict[str, Any], alarms: List[Dict[str, Any]]
) -> Tuple[Dict[str, bool], List[str]]:
    """对单个 feature 的所有 signal_mappings 逐一匹配告警。

    Returns:
        (mapping_states: {signal_index: bool}, matched_alarm_ids: [...])
    """
    mapping_states: Dict[str, bool] = {}
    all_matched_alarm_ids: List[str] = []

    for mapping in feature.get("signal_mappings", []):
        index = str(mapping.get("index", ""))
        if not index:
            continue

        matched_ids = _match_signal_mapping_against_alarms(mapping, alarms)
        mapping_states[index] = bool(matched_ids)
        all_matched_alarm_ids.extend(matched_ids)

    # 按出现顺序去重
    seen: Set[str] = set()
    unique_ids: List[str] = []
    for aid in all_matched_alarm_ids:
        if aid not in seen:
            seen.add(aid)
            unique_ids.append(aid)

    # 注入 _matched_alarms 方便下游直接取用
    mapping_states["_matched_alarms"] = unique_ids

    return mapping_states, unique_ids


# ===================================================================
# Signal Mapping → Alarm 匹配核心
# ===================================================================


def _match_signal_mapping_against_alarms(
    mapping: Dict[str, Any], alarms: List[Dict[str, Any]]
) -> List[str]:
    """判断 signal_mapping 是否被任意告警命中。返回命中告警的 alarm_id 列表。

    匹配策略（多级，有一级命中即视为匹配）：
    1. 精确包含：object_name 整体出现在告警文本中
    2. Token 匹配：object_name 拆分后的有意义 token 全部命中
    3. device_name / object_type 辅助匹配
    4. signal_type 提示匹配
    """
    # ── 提取匹配关键词 ──
    primary_phrase = _extract_primary_phrase(mapping)
    secondary_phrases = _extract_secondary_phrases(mapping)

    matched_ids: List[str] = []
    for alarm in alarms:
        if _alarm_matches(alarm, primary_phrase, secondary_phrases, mapping):
            matched_ids.append(str(alarm.get("alarm_id", "")))

    return matched_ids


def _alarm_matches(
    alarm: Dict[str, Any],
    primary_phrase: Optional[str],
    secondary_phrases: List[str],
    mapping: Dict[str, Any],
) -> bool:
    """多级匹配：精确 > 智能分词 > 子串交集 > 信号类型提示。"""
    search_text = _build_alarm_search_text(alarm)
    signal_type = str(alarm.get("signal_type", ""))

    # ── 级别 1：精确包含匹配 ──
    if primary_phrase and primary_phrase in search_text:
        return True

    # ── 级别 2：智能分词阈值匹配 ──
    if primary_phrase:
        tokens = _tokenize_smart(primary_phrase)
        valid_tokens = [t for t in tokens if _is_valid_match_token(t)]
        if valid_tokens:
            hit_count = sum(1 for t in valid_tokens if t in search_text)
            ratio = hit_count / len(valid_tokens)
            # 阈值：>= 50% 的 token 命中即认为匹配
            if ratio >= 0.5 and hit_count >= 1:
                return True

    # ── 级别 2b：character bigram 交集匹配（对中文短语模糊匹配） ──
    if primary_phrase:
        bigrams = _extract_bigrams(primary_phrase)
        valid_bigrams = [b for b in bigrams if _is_valid_match_token(b)]
        if valid_bigrams:
            hit_count = sum(1 for b in valid_bigrams if b in search_text)
            ratio = hit_count / len(valid_bigrams)
            # 阈值：>= 30% 的 bigram 命中
            if ratio >= 0.3 and hit_count >= 2:
                return True

    # ── 级别 3：secondary phrases 任一精确命中 ──
    for phrase in secondary_phrases:
        if phrase in search_text:
            return True

    # ── 级别 4：signal_type 提示匹配 ──
    hints = SIGNAL_TYPE_HINTS.get(signal_type, [])
    if hints and primary_phrase:
        for hint in hints:
            if len(hint) >= 2 and hint in primary_phrase and hint in search_text:
                return True

    return False


# ===================================================================
# 关键词提取
# ===================================================================


def _extract_primary_phrase(mapping: Dict[str, Any]) -> Optional[str]:
    """从 signal_mapping 中提取主匹配短语（object_name 优先）。

    返回 None 表示该 mapping 无有效主短语，仅靠辅助字段匹配。
    """
    candidates = [
        mapping.get("object_name", ""),
        mapping.get("signal_feature", ""),
        mapping.get("feature_desc", ""),
    ]
    for val in candidates:
        text = str(val).strip()
        if _is_meaningful(text):
            return text
    return None


def _extract_secondary_phrases(mapping: Dict[str, Any]) -> List[str]:
    """提取辅助匹配短语：device_name、object_type 等。"""
    phrases: List[str] = []
    for key in ("device_name", "object_type", "bay_name"):
        val = str(mapping.get(key, "")).strip()
        if _is_meaningful(val):
            phrases.append(val)
    return phrases


def _is_meaningful(text: str) -> bool:
    """判断文本是否为有意义的关键词（排除占位符和纯编号）。"""
    if not text or text in _IGNORE_VALUES:
        return False
    if _FEATURE_ID_PATTERN.match(text):
        return False
    # 排除纯数字/编号
    if re.match(r"^\d+$", text):
        return False
    return True


# ===================================================================
# 文本 tokenization
# ===================================================================

# 中文语义边界拆分模式（标点分隔）
_TOKEN_SPLIT_RE = re.compile(
    r"[，,。\.、\s/\\\-—|&｜()（）\[\]【】{}「」『』\"'':;；!！?？]+"
)

# 常见电力领域短词（用于在长 CJK 段中做辅助切分）
_DOMAIN_BOUNDARY_WORDS = [
    "保护", "测控", "开关", "刀闸", "接地", "线路",
    "装置", "通道", "通信", "中断", "异常", "故障",
    "直流", "交流", "系统", "母线", "充电", "输入",
    "主供", "失灵", "出口", "动作", "复归",
]


def _tokenize_smart(text: str) -> List[str]:
    """智能中文分词：按字符类型边界 + 领域词边界拆分。

    例如 "保护装置A网通信中断" → ["保护", "装置", "A", "网", "通信", "中断"]
    """
    # Step 1: 按字符类型边界拆分
    segments = _split_by_char_type(text)

    # Step 2: 对纯 CJK 长片段（>= 4 字），用领域词辅助切片
    result: List[str] = []
    for seg in segments:
        if _is_pure_cjk(seg) and len(seg) >= 4:
            result.extend(_split_cjk_by_domain(seg))
        else:
            result.append(seg)
    return result


def _split_by_char_type(text: str) -> List[str]:
    """按字符类型边界拆分（CJK / 拉丁字母 / 数字 / 罗马数字 / 其他）。"""
    if not text:
        return []
    segments: List[str] = []
    current = ""
    prev_type = ""

    for ch in text:
        ctype = _char_type(ch)
        if ctype != prev_type and current:
            segments.append(current)
            current = ch
        else:
            current += ch
        prev_type = ctype

    if current:
        segments.append(current)
    return segments


def _split_cjk_by_domain(text: str) -> List[str]:
    """用领域词表对纯 CJK 文本做辅助切分，同时保留 2-gram 作为备选。"""
    # 尝试用领域词匹配切分
    tokens: List[str] = []
    i = 0
    while i < len(text):
        matched = False
        for word in _DOMAIN_BOUNDARY_WORDS:
            if text[i:].startswith(word) and len(word) >= 2:
                tokens.append(word)
                i += len(word)
                matched = True
                break
        if not matched:
            # 未匹配，取单个字符
            tokens.append(text[i])
            i += 1

    # 合并单字 token 到相邻域词
    merged: List[str] = []
    buf = ""
    for tok in tokens:
        if len(tok) == 1 and _is_pure_cjk(tok):
            buf += tok
        else:
            if buf:
                merged.append(buf)
                buf = ""
            merged.append(tok)
    if buf:
        merged.append(buf)

    # 过滤长度 < 2 的单字（除非是唯一的 token）
    filtered = [t for t in merged if len(t) >= 2]
    return filtered if filtered else merged


def _char_type(ch: str) -> str:
    """判断字符类型。"""
    if "\u4e00" <= ch <= "\u9fff":
        return "cjk"
    if ch.isdigit():
        return "digit"
    if ch.isalpha() and ord(ch) < 128:
        return "ascii"
    if ch in "\u2160\u2161\u2162\u2163\u2164\u2165\u2166\u2167\u2168\u2169":
        return "roman"
    if ch in "ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ":
        return "roman_fullwidth"
    return "other"


def _is_pure_cjk(text: str) -> bool:
    """判断文本是否全部由 CJK 字符组成。"""
    return all("\u4e00" <= ch <= "\u9fff" for ch in text)


def _extract_bigrams(text: str) -> List[str]:
    """提取所有连续的 2-gram 子串（用于模糊匹配）。"""
    if len(text) < 2:
        return []
    return [text[i : i + 2] for i in range(len(text) - 1)]


def _is_valid_match_token(token: str) -> bool:
    """判断 token 是否为有效的匹配单元（排除过短或纯数字的）。"""
    if len(token) < 2:
        return False
    if re.match(r"^\d+$", token):
        return False
    return True


def _build_alarm_search_text(alarm: Dict[str, Any]) -> str:
    """构建告警搜索文本（拼接所有可搜索字段）。"""
    parsed = alarm.get("parsed") or {}
    if not isinstance(parsed, dict):
        parsed = {}

    parts = [
        str(alarm.get("raw_signal_name", "")),
        str(alarm.get("signal_name", "")),
        str(alarm.get("station_name", "")),
        str(alarm.get("device_name", "")),
        str(alarm.get("voltage_level", "")),
        str(parsed.get("station_name", "")),
        str(parsed.get("object_name", "")),
        str(parsed.get("action", "")),
        str(alarm.get("device", "")),
        str(alarm.get("action", "")),
        str(alarm.get("station", "")),
        str(alarm.get("signal_type", "")),
    ]
    return " ".join(p for p in parts if p)


# ===================================================================
# 候选 SKILL 构建
# ===================================================================


def _build_candidate_features(
    feature_index: Dict[str, Dict[str, Any]],
    feature_hit_alarms: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
    """构建候选 Feature SKILL 列表。

    只包含至少命中一条告警的 feature。
    """
    candidates: List[Dict[str, Any]] = []
    for feature_id in sorted(feature_hit_alarms.keys()):
        feature = feature_index.get(feature_id)
        if not feature:
            continue
        alarm_ids = feature_hit_alarms[feature_id]
        padded_id = feature_id.lstrip("@").zfill(3)
        candidates.append(
            {
                "skill_id": f"FEATURE_{padded_id}",
                "source_feature_id": feature_id,
                "feature_name": feature.get("feature_name", ""),
                "skill_path": f"skills/features/FEATURE_{padded_id}.md",
                "match_score": 1.0,
                "matched_alarm_count": len(alarm_ids),
                "match_reason": f"命中告警：{', '.join(alarm_ids[:5])}"
                + (f" 等共{len(alarm_ids)}条" if len(alarm_ids) > 5 else ""),
            }
        )
    return candidates


def _build_candidate_rules(
    rule_defs: List[Dict[str, Any]],
    feature_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """构建候选 Rule SKILL 列表。

    所有启用的规则都会被列为候选规则。
    是否真正触发由 C 模块的表达式求值决定。
    """
    candidates: List[Dict[str, Any]] = []
    for rule in rule_defs:
        if not _is_enabled(rule):
            continue
        rule_id = str(rule.get("rule_id", ""))
        if not rule_id:
            continue
        padded_id = rule_id.zfill(4)
        # 检查 rule.expression 中引用的 feature 是否至少有一个已命中
        expression = str(rule.get("expression", ""))
        referenced_features = re.findall(r"@\w+", expression)
        has_relevant_features = any(
            fid in feature_index for fid in referenced_features
        )

        candidates.append(
            {
                "skill_id": f"RULE_{padded_id}",
                "source_rule_id": rule_id,
                "rule_name": rule.get("rule_name", ""),
                "skill_path": f"skills/event_rules/RULE_{padded_id}.md",
                "match_score": 1.0,
                "enabled": True,
                "referenced_feature_count": len(referenced_features),
                "match_reason": (
                    "规则已加载，引用特征可用于表达式求值"
                    if has_relevant_features
                    else "规则已加载（表达式引用的特征未在 features.json 中定义）"
                ),
            }
        )
    return candidates


# ===================================================================
# 辅助工具
# ===================================================================


def _resolve_items(
    payload: Optional[Mapping[str, Any] | List[Dict[str, Any]]],
    key: str,
    fallback_filename: str,
) -> List[Dict[str, Any]]:
    """从 payload 或默认文件路径加载 items 列表。"""
    if payload is not None:
        if isinstance(payload, list):
            return payload
        items = payload.get(key, [])
        if items:
            return items if isinstance(items, list) else []

    # 自动从默认路径加载
    default_path = PROJECT_ROOT / "data" / "samples" / "samples-md" / fallback_filename
    if default_path.exists():
        data = load_json(default_path)
        items = data.get(key, [])
        return items if isinstance(items, list) else []

    # 回退：尝试不带 samples-md 的路径
    alt_path = PROJECT_ROOT / "data" / "samples" / fallback_filename
    if alt_path.exists():
        data = load_json(alt_path)
        items = data.get(key, [])
        return items if isinstance(items, list) else []

    return []


def _is_enabled(rule: Dict[str, Any]) -> bool:
    """判断规则是否启用。"""
    value = rule.get("enabled", True)
    if isinstance(value, str):
        return value.lower() not in {"false", "0", "停用", "disabled"}
    return bool(value)


# ===================================================================
# CLI 入口
# ===================================================================


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="课题B：SKILL 规则管理与智能匹配 —— 将 A 的结构化告警与 signal_mappings 匹配"
    )
    parser.add_argument(
        "--input",
        default=str(
            PROJECT_ROOT / "data" / "generated" / "structured_alarms.json"
        ),
        help="A 模块输出的结构化告警 JSON 路径",
    )
    parser.add_argument(
        "--features",
        default=str(
            PROJECT_ROOT / "data" / "samples" / "samples-md" / "features.json"
        ),
        help="features.json 路径",
    )
    parser.add_argument(
        "--rules",
        default=str(
            PROJECT_ROOT / "data" / "samples" / "samples-md" / "rules.json"
        ),
        help="rules.json 路径",
    )
    parser.add_argument(
        "--output",
        default=str(
            PROJECT_ROOT / "data" / "generated" / "skill_match.json"
        ),
        help="输出 skill_match.json 路径",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    features_path = Path(args.features)
    rules_path = Path(args.rules)
    output_path = Path(args.output)

    print(f"[skill_engine] 读取 A 输出: {input_path}")
    if not input_path.exists():
        print(
            f"[skill_engine] ⚠ A 输出文件不存在，请先运行 perception_agent\n"
            f"   python src/perception_agent/perception_agent.py "
            f"--input data/samples/samples-md/alarms.json"
        )
        raise SystemExit(1)

    structured = load_json(input_path)

    print(f"[skill_engine] 加载 features: {features_path}")
    features_data = load_json(features_path)

    print(f"[skill_engine] 加载 rules: {rules_path}")
    rules_data = load_json(rules_path)

    result = match_skills(structured, features=features_data, rules=rules_data)
    save_json(result, output_path)

    source = result["source"]
    print(
        f"[skill_engine] 匹配完成: "
        f"{source['matched_feature_count']}/{source['feature_count']} 特征命中, "
        f"{source['matched_rule_count']}/{source['rule_count']} 规则候选 → {output_path}"
    )


if __name__ == "__main__":
    main()

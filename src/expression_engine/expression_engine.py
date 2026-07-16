import re
from typing import Any, Dict, List, Mapping, Tuple

from src.skill_engine import DEMO_FEATURES, DEMO_RULES


TOKEN_PATTERN = re.compile(r"@\w+|[()&|!]|=|[01]")


def evaluate_rules(skill_match: Mapping[str, Any]) -> Dict[str, Any]:
    signal_mapping_states = skill_match.get("signal_mapping_states", {})
    feature_states: Dict[str, bool] = {}
    feature_hits: Dict[str, List[str]] = {}
    feature_errors: Dict[str, str] = {}
    features = skill_match.get("features") or DEMO_FEATURES
    rules = skill_match.get("rules") or DEMO_RULES

    for feature in features:
        feature_id = str(feature.get("feature_id", ""))
        if not feature_id:
            continue
        local_states = signal_mapping_states.get(feature_id, {})
        try:
            feature_states[feature_id] = evaluate_expression(str(feature.get("expression", "")), local_states)
        except ValueError as exc:
            feature_states[feature_id] = False
            feature_errors[feature_id] = str(exc)
        if feature_states[feature_id]:
            feature_hits[feature_id] = list(local_states.get("_matched_alarms", []))

    rule_results = [_evaluate_rule(rule, feature_states, feature_hits) for rule in rules]
    return {
        "dataset_id": skill_match.get("dataset_id", "demo-dataset"),
        "feature_states": feature_states,
        "feature_hits": feature_hits,
        "feature_errors": feature_errors,
        "rule_results": rule_results,
    }


def evaluate_expression(expression: str, states: Mapping[str, Any]) -> bool:
    normalized = _normalize_expression(expression)
    if normalized.startswith("["):
        return _evaluate_threshold_expression(normalized, states)
    tokens = TOKEN_PATTERN.findall(normalized)
    if not tokens:
        return False
    parser = _ExpressionParser(tokens, states)
    value = parser.parse_or()
    if parser.position != len(tokens):
        raise ValueError(f"Unexpected token: {tokens[parser.position]}")
    return bool(value)


def _evaluate_rule(
    rule: Mapping[str, Any],
    feature_states: Mapping[str, bool],
    feature_hits: Mapping[str, List[str]],
) -> Dict[str, Any]:
    expression = str(rule.get("expression", ""))
    error = ""
    try:
        triggered = evaluate_expression(expression, feature_states)
    except ValueError as exc:
        triggered = False
        error = str(exc)
    variables = _extract_variables(expression)
    matched_variables = [variable for variable in variables if feature_states.get(variable, False)]
    unmatched_variables = [variable for variable in variables if not feature_states.get(variable, False)]
    matched_alarms: List[str] = []
    for variable in matched_variables:
        matched_alarms.extend(feature_hits.get(variable, []))

    return {
        "source_rule_id": str(rule.get("rule_id", "")),
        "rule_name": rule.get("rule_name", ""),
        "expression": expression,
        "triggered": triggered,
        "matched_variables": matched_variables,
        "unmatched_variables": unmatched_variables,
        "event_level": rule.get("event_level", ""),
        "event_type": rule.get("event_type", ""),
        "output_format": rule.get("output_format", ""),
        "matched_alarms": _unique(matched_alarms),
        "reason": f"表达式解析失败：{error}" if error else ("表达式求值结果为 true。" if triggered else "表达式求值结果为 false。"),
    }


def _normalize_expression(expression: str) -> str:
    return (
        expression.replace("（", "(")
        .replace("）", ")")
        .replace("&&", "&")
        .replace("||", "|")
        .replace(" ", "")
    )


def _evaluate_threshold_expression(expression: str, states: Mapping[str, Any]) -> bool:
    threshold_match = re.match(r"\[(\d+),", expression)
    if not threshold_match:
        raise ValueError(f"Invalid threshold expression: {expression}")
    threshold = int(threshold_match.group(1))
    variables = _extract_variables(expression)
    matched_count = sum(1 for variable in variables if bool(states.get(variable, False)))
    return matched_count >= threshold


def _extract_variables(expression: str) -> List[str]:
    return _unique(re.findall(r"@\w+", expression))


def _unique(values: List[str]) -> List[str]:
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


class _ExpressionParser:
    def __init__(self, tokens: List[str], states: Mapping[str, Any]) -> None:
        self.tokens = tokens
        self.states = states
        self.position = 0

    def parse_or(self) -> bool:
        value = self.parse_and()
        while self._match("|"):
            right = self.parse_and()
            value = value or right
        return value

    def parse_and(self) -> bool:
        value = self.parse_not()
        while self._match("&"):
            right = self.parse_not()
            value = value and right
        return value

    def parse_not(self) -> bool:
        if self._match("!"):
            return not self.parse_not()
        return self.parse_atom()

    def parse_atom(self) -> bool:
        if self._match("("):
            value = self.parse_or()
            self._consume(")")
            return value

        token = self._advance()
        if token in ("0", "1"):
            return token == "1"
        if token.startswith("@"):
            if self._match("="):
                expected = self._advance()
                return bool(self.states.get(token, False)) == (expected == "1")
            return bool(self.states.get(token, False))
        raise ValueError(f"Unexpected token: {token}")

    def _match(self, expected: str) -> bool:
        if self.position < len(self.tokens) and self.tokens[self.position] == expected:
            self.position += 1
            return True
        return False

    def _consume(self, expected: str) -> None:
        if not self._match(expected):
            actual = self.tokens[self.position] if self.position < len(self.tokens) else "<eof>"
            raise ValueError(f"Expected {expected}, got {actual}")

    def _advance(self) -> str:
        if self.position >= len(self.tokens):
            raise ValueError("Unexpected end of expression")
        token = self.tokens[self.position]
        self.position += 1
        return token

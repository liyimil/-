"""
课题 B：SKILL 规则管理与智能匹配模块。

核心接口：
    match_skills(structured_alarms, features=None, rules=None)
    → 返回 candidate_feature_skills、candidate_rule_skills、signal_mapping_states

CLI 用法：
    python src/skill_engine/skill_engine.py --input structured_alarms.json
"""

from .skill_engine import match_skills

__all__ = ["match_skills"]

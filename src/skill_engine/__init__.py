"""
课题 B：SKILL 规则管理与智能匹配模块。

核心接口：
    match_skills(structured_alarms, features=None, rules=None)
    → 返回 candidate_feature_skills、candidate_rule_skills、signal_mapping_states

    generate_skill_files(features_data, rules_data)
    → 批量生成 Feature SKILL / Rule SKILL .md 文件

CLI 用法：
    # 运行匹配
    python src/skill_engine/skill_engine.py --input structured_alarms.json

    # 生成 SKILL 文件
    python src/skill_engine/skill_engine.py --generate-skills --features features.json --rules rules.json
"""

from .skill_engine import generate_skill_files, match_skills

__all__ = ["generate_skill_files", "match_skills"]

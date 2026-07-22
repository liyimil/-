"""
模拟告警数据生成引擎 —— 课题 A：alarm_generator。

职责：
- 基于真实电网运行场景构造**典型告警序列**（非孤立单条）。
- 模拟故障爆发时 3~8 条关联告警在 1~2 秒内连续产生的真实模式。
- 输出到 data/generated/，不修改原始样例文件。

设计原则：
- 场景驱动：按故障模板生成突发序列，而非逐条随机拼凑。
- 字段一致：顶级字段与 signal_name 内容严格匹配。
- 命名规范：开关/刀闸不加 kV 前缀，线路保护/测控才加。
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# 时间基准（与原始数据对齐：2023-08-29）
# ---------------------------------------------------------------------------

_BASE_REFERENCE = datetime(2023, 8, 29, 0, 0, 0)

# 用于从 signal_name 中提取时间做全局排序
_TIME_RE = re.compile(
    r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(\d{1,2}):(\d{2}):(\d{2})"
)


def _extract_time_from_signal(signal_name: str) -> datetime:
    """从 signal_name 中解析时间，用于排序。解析失败返回 datetime.min。"""
    m = _TIME_RE.search(signal_name)
    if m:
        y, mo, d, h, mi, s = m.groups()
        return datetime(int(y), int(mo), int(d), int(h), int(mi), int(s))
    return datetime.min

# ---------------------------------------------------------------------------
# 厂站参数池
# ---------------------------------------------------------------------------

_STATION_POOL: List[Tuple[str, str]] = [
    ("20kV示范变电站", "20kV"),
    ("20kV新华变电站", "20kV"),
    ("20kV城东变电站", "20kV"),
    ("35kV城南变电站", "35kV"),
    ("10kV工业园变电站", "10kV"),
]

# 设备编号前缀
_DEVICE_NUM_POOL = ["101", "102", "103", "201", "202", "203", "301", "302", "401", "402"]

# ---------------------------------------------------------------------------
# 设备分类（决定是否加电压前缀）
# ---------------------------------------------------------------------------

# 不加电压前缀：开关、刀闸、接地刀闸
_DEVICE_NO_PREFIX = {"开关", "刀闸", "接地刀闸"}

# 加电压前缀：线路保护、线路测控
_DEVICE_WITH_PREFIX = {"线路1保护", "线路2保护", "线路1测控", "线路2测控"}


def _needs_voltage_prefix(device_noun: str) -> bool:
    """判断该设备类型在 signal_name 中是否需要电压前缀。"""
    return device_noun in _DEVICE_WITH_PREFIX


# ---------------------------------------------------------------------------
# 典型故障场景模板（核心）
# ---------------------------------------------------------------------------

SCENARIO_TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "线路跳闸（开关+刀闸联动）",
        "interval_seconds": 1,
        "steps": [
            {"device_noun": "线路1保护", "action": "动作(全数据判定)"},
            {"device_noun": "开关",          "action": "分闸"},
            {"device_noun": "刀闸",          "action": "分闸"},
            {"device_noun": "接地刀闸",       "action": "分闸"},
        ],
    },
    {
        "name": "线路跳闸后重合成功",
        "interval_seconds": 1,
        "steps": [
            {"device_noun": "线路1保护", "action": "动作(全数据判定)"},
            {"device_noun": "开关",          "action": "分闸"},
            {"device_noun": "开关",          "action": "合闸"},
        ],
    },
    {
        "name": "保护通道A网中断（双套同时）",
        "interval_seconds": 0,
        "steps": [
            {"device_noun": "线路1保护", "action": "保护A网中断"},
            {"device_noun": "线路2保护", "action": "保护A网中断"},
        ],
    },
    {
        "name": "测控A网中断后复归",
        "interval_seconds": 2,
        "steps": [
            {"device_noun": "线路1测控", "action": "测控A网中断"},
            {"device_noun": "线路1测控", "action": "复归"},
        ],
    },
    {
        "name": "保护动作后复归",
        "interval_seconds": 3,
        "steps": [
            {"device_noun": "线路1保护", "action": "动作"},
            {"device_noun": "线路1保护", "action": "复归"},
        ],
    },
    {
        "name": "多开关联动分闸",
        "interval_seconds": 1,
        "steps": [
            {"device_noun": "开关",  "action": "分闸"},
            {"device_noun": "刀闸",  "action": "分闸"},
            {"device_noun": "刀闸",  "action": "分闸"},
            {"device_noun": "开关",  "action": "分闸"},
        ],
    },
    {
        "name": "线路跳闸+保护通道异常",
        "interval_seconds": 1,
        "steps": [
            {"device_noun": "线路1保护", "action": "保护A网中断"},
            {"device_noun": "线路1保护", "action": "动作(全数据判定)"},
            {"device_noun": "开关",          "action": "分闸"},
            {"device_noun": "刀闸",          "action": "分闸"},
        ],
    },
]


# ---------------------------------------------------------------------------
# signal_name 构造
# ---------------------------------------------------------------------------

def _make_signal_name(
    station: str,
    device: str,
    action: str,
    ts: datetime,
    voltage: str,
    device_noun: str,
) -> str:
    """构造一条符合真实格式的 signal_name。

    规则：
    - 开关/刀闸：不加 kV 前缀，如 "101开关"
    - 线路保护/测控：加 kV 前缀，如 "10kV101线路1保护"
    """
    time_part = ts.strftime("%Y年%m月%d日 %H:%M:%S")

    if _needs_voltage_prefix(device_noun):
        dev = f"{voltage}{device}"
    else:
        dev = device

    return f"{time_part} {station} {dev} {action}"


# ---------------------------------------------------------------------------
# 场景爆发生成
# ---------------------------------------------------------------------------

def _generate_scenario_burst(
    scenario: Dict[str, Any],
    station: str,
    voltage: str,
    device_num: str,
    base_time: datetime,
) -> List[Dict[str, Any]]:
    """根据场景模板生成一次故障爆发序列（不含 alarm_id，无副作用）。

    alarm_id 由调用方在确认场景可加入后再分配，避免计数器空洞。
    """
    burst: List[Dict[str, Any]] = []
    interval = scenario.get("interval_seconds", 1)

    for idx, step in enumerate(scenario["steps"]):
        device_noun = step["device_noun"]
        action = step["action"]
        device = f"{device_num}{device_noun}"
        ts = base_time + timedelta(seconds=idx * interval)

        signal_name = _make_signal_name(
            station=station,
            device=device,
            action=action,
            ts=ts,
            voltage=voltage,
            device_noun=device_noun,
        )

        burst.append({
            "station_name": station,
            "device_name": device,
            "voltage_level": voltage,
            "signal_name": signal_name,
            "signal_value": 1,
        })

    return burst


# ---------------------------------------------------------------------------
# 主生成函数
# ---------------------------------------------------------------------------

def generate_extended_alarms(
    template_alarms: List[Dict[str, Any]],
    count: int = 50,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """基于场景模板生成典型告警序列。

    策略：
    1. 随机选择场景模板 + 厂站 + 设备编号。
    2. 每个场景内部按时间间隔生成连续告警（2~4 条）。
    3. 场景完整性优先：场景要么完整保留，要么整组跳过，不截断。
    4. 最终数量可能略少于 count（差距不超过最大场景步数）。

    Args:
        template_alarms: 原始告警列表（仅用于计数参考，不复制内容）
        count: 需要生成的告警总数（软上限，保证场景完整性）
        seed: 随机种子，保证可复现

    Returns:
        (告警列表, 实际使用的场景名称集合)
    """
    random.seed(seed)

    result: List[Dict[str, Any]] = []
    used_scenarios: set = set()
    counter = 1

    while len(result) < count:
        # 随机选择：厂站 + 设备编号 + 场景
        station, voltage = random.choice(_STATION_POOL)
        device_num = random.choice(_DEVICE_NUM_POOL)
        scenario = random.choice(SCENARIO_TEMPLATES)

        base_time = _BASE_REFERENCE + timedelta(
            seconds=random.randint(0, 24 * 3600 - 1)
        )

        burst = _generate_scenario_burst(
            scenario=scenario,
            station=station,
            voltage=voltage,
            device_num=device_num,
            base_time=base_time,
        )

        # 场景完整性优先：放得下完整场景才加入
        if len(result) + len(burst) <= count:
            # 确认加入后分配连续 ID，避免计数器空洞
            for item in burst:
                item["alarm_id"] = f"ALM-GEN-{counter:04d}"
                counter += 1
            result.extend(burst)
            used_scenarios.add(scenario["name"])
        else:
            break

    # 无需截断，每个场景都是完整的；按时间全局排序
    result.sort(key=lambda a: _extract_time_from_signal(a["signal_name"]))

    return result, used_scenarios


# ---------------------------------------------------------------------------
# 完整流程
# ---------------------------------------------------------------------------

def run_generation(
    input_path: Path,
    output_path: Path,
    extra_count: int = 50,
    seed: int = 42,
) -> Dict[str, Any]:
    """完整流程：读取原始告警 → 生成扩展数据 → 合并写入。

    Args:
        input_path: 原始 alarms.json 路径
        output_path: 输出路径
        extra_count: 额外生成数量

    Returns:
        合并后的完整告警字典
    """
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    original = raw.get("alarms", [])
    generated, used_scenarios = generate_extended_alarms(
        original, count=extra_count, seed=seed
    )

    merged = {
        "description": "告警采样数据（含模拟场景扩展）",
        "version": "1.0",
        "scenario": "original + generated (scenario-based bursts)",
        "total_count": len(original) + len(generated),
        "original_count": len(original),
        "generated_count": len(generated),
        "used_scenario_count": len(used_scenarios),
        "used_scenario_names": sorted(used_scenarios),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "alarms": list(original) + generated,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(
        f"[alarm_generator] 原始 {len(original)} 条 + 生成 {len(generated)} 条 "
        f"(使用 {len(used_scenarios)}/{len(SCENARIO_TEMPLATES)} 个场景模板) → {output_path}"
    )
    return merged


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="课题A：模拟告警数据生成 —— 基于场景模板构造典型告警序列"
    )
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "data" / "samples" / "alarms.json"),
        help="原始告警数据路径",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "data" / "generated" / "extended_alarms.json"),
        help="输出扩展后告警数据路径",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="额外生成的告警数量",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    args = parser.parse_args()

    run_generation(
        input_path=Path(args.input),
        output_path=Path(args.output),
        extra_count=args.count,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()

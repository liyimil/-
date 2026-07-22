"""
感知智能体 —— 课题 A：告警数据感知与预处理。

职责：
1. 读取 alarms.json，解析 signal_name 文本字段
2. 提取告警时间、厂站名称、电压等级、设备对象名称、动作状态
3. 输出符合 contracts/module_contracts.md 的结构化告警 JSON
4. 输出到 data/generated/structured_alarms.json，供课题 B 消费
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 项目根目录
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# 正则编译（一次性，避免每次调用重复编译）
# ---------------------------------------------------------------------------

# 时间：2023年08月29日 17:08:38
_TIME_RE = re.compile(
    r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(\d{1,2}):(\d{2}):(\d{2})"
)

# 电压等级 + 厂站：20kV示范变电站 / 演示变电站
# 注：变电站前面可能有或不带电压前缀，如 "示范变电站"、"20kV示范变电站"
_STATION_WITH_VOLTAGE_RE = re.compile(
    r"(\d+kV)?\s*([\u4e00-\u9fa5]+变电站)"
)

# 单独电压等级：10kV / 20kV / 35kV / 110kV / 220kV
_VOLTAGE_RE = re.compile(r"(\d+kV)")

# 动作词列表（按长度降序排列，优先匹配长的）
# 设备关键词（用于合法性校验）
_DEVICE_KEYWORDS = [
    "开关", "刀闸", "保护", "测控", "线路", "接地",
    "母线", "主变", "变压器", "断路器", "隔离开关",
    "PT", "CT", "避雷器", "电容器", "电抗器",
]


# ---------------------------------------------------------------------------
# 标准化信号枚举映射
# ---------------------------------------------------------------------------

def map_to_signal_type(object_name: Optional[str], action: Optional[str]) -> str:
    """根据设备名和动作，生成标准信号枚举。

    课题 B 的 signal_mapping 依赖此枚举做特征匹配。
    若课题 B 有现成枚举表，直接替换此映射。

    判断优先级：动作语义 > 设备类型。
    网络中断类优先于开关变位类，避免 "101开关保护A网中断" 被误判为 BREAKER_OPEN。
    """
    if not object_name or not action:
        return "UNKNOWN"

    obj = object_name
    act = action

    # ── 优先级1：网络中断（语义明确，不受设备类型干扰） ──
    if "A网中断" in act:
        return "NETWORK_A_DOWN"
    if "B网中断" in act:
        return "NETWORK_B_DOWN"
    if "C网中断" in act:
        return "NETWORK_C_DOWN"

    # ── 优先级2：按设备类型细分（网络中断已在优先级1处理完毕） ──
    if "开关" in obj:
        if "分闸" in act:
            return "BREAKER_OPEN"
        if "合闸" in act:
            return "BREAKER_CLOSE"

    if "刀闸" in obj:
        if "分闸" in act:
            return "DISCONNECTOR_OPEN"
        if "合闸" in act:
            return "DISCONNECTOR_CLOSE"

    if "保护" in obj:
        if "动作" in act:
            return "PROTECTION_TRIP"
        if "复归" in act:
            return "PROTECTION_RESET"

    if "测控" in obj:
        if "动作" in act:
            return "CTRL_ACTIVE"
        if "复归" in act:
            return "CTRL_RESET"

    # ── 优先级3：通用动作兜底 ──
    if "动作" in act:
        return "GENERAL_TRIP"
    if "复归" in act:
        return "GENERAL_RESET"
    if "异常" in act:
        return "GENERAL_FAULT"

    return "UNKNOWN"


_ACTION_WORDS = [
    "A网中断", "B网中断", "C网中断",
    "测控A网中断", "测控B网中断", "测控C网中断",
    "保护A网中断", "保护B网中断", "保护C网中断",
    "动作(全数据判定)", "动作",
    "复归",
    "分闸", "合闸",
    "异常", "故障",
    "投入", "退出",
    "告警", "恢复",
    "接通", "断开",
]


def _parse_time(raw_signal: str) -> tuple[Optional[str], str]:
    """从 signal_name 中抽取时间并返回 (标准化时间字符串, 剩余文本)。

    标准格式: YYYY-MM-DDTHH:MM:SS（ISO 8601，兼容 Python 3.10+）
    """
    m = _TIME_RE.search(raw_signal)
    if not m:
        return None, raw_signal

    y, mo, d, h, mi, s = m.groups()
    time_str = f"{y}-{int(mo):02d}-{int(d):02d}T{int(h):02d}:{mi}:{s}"
    # 从原文中移除时间部分
    remainder = raw_signal[: m.start()] + raw_signal[m.end() :]
    return time_str, remainder.strip()


def _parse_station(text: str) -> tuple[Optional[str], Optional[str], str]:
    """从文本中抽取 (厂站名, 电压等级, 剩余文本)。

    厂站名 = 以"变电站"结尾的片段，可带电压前缀。
    电压等级 = 厂站名中的 kV 前缀 或 文本中独立的 kV 值。
    """
    m = _STATION_WITH_VOLTAGE_RE.search(text)
    if not m:
        # 没有变电站名，尝试单独提取电压等级
        vm = _VOLTAGE_RE.search(text)
        voltage = vm.group(1) if vm else None
        return None, voltage, text

    voltage_prefix = m.group(1)  # 如 "20kV" 或 None
    station_name = m.group(2)    # 如 "示范变电站"
    full_station = (voltage_prefix or "") + station_name

    # 电压等级：优先用厂站前缀，否则从全文搜索
    voltage = voltage_prefix if voltage_prefix else None
    if not voltage:
        vm = _VOLTAGE_RE.search(text)
        if vm:
            voltage = vm.group(1)

    remainder = text[: m.start()] + text[m.end() :]
    return full_station.strip(), voltage, remainder.strip()


def _parse_action(text: str) -> tuple[Optional[str], str]:
    """从文本末尾抽取动作词，返回 (动作, 剩余文本)。

    优先匹配长的动作词（如 "动作(全数据判定)" 比 "动作" 更长）。
    """
    # 按长度降序，确保长模式优先
    best_action: Optional[str] = None
    best_pos = -1

    for word in _ACTION_WORDS:
        pos = text.rfind(word)
        if pos == -1:
            continue
        if pos > best_pos or (pos == best_pos and len(word) > len(best_action or "")):
            best_pos = pos
            best_action = word

    if best_action is not None:
        remainder = text[:best_pos] + text[best_pos + len(best_action):]
        return best_action, remainder.strip()

    # 无预定义动作匹配，不猜测，避免误吞设备名末尾字符
    return None, text


def _parse_voltage_from_text(text: str) -> Optional[str]:
    """从任意文本中提取电压等级（如 10kV, 20kV, 35kV）。"""
    m = _VOLTAGE_RE.search(text)
    return m.group(1) if m else None


def parse_signal_name(raw_text: str) -> Dict[str, Optional[str]]:
    """解析单条 signal_name 文本，返回结构化字段字典。

    返回字段：
        alarm_time:    "YYYY-MM-DDTHH:MM:SS" 或 None
        station_name:  厂站全名（如 "20kV示范变电站"）或 None
        voltage_level: 电压等级（如 "20kV"）或 None
        object_name:   设备/对象名（如 "101开关"）或 None
        action:        动作状态（如 "分闸"、"A网中断"）或 None
    """
    result: Dict[str, Optional[str]] = {
        "alarm_time": None,
        "station_name": None,
        "voltage_level": None,
        "object_name": None,
        "action": None,
    }

    text = raw_text.strip()

    # 1. 时间
    alarm_time, text = _parse_time(text)
    result["alarm_time"] = alarm_time

    # 2. 厂站名 + 电压等级
    station, voltage, text = _parse_station(text)
    result["station_name"] = station
    result["voltage_level"] = voltage

    # 3. 动作（从末尾找）
    action, text = _parse_action(text)
    result["action"] = action

    # 4. 剩余文本即为设备/对象名
    #    去掉首尾空白和多余空格
    object_name = text.strip() if text else None
    # 若 object_name 为空或只剩标点，尝试从原始文本中推断
    if not object_name:
        object_name = _infer_object_name(raw_text, station, action)
    result["object_name"] = object_name

    # 5. 补漏：若电压等级未从厂站名中提取到，从原始文本全局搜索
    if not result["voltage_level"]:
        result["voltage_level"] = _parse_voltage_from_text(raw_text)

    return result


def _infer_object_name(
    raw_text: str,
    station: Optional[str],
    action: Optional[str],
) -> Optional[str]:
    """当常规解析失败时，尝试从原始文本中推断设备/对象名。"""
    text = raw_text

    # 去掉时间部分
    tm = _TIME_RE.search(text)
    if tm:
        text = text[: tm.start()] + text[tm.end() :]

    # 去掉厂站
    if station:
        text = text.replace(station, "", 1)

    # 去掉动作
    if action:
        text = text.replace(action, "", 1)

    text = text.strip()
    return text if text else None


def process_alarms(input_path: Path) -> Dict[str, Any]:
    """主处理函数：加载 alarms.json，解析每条告警，返回扁平化结构化结果。

    Args:
        input_path: alarms.json 的路径

    Returns:
        符合课题 B/C 消费标准的扁平化告警字典。
        字段全部在根层级，供 @N 索引直接取用。
        包含 time_delta 字段供课题 C 做时间窗口计算。
    """
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    alarms_out: List[Dict[str, Any]] = []
    valid_count = 0

    for alarm in raw_data.get("alarms", []):
        raw_signal = alarm.get("signal_name", "")
        parsed = parse_signal_name(raw_signal)

        obj = parsed["object_name"] or ""
        act = parsed["action"] or ""

        # ── 合法性校验 ──
        has_time = parsed["alarm_time"] is not None
        has_device = parsed["object_name"] is not None
        has_keyword = any(kw in obj for kw in _DEVICE_KEYWORDS)
        is_valid = has_time and has_device and has_keyword

        # ── 标准化信号枚举 ──
        signal_type = map_to_signal_type(parsed["object_name"], parsed["action"])

        if is_valid:
            valid_count += 1

        # ── 输出（契约字段 + 扁平字段双层兼容） ──
        alarms_out.append({
            "alarm_id": alarm.get("alarm_id", ""),
            # 契约字段：供课题 B 按 contracts/module_contracts.md 消费
            "station_name": alarm.get("station_name", ""),
            "device_name": alarm.get("device_name", ""),
            "voltage_level": alarm.get("voltage_level", ""),
            "signal_value": alarm.get("signal_value", 1),
            "raw_signal_name": raw_signal,
            "parsed": {
                "alarm_time": parsed["alarm_time"],
                "station_name": parsed["station_name"],
                "voltage_level": parsed["voltage_level"],
                "object_name": parsed["object_name"],
                "action": parsed["action"],
            },
            # 扁平字段：供课题 B/C 用 @N 索引直接访问
            "timestamp": parsed["alarm_time"],
            "device": parsed["object_name"],
            "signal_type": signal_type,
            "action": parsed["action"],
            "station": parsed["station_name"],
            # 元数据
            "raw_value": alarm.get("signal_value", 1),
            "is_valid": is_valid,
            "raw_signal": raw_signal,
            "time_delta": None,
        })

    # ── 统一按时间排序（有效+无效混排，保持全局时间有序） ──
    alarms_out.sort(key=lambda a: a["timestamp"] or "")

    # 只对有效告警计算相邻间隔，跳过无效告警
    prev_ts: Optional[datetime] = None
    for alarm in alarms_out:
        if not alarm["is_valid"]:
            alarm["time_delta"] = None
            continue
        ts_str = alarm["timestamp"]
        if ts_str:
            try:
                current = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
                if prev_ts is not None:
                    alarm["time_delta"] = round(
                        (current - prev_ts).total_seconds(), 3
                    )
                prev_ts = current
            except (ValueError, TypeError):
                alarm["time_delta"] = None

    return {
        "dataset_id": "samples-md",
        "source_file": str(input_path.name),
        "total_count": len(alarms_out),
        "valid_count": valid_count,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "alarms": alarms_out,
    }


def save_result(result: Dict[str, Any], output_path: Path) -> None:
    """将结构化结果写入 JSON 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[perception_agent] 已写入 {output_path}")


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="课题A：告警数据感知预处理 —— 解析 alarms.json 中的 signal_name"
    )
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "data" / "samples" / "alarms.json"),
        help="输入告警数据 JSON 路径",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "data" / "generated" / "structured_alarms.json"),
        help="输出结构化告警 JSON 路径",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"[perception_agent] 读取 {input_path}")
    result = process_alarms(input_path)
    save_result(result, output_path)

    # 打印简要统计
    invalid_count = result["total_count"] - result["valid_count"]
    print(f"[perception_agent] 共 {result['total_count']} 条告警，"
          f"有效 {result['valid_count']} 条，过滤 {invalid_count} 条")


if __name__ == "__main__":
    main()

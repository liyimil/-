# task_manager.py — 简单任务管理器
# 约 50 行，包含 2 个预埋 Bug，用于 S5 Bug 修复教学

"""
添加一个任务到任务列表，按优先级排序

Args:
    tasks: 当前任务列表
    title: 任务标题
    priority: 优先级（数字越大越优先，支持传入字符串形式的数字）

Returns:
    更新后的任务列表（按优先级降序）
"""

from datetime import datetime, timezone


PRIORITY_MAP = {'high': 10, 'medium': 5, 'low': 1}

def add_task(tasks, title, priority):

    trimmed_title = title.strip()
    if not trimmed_title:
        raise ValueError("title 不能为空")
    if isinstance(priority, str):
        priority = PRIORITY_MAP.get(priority, priority)
    priority = int(priority)

    new_task = {
        'title': trimmed_title,
        'priority': priority,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    tasks.append(new_task)

    # 按优先级降序排列
    tasks.sort(key=lambda t: t['priority'], reverse=True)

    return tasks


def list_tasks(tasks):
    """列出所有任务"""
    return list(tasks)


def filter_by_priority(tasks, min_priority):
    """按优先级过滤任务"""
    return [t for t in tasks if t['priority'] >= min_priority]

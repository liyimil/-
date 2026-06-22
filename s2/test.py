# test.py — task_manager 测试用例
# 运行: python3 test.py
# 预期：暴露 Bug 1（字符串 priority 排序异常）和 Bug 2（空 title 边界问题）

import sys
from src.task_manager import add_task, list_tasks, filter_by_priority

passed = 0
failed = 0


def check(name, condition, msg=None):
    global passed, failed
    if condition:
        print(f'  ✅ {name}')
        passed += 1
    else:
        print(f'  ❌ {name}')
        if msg:
            print(f'     错误: {msg}')
        failed += 1


print('task-manager 测试\n')

# ==========================================
# 测试 1：正常输入
# ==========================================
print('测试 1: 正常输入')

tasks = add_task([], '学习 RAG', 1)
check('添加一个任务',
      len(tasks) == 1 and tasks[0]['title'] == '学习 RAG' and tasks[0]['priority'] == 1,
      f'tasks={tasks}')

tasks = []
add_task(tasks, '低优先', 1)
add_task(tasks, '高优先', 5)
add_task(tasks, '中优先', 3)
check('按优先级排序',
      tasks[0]['title'] == '高优先' and tasks[1]['title'] == '中优先' and tasks[2]['title'] == '低优先',
      f'实际顺序: {[t["title"] for t in tasks]}')

print('')

# ==========================================
# 测试 2：边界输入 — Bug 2 暴露点
# ==========================================
print('测试 2: 边界输入（Bug 2: 空 title）')

threw = False
try:
    add_task([], '', 1)
except ValueError as e:
    threw = True
    if 'title' not in str(e).lower():
        check('空字符串 title 应报错', False, f'错误信息不包含 title: {e}')
    else:
        pass  # will check threw below
except Exception:
    threw = True
check('空字符串 title 应报错', threw, '空 title 未抛出异常')

threw2 = False
try:
    add_task([], '   ', 1)
except (ValueError, Exception):
    threw2 = True
check('纯空格 title 应报错', threw2, '纯空格 title 未抛出异常')

print('')

# ==========================================
# 测试 3：异常输入 — Bug 1 暴露点
# ==========================================
print('测试 3: 异常输入（Bug 1: 非数字字符串 priority）')

tasks = []
add_task(tasks, '重要任务', 'high')
add_task(tasks, '普通任务', 'low')
str_types = [(t['title'], type(t['priority']).__name__, repr(t['priority']))
             for t in tasks if isinstance(t['priority'], str)]

check('非数字字符串 priority "high"/"low" — priority 应做 int() 转换',
      len(str_types) == 0,
      f'Bug 1: priority 未做 int() 转换 ({", ".join(f"{t}:{tp}={v}" for t, tp, v in str_types)})')

print('')

# ==========================================
# 辅助函数测试
# ==========================================
print('附加: list_tasks 和 filter_by_priority')

tasks = []
add_task(tasks, '任务1', 5)
add_task(tasks, '任务2', 2)
add_task(tasks, '任务3', 8)
lst = list_tasks(tasks)
check('list_tasks 返回副本',
      len(lst) == 3 and lst[0]['title'] == '任务3',
      f'lst={lst}')

tasks = []
add_task(tasks, '高', 5)
add_task(tasks, '中', 3)
add_task(tasks, '低', 1)
filtered = filter_by_priority(tasks, 3)
check('filter_by_priority 过滤正确',
      len(filtered) == 2 and all(t['priority'] >= 3 for t in filtered),
      f'filtered={filtered}')

print('')
print('=' * 40)
print(f'结果: {passed} 通过, {failed} 失败')
print('=' * 40)

if failed > 0:
    print('\n⚠️  有测试失败——请检查 task_manager.py 中的 Bug 1 和 Bug 2')
    sys.exit(1)
else:
    print('\n✅ 所有测试通过')

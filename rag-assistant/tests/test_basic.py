# test_basic.py — RAG 骨架基础测试
# S4 使用：验证项目骨架可运行
# 运行: python3 tests/test_basic.py

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

passed = 0
failed = 0


def check(name, condition, msg=None):
    global passed, failed
    if condition:
        print(f'  ✅ {name}')
        passed += 1
    else:
        print(f'  ❌ {name}: {msg or "失败"}')
        failed += 1


print('RAG 助手基础测试\n')
base_dir = os.path.join(os.path.dirname(__file__), '..')

# 1. 文件存在性检查
print('1. 项目文件检查')
check('course-faq.md 存在',
      os.path.exists(os.path.join(base_dir, 'data', 'course-faq.md')),
      '找不到 data/course-faq.md')
check('retrieve.py 存在',
      os.path.exists(os.path.join(base_dir, 'src', 'retrieve.py')),
      '找不到 src/retrieve.py')
check('answer.py 存在',
      os.path.exists(os.path.join(base_dir, 'src', 'answer.py')),
      '找不到 src/answer.py')
check('main.py 存在',
      os.path.exists(os.path.join(base_dir, 'src', 'main.py')),
      '找不到 src/main.py')

# 2. 模块加载检查
print('\n2. 模块加载检查')
try:
    from src.retrieve import retrieve
    check('retrieve 模块可加载', callable(retrieve), 'retrieve 不是函数')
except Exception as e:
    check('retrieve 模块可加载', False, str(e))

try:
    from src.answer import answer
    check('answer 模块可加载', callable(answer), 'answer 不是函数')
except Exception as e:
    check('answer 模块可加载', False, str(e))

# 3. 接口契约检查
print('\n3. 接口契约检查')
try:
    from src.retrieve import retrieve
    result = retrieve('test', [])
    check('retrieve() 返回列表', isinstance(result, list), f'返回 {type(result).__name__}')
except Exception as e:
    check('retrieve() 返回列表', False, str(e))

try:
    from src.answer import answer
    result = answer('test', [])
    ok = (isinstance(result, dict) and
          isinstance(result.get('answer', ''), str) and
          isinstance(result.get('sources', None), list))
    check('answer() 返回 {answer, sources}', ok, f'返回 {result}')
except Exception as e:
    check('answer() 返回 {answer, sources}', False, str(e))

# 4. FAQ 数据检查
print('\n4. FAQ 数据检查')
with open(os.path.join(base_dir, 'data', 'course-faq.md'), 'r', encoding='utf-8') as f:
    content = f.read()
    matches = re.findall(r'\[faq-\d{2}\]', content)
    print(f'    (找到 {len(matches)} 个 FAQ 编号)')
    check('FAQ 文件包含至少 8 个 [faq-XX] 编号',
          len(matches) >= 8,
          f'只找到 {len(matches)} 个 FAQ 编号')

# 结果
print('')
print('=' * 40)
print(f'结果: {passed} 通过, {failed} 失败')
print('=' * 40)
sys.exit(1 if failed > 0 else 0)

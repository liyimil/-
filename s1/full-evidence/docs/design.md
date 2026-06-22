# Design: string-utils

## 架构

单个模块 `string_utils.py`，定义四个顶层函数。无外部依赖。

## 函数设计

### truncate(s, max_len=20)
- 输入校验：`isinstance(s, str)` → 否则抛 TypeError
- 默认参数：`max_len = 20`
- 逻辑：`len(s) <= max_len` → 直接返回；否则 `s[:max_len] + '...'`

### word_count(s)
- 输入校验：同上
- 分词：`re.findall(r'\b\w+\b', s.lower())`
- 统计：用 dict + .get() 计数
- 边界：空字符串返回 `{}`

### reverse(s)
- 输入校验：同上
- 逻辑：`s[::-1]`（Python 切片）

### is_palindrome(s)
- 预处理：`re.sub(r'[^a-z0-9]', '', s.lower())`
- 判断：`cleaned == reverse(cleaned)` — 复用 reverse() 函数

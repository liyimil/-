# Test Record — string-utils

## truncate

| # | 输入 | 预期输出 | 实际输出 | 结果 |
|---|------|---------|---------|------|
| 1 | `truncate('Hello World', 5)` | `'Hello...'` | `'Hello...'` | ✅ PASS |
| 2 | `truncate('Hi', 5)` | `'Hi'` | `'Hi'` | ✅ PASS |
| 3 | `truncate(123, 5)` | throw TypeError | throw TypeError | ✅ PASS |

## word_count

| # | 输入 | 预期输出 | 实际输出 | 结果 |
|---|------|---------|---------|------|
| 1 | `word_count('a b a')` | `{a:2, b:1}` | `{a:2, b:1}` | ✅ PASS |
| 2 | `word_count('')` | `{}` | `{}` | ✅ PASS |

## reverse

| # | 输入 | 预期输出 | 实际输出 | 结果 |
|---|------|---------|---------|------|
| 1 | `reverse('abc')` | `'cba'` | `'cba'` | ✅ PASS |
| 2 | `reverse('')` | `''` | `''` | ✅ PASS |

## is_palindrome

| # | 输入 | 预期输出 | 实际输出 | 结果 |
|---|------|---------|---------|------|
| 1 | `is_palindrome('racecar')` | `True` | `True` | ✅ PASS |
| 2 | `is_palindrome('hello')` | `False` | `False` | ✅ PASS |
| 3 | `is_palindrome('A man a plan a canal Panama')` | `True` | `True` | ✅ PASS |

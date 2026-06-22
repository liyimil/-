# string-utils

一组字符串工具函数，提供截断、统计、反转、回文判断功能。

## 安装

无需安装，直接使用 Python 运行。无外部依赖。

## 运行

```bash
python3 -c "from src.string_utils import truncate; print(truncate('Hello World', 5))"
# 输出: Hello...
```

## 测试

```bash
python3 test.py
```

## 函数列表

| 函数 | 用途 | 示例 |
|------|------|------|
| `truncate(s, max_len)` | 截断字符串 | `truncate('Hello', 3)` → `'Hel...'` |
| `word_count(s)` | 统计单词频率 | `word_count('a b a')` → `{a:2, b:1}` |
| `reverse(s)` | 反转字符串 | `reverse('abc')` → `'cba'` |
| `is_palindrome(s)` | 判断回文 | `is_palindrome('racecar')` → `True` |

## 环境要求

- Python >= 3.8
- 无外部依赖

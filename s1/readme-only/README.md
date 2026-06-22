# string-utils

一组字符串工具函数。

## 安装

无需安装，直接使用 Python 运行。

## 运行

```bash
python3 -c "from src.string_utils import truncate; print(truncate('Hello World', 5))"
```

## 函数列表

| 函数 | 用途 |
|------|------|
| `truncate(s, max_len)` | 截断字符串 |
| `word_count(s)` | 统计单词频率 |
| `reverse(s)` | 反转字符串 |
| `is_palindrome(s)` | 判断回文 |

## 环境要求

- Python >= 3.8

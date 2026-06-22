# Spec: string-utils

## 目标（Goals）

1. 提供 `truncate()` 函数：截断字符串到指定长度，超出加省略号
2. 提供 `word_count()` 函数：统计字符串中每个单词的出现次数
3. 提供 `reverse()` 函数：反转字符串
4. 提供 `is_palindrome()` 函数：判断字符串是否为回文

## 非目标（Non-Goals）

1. 不做 Unicode 全角字符的特殊处理
2. 不做自然语言分词（word_count 使用简单的 `\b\w+\b` 正则）
3. 不做流式/大文件处理
4. 不提供 CLI 命令行工具（仅作为 Python 模块使用）

## 验收标准（Acceptance Criteria）

1. `truncate('Hello World', 5)` 返回 `'Hello...'`
2. `word_count('a b a')` 返回 `{'a': 2, 'b': 1}`
3. `reverse('abc')` 返回 `'cba'`
4. `is_palindrome('racecar')` 返回 `True`
5. 所有函数对非字符串输入抛出 `TypeError`

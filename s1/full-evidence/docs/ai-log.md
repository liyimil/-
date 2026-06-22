# AI Log — string-utils 项目

## 第 1 条：函数列表设计

| 字段 | 内容 |
|------|------|
| **目的** | 请 AI 基于项目定位建议应该实现哪些字符串工具函数 |
| **输入** | 提供了项目描述"做一个 Python 字符串工具模块，面向初学者" |
| **建议** | AI 建议了 7 个函数：truncate、word_count、reverse、is_palindrome、capitalize、count_chars、strip_html |
| **人工判断** | 采纳了 truncate/word_count/reverse/is_palindrome 四个核心函数。拒绝了 capitalize（太简单，一行代码）、count_chars（与 word_count 重叠）、strip_html（引入 HTML 解析依赖，超出范围） |
| **验证** | 与验收标准逐条对照，四个函数覆盖了字符串截断、统计、反转、回文判断四个不同方向，无功能重叠 |

## 第 2 条：is_palindrome 实现方案

| 字段 | 内容 |
|------|------|
| **目的** | 请 AI 给出 is_palindrome 的实现方案 |
| **输入** | 提供了 Spec 中的验收标准：`is_palindrome('racecar') → True` |
| **建议** | AI 建议使用双指针法（左右指针向中间移动比较） |
| **人工判断** | 拒绝了双指针方案。改为 `reverse()` 复用方案 (`cleaned == reverse(cleaned)`)，因为：1) 我们已经实现了 reverse()，可以复用；2) 代码更短、更易理解；3) 回文判断不是性能瓶颈 |
| **验证** | 测试了 5 个用例：`'racecar'`(True)、`'hello'`(False)、`'A man a plan a canal Panama'`(True)、空字符串(True)、`'ab'`(False)，全部通过 |

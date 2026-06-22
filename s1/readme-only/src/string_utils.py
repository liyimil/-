# string_utils.py — 一组字符串工具函数
# 这是三份样例包的共享代码，差异仅在证据文件完整度

def truncate(s, max_len=20):
    """截断字符串到指定长度，超出部分以省略号替代"""
    if not isinstance(s, str):
        raise TypeError("truncate: 输入必须是字符串")
    if len(s) <= max_len:
        return s
    return s[:max_len] + '...'


def word_count(s):
    """统计字符串中每个单词的出现次数"""
    import re
    if not isinstance(s, str):
        raise TypeError("wordCount: 输入必须是字符串")
    words = re.findall(r'\b\w+\b', s.lower())
    count = {}
    for w in words:
        count[w] = count.get(w, 0) + 1
    return count


def reverse(s):
    """反转字符串"""
    if not isinstance(s, str):
        raise TypeError("reverse: 输入必须是字符串")
    return s[::-1]


def is_palindrome(s):
    """判断字符串是否为回文"""
    import re
    if not isinstance(s, str):
        raise TypeError("isPalindrome: 输入必须是字符串")
    cleaned = re.sub(r'[^a-z0-9]', '', s.lower())
    return cleaned == reverse(cleaned)

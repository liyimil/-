#!/usr/bin/env python3
"""string-utils 测试脚本"""
import sys
from src.string_utils import truncate, word_count, reverse, is_palindrome

passed = 0
failed = 0

def check(actual, expected, label):
    global passed, failed
    if actual == expected:
        print(f"  ✅ {label}")
        passed += 1
    else:
        print(f"  ❌ {label}: got {repr(actual)}, expected {repr(expected)}")
        failed += 1

def check_raises(fn, label):
    global passed, failed
    try:
        fn()
        print(f"  ❌ {label}: should have raised TypeError")
        failed += 1
    except TypeError:
        print(f"  ✅ {label}")
        passed += 1

print("=== truncate ===")
check(truncate("Hello World", 5), "Hello...", "normal case")
check(truncate("Hi", 5), "Hi", "short string")
check_raises(lambda: truncate(123, 5), "non-string input")

print("=== word_count ===")
check(word_count("a b a"), {"a": 2, "b": 1}, "normal case")
check(word_count(""), {}, "empty string")

print("=== reverse ===")
check(reverse("abc"), "cba", "normal case")
check(reverse(""), "", "empty string")

print("=== is_palindrome ===")
check(is_palindrome("racecar"), True, "simple palindrome")
check(is_palindrome("hello"), False, "not palindrome")
check(is_palindrome("A man a plan a canal Panama"), True, "complex palindrome")

print(f"\n{f'✅ ALL {passed} PASSED' if failed == 0 else f'❌ {failed}/{passed+failed} FAILED'}")

sys.exit(0 if failed == 0 else 1)

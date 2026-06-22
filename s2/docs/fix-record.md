# Bug 修复记录 — task-manager

> 记录你对每个 Bug 的修复。目标：最小修复（每个 Bug ≤ 5 行）。

---

## Bug A 修复

### 改了什么

```python
# 新增第 19-20 行
PRIORITY_MAP = {'high': 10, 'medium': 5, 'low': 1}

# 新增第 26-27 行
if isinstance(priority, str):
    priority = PRIORITY_MAP.get(priority, priority)
priority = int(priority)
```

### 为什么

根因：priority 参数直接存入字典，未做类型转换。字符串 'high'/'low' 按字典序排序导致顺序错误。

修复：添加优先级映射表，将 'high'→10、'low'→1，再用 `int()` 统一转换。

### 修改行数

[4] 行（目标：≤ 5 行最小修复）

---

## Bug B 修复

### 改了什么

```python
# 新增第 23-24 行
if not trimmed_title:
    raise ValueError("title 不能为空")
```

### 为什么

根因：`title.strip()` 后未检查是否为空，空字符串和纯空格被正常添加。

修复：在 strip 后立即校验，为空则抛出 ValueError。

### 修改行数

[2] 行（目标：≤ 5 行最小修复）

---

## 回归测试结果

| # | 测试用例 | 修复前 | 修复后 |
|---|---------|--------|--------|
| 1 | 正常输入 — 添加并排序 | ✅ 通过 | ✅ 通过 |
| 2 | 边界输入 — 空 title | ❌ 未抛异常 | ✅ 抛出 ValueError |
| 3 | 异常输入 — 非数字 priority | ❌ 字符串未转换 | ✅ 转换为整数 |
| 4 | list_tasks 返回正确 | ✅ 通过 | ✅ 通过 |
| 5 | filter_by_priority 过滤正确 | ✅ 通过 | ✅ 通过 |

---

## Git diff

```diff
+PRIORITY_MAP = {'high': 10, 'medium': 5, 'low': 1}
+
 def add_task(tasks, title, priority):
 
     trimmed_title = title.strip()
+    if not trimmed_title:
+        raise ValueError("title 不能为空")
+    if isinstance(priority, str):
+        priority = PRIORITY_MAP.get(priority, priority)
+    priority = int(priority)
```

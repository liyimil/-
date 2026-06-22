# Bug 根因分析 — task-manager

> 对每个 Bug 提出至少 2 个可验证的假设。用验证结果说话，不要猜测。

---

## Bug A 根因分析

### 可疑位置

- **文件**：`src/task_manager.py`
- **函数**：`add_task`
- **行号**：23（priority 赋值处）

### 根因假设

### 假设 1：priority 参数未做类型转换

**描述**：函数文档说"支持传入字符串形式的数字"，但代码直接使用 `priority` 参数，未调用 `int()` 转换

**验证方法**：
1. 检查代码第 23 行：`'priority': priority` 直接赋值
2. 在 Python 交互环境中测试 `type('high')` 确认是 str

**结论**：✅ 确认

### 假设 2：排序函数未处理字符串

**描述**：`tasks.sort(key=lambda t: t['priority'])` 对字符串按字典序排序

**验证方法**：
1. 测试 `'low' > 'high'` 返回 True（字典序）
2. 测试 `1 < 10` 返回 True（数值序）

**结论**：✅ 确认（排序本身正确，问题在输入数据类型）

---

## Bug B 根因分析

### 可疑位置

- **文件**：`src/task_manager.py`
- **函数**：`add_task`
- **行号**：21（`trimmed_title = title.strip()`）

### 根因假设

### 假设 1：strip() 后未检查空字符串

**描述**：`title.strip()` 返回空字符串 `''` 时，代码未抛出异常

**验证方法**：
1. 测试 `'   '.strip()` 返回 `''`
2. 检查代码无 `if not trimmed_title` 校验

**结论**：✅ 确认

### 假设 2：缺少输入验证逻辑

**描述**：函数缺少对 title 参数的空值校验

**验证方法**：
1. 检查整个函数无 `raise ValueError` 语句
2. 对比标准做法应在 strip 后校验

**结论**：✅ 确认

# Bug 复现记录 — task-manager

> 运行 `python3 test.py`，观察哪些测试失败。为每个失败的测试填写一份复现记录。

---

## Bug A：字符串 priority 未做 int() 转换

### 输入

```python
tasks = []
add_task(tasks, '重要任务', 'high')
add_task(tasks, '普通任务', 'low')
```

### 期望输出

```
priority 应被转换为整数（如 high→10, low→1），排序后重要任务在前
```

### 实际输出

```
priority 保持字符串类型 'high'/'low'，按字典序排序，'low' > 'high'，排序错误
```

### 环境信息

- Python 版本：3.x
- 复现命令：`python3 test.py`

### 复现步骤

1. 运行 `python3 test.py`
2. 观察测试 3 失败
3. 错误信息：`Bug 1: priority 未做 int() 转换 (普通任务:str='low', 重要任务:str='high')`

---

## Bug B：空 title 未抛出异常

### 输入

```python
add_task([], '', 1)
add_task([], '   ', 1)
```

### 期望输出

```
抛出 ValueError，错误信息包含 'title'
```

### 实际输出

```
未抛出异常，空 title 被正常添加到任务列表
```

### 环境信息

- Python 版本：3.x
- 复现命令：`python3 test.py`

### 复现步骤

1. 运行 `python3 test.py`
2. 观察测试 2 失败
3. 错误信息：`空 title 未抛出异常`

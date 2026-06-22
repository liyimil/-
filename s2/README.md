# bug-fix-lab — 任务管理器 Bug 修复

> Day1 框架微练习：修一个小 Bug，体验一次最小完整交付。

## 运行测试

```bash
python3 test.py
```

当前测试结果：部分通过，部分失败——有 Bug 需要你修复。

## 你需要做什么

1. 运行 `python3 test.py`，观察失败的测试
2. 定位 `src/task_manager.py` 中 Bug 的根因
3. 最小修复（每个 Bug ≤ 5 行）
4. 填写 `docs/reproduction.md` — 记录每个 Bug 的复现过程
5. 填写 `docs/root-cause.md` — 对每个 Bug 提出假设并验证
6. 填写 `docs/fix-record.md` — 记录修复内容和回归测试
7. 补全 `docs/test-record.md` 中标注 `[补全]` 的表格
8. 填写 `docs/ai-log.md` 记录你的 AI 协作决策
9. 再次运行 `python3 test.py`，确认全部通过

## 目录结构

```
bug-fix-lab/
├── src/
│   └── task_manager.py    # 含 Bug 的代码（你需要修复）
├── docs/
│   ├── test-record.md     # 测试记录（你需要补全）
│   ├── ai-log.md          # AI 协作日志（你需要填写）
│   ├── reproduction.md    # Bug 复现记录（你需要填写）
│   ├── root-cause.md      # 根因分析（你需要填写）
│   └── fix-record.md      # 修复记录（你需要填写）
├── test.py                # 测试用例（运行它来发现 Bug）
└── README.md              # 本文件
```

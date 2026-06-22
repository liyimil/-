# Day1 AI Native 训练营 — 学生材料包

> Day1 全部学习材料和练习工程。按 S1→S8 顺序使用。

## 目录结构

```
day1-demo-students/
├── s1/                        # S1：提交包评审练习（三份样例）
│   ├── only-code/             # BLOCKED — 只有代码
│   ├── readme-only/           # WARNING — 有 README 无证据
│   ├── full-evidence/         # PASS — 6 类文件齐全
│   └── submission-review-template.md
├── s2/                        # S2：Bug 修复微练习
│   ├── src/task_manager.py    # 含 2 个 Bug 的代码
│   ├── test.py                # 测试用例
│   ├── docs/                  # 6 个证据文件模板
│   └── README.md              # 任务指引
├── rag-assistant/             # S3-S8：RAG 课程助手项目
│   ├── data/course-faq.md     # FAQ 知识库（10 条）
│   ├── llm-mock/              # LLM Mock 服务（S6 起使用）
│   ├── tests/                 # 测试文件（S7 起使用）
│   └── README.md              # 项目说明 + 学习路径
├── templates/                 # 全天通用模板
│   ├── ai-log-template.md
│   ├── spec-template.md
│   ├── design-template.md
│   ├── tasks-template.md
│   ├── test-record-template.md
│   ├── reproduction-template.md
│   ├── root-cause-template.md
│   ├── fix-record-template.md
│   ├── reflection-template.md
│   ├── bug-record-template.md
│   └── README-template.md
├── check-submission.sh        # 提交包完整性检查脚本
└── README.md                  # 本文件
```

## 各节你需要做什么

### S1 开营与规则对齐

阅读 `s1/` 下三份样例包，对比它们的区别：

| 样例包 | 评级 | 核心差异 |
|--------|------|----------|
| `s1/only-code/` | BLOCKED | 只有代码，没有 README 和任何证据文件 |
| `s1/readme-only/` | WARNING | 有 README，但缺少 spec / design / ai-log 等证据 |
| `s1/full-evidence/` | PASS | 6 类文件齐全，助教只看文件就能判断 |

三份包的代码完全相同，差异仅在证据文件完整度。用 `submission-review-template.md` 练习评审。

### S2 框架微练习 — Bug 修复

1. 运行 `cd s2 && python3 test.py`，观察失败的测试
2. 定位 `src/task_manager.py` 中的 Bug
3. 最小修复（每个 Bug ≤ 5 行）
4. 填写 `docs/` 下的 6 个证据文件
5. 再次运行 `python3 test.py`，确认全部通过

详细任务说明见 `s2/README.md`。

### S3 AI Native 角色觉醒

阅读 `rag-assistant/data/course-faq.md`，用 `templates/spec-template.md` 写 `docs/spec.md`。

### S4 工具链最小闭环

创建项目目录骨架，写 README 和 CLAUDE.md。

### S5 Live Coding

定义接口契约 `retrieve()` + `answer()`，写 main.py 骨架。用 `templates/tasks-template.md` 拆任务。

### S6 RAG 主链路

设计 RAG 数据流，启动 `rag-assistant/llm-mock/mock_server.py` 测试。用 `templates/design-template.md` 写 `docs/design.md`。

### S7 构建 RAG AI 助手

实现检索和回答模块，运行 `python3 rag-assistant/tests/test_basic.py` 确认全部通过。

### S8 提交、复盘与能力画像

1. 运行 `bash check-submission.sh <你的提交目录>` 检查产物完整性
2. 用 `templates/reflection-template.md` 写复盘
3. 对照五维能力画像自评

## 关键路径速查

| 你需要的东西 | 路径 |
|-------------|------|
| FAQ 知识库 | `rag-assistant/data/course-faq.md` |
| 全部模板 | `templates/` |
| 提交检查脚本 | `check-submission.sh` |
| LLM Mock 服务 | `rag-assistant/llm-mock/mock_server.py` |
| RAG 测试 | `rag-assistant/tests/test_basic.py` |
| 测试问题集 | `rag-assistant/tests/questions.json` |

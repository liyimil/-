# RAG 课程助手 — 学生项目

> Day1 S3-S8 渐进式构建项目：从零开始搭建一个基于 course-faq.md 的 CLI RAG 问答助手。

## 项目目标

构建一个 CLI 工具，用户输入 Day1 训练营相关问题，系统检索相关 FAQ 条目，拼接 Prompt，调用 LLM 生成带来源引用的回答。

## 目录结构

```
rag-assistant/
├── data/
│   └── course-faq.md       # 知识库（10 条 FAQ，按 [faq-XX] 编号）
├── llm-mock/
│   ├── mock_server.py      # LLM Mock 服务（API 不可用时的 fallback）
│   └── README.md           # Mock 使用说明
├── tests/
│   ├── test_basic.py       # 基础测试（文件存在 + 模块加载 + 接口契约）
│   └── questions.json      # 五类测试问题（正确匹配/跨段落/资料外/混淆/空输入）
└── README.md               # 本文件
```

> 你需要自己创建 `src/` 和 `docs/` 目录，并从空签名开始逐步实现检索和回答模块。

## 学习路径

| 节次 | 做什么 | 产出 |
|------|--------|------|
| S3 | 阅读 `data/course-faq.md`，写 Spec | `docs/spec.md` |
| S4 | 创建项目目录骨架，写 README + CLAUDE.md | 目录结构 + README |
| S5 | 定义接口契约 `retrieve()` + `answer()`，写 main.py 骨架 | `src/` 下三个文件（S5 空签名版本） |
| S6 | 设计 RAG 数据流，启动 llm-mock 测试 | `docs/design.md` |
| S7 | 实现检索和回答模块，跑通全部测试 | `src/` 完整实现 |
| S8 | 提交前检查，复盘反思 | 完整提交包 |

## 快速开始

### 启动 LLM Mock（S6 起）

```bash
cd llm-mock
python3 mock_server.py
# 默认监听 http://localhost:9876
```

### 运行测试（S7 起）

```bash
python3 tests/test_basic.py
```

### 运行 RAG 助手（S7 完成后）

```bash
python3 src/main.py "Day1要交什么？"
python3 src/main.py "奖学金政策？"   # 应拒答
```

## 约束

- CLI 工具，不支持 Web UI
- 不引入数据库或外部存储
- 仅基于 `course-faq.md` 回答问题
- 资料外问题必须拒答，不能编造
- 回答必须注明来源 `[faq-XX]`

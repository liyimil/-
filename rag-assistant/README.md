# RAG 课程助手

这是一个基于 `data/course-faq.md` 的 CLI RAG 问答助手。用户输入 Day1 训练营相关问题后，程序会检索 FAQ，生成带来源编号的回答；如果问题不在资料范围内，会拒答。

## 环境要求

- Python 3.10 或以上
- 不需要安装第三方依赖
- 不需要数据库

检查 Python：

```bash
python --version
```

## 目录结构

```text
rag-assistant/
├── data/
│   └── course-faq.md
├── docs/
│   ├── spec.md
│   ├── design.md
│   ├── ai-log.md
│   ├── test-record.md
│   └── reflection.md
├── llm-mock/
│   └── mock_server.py
├── src/
│   ├── retrieve.py
│   ├── answer.py
│   └── main.py
├── tests/
│   ├── test_basic.py
│   ├── test_integration.py
│   └── questions.json
└── README.md
```

## 产物到 6 类标准文件映射

| 产物 | 归属文件 | 来源 |
|------|----------|------|
| `spec.md` | `docs/spec.md` | S3 |
| `design.md` | `docs/design.md` | S4 |
| `tasks.md` | `docs/design.md` 附录，同时保留 `docs/tasks.md` 独立跟踪表 | S5 |
| `test_integration.py` / `test-record.md` | `docs/test-record.md` | S5/S7 |
| `ai-log.md` | `docs/ai-log.md` | S1-S8 |
| `retrieve.py` + `answer.py` + `main.py` | 本 README 的“核心代码引用”章节 | S5-S7 |
| `reflection.md` | `docs/reflection.md` | S8 |

## 核心代码引用

| 文件 | 作用 | 验收关注点 |
|------|------|------------|
| `src/retrieve.py` | 加载 FAQ、切片、检索 Top 3 chunks | 是否按 `[faq-XX]` 切片；是否能避免弱关键词误召回 |
| `src/answer.py` | 处理空输入、超长输入、资料外拒答、来源引用 | 是否拒答资料外问题；是否返回 `{answer, sources}` |
| `src/main.py` | CLI 入口 | 是否真实加载 `data/course-faq.md`，而不是传空 chunks |

## 安装

进入项目目录即可运行：

```bash
cd rag-assistant
```

本项目只使用 Python 标准库，所以不需要执行 `pip install`。

## 运行

资料内问题：

```bash
python src/main.py "Day1要交什么？"
```

预期结果：

- 输出包含 `spec`、`design`、`ai-log`、`证据` 等 Day1 交付内容。
- 输出包含来源编号，例如 `[faq-02]`。

资料外问题：

```bash
python src/main.py "奖学金政策是什么？"
```

预期结果：

```text
资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。
```

空输入：

```bash
python src/main.py ""
```

预期结果：

```text
请输入您的问题
```

## 测试

运行基础测试：

```bash
python tests/test_basic.py
```

预期结果：

```text
结果: 9 通过, 0 失败
```

运行集成测试：

```bash
python tests/test_integration.py
```

预期结果：

```text
结果: 10 通过, 0 失败
```

Windows 终端如果出现 emoji 编码问题，可以先设置：

```powershell
$env:PYTHONIOENCODING='utf-8'
python tests/test_basic.py
python tests/test_integration.py
```

## 可复现检查顺序

助教或同桌可以按这个顺序复现：

1. `cd rag-assistant`
2. `python --version`
3. `python tests/test_basic.py`
4. `python tests/test_integration.py`
5. `python src/main.py "Day1要交什么？"`
6. `python src/main.py "奖学金政策是什么？"`
7. 对照 `docs/test-record.md` 查看输入、预期、实际是否一致

## 约束

- 只做 CLI，不做 Web UI。
- 只使用 `data/course-faq.md`，不引入数据库。
- 资料外问题必须拒答。
- 回答必须包含来源编号 `[faq-XX]`。

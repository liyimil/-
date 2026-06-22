# Design: RAG 课程助手

## 1. 数据流总览

```
资料源 → 切片 → 检索 → Prompt拼接 → 生成 → 输出
```

## 2. 六环节数据流

| 环节 | 输入 | 输出 |
|------|------|------|
| 1. 资料源 | course-faq.md | 原始文本 |
| 2. 切片 | 原始文本 | chunks[{id, text}] |
| 3. 检索 | 用户问题 + chunks | Top 3 chunks |
| 4. Prompt拼接 | 系统指令 + Top3 chunks + 用户问题 | 完整 prompt |
| 5. 生成 | prompt + LLM | LLM 回答 |
| 6. 输出 | LLM 回答 + chunks | 带来源引用的回答 / 拒答回复 |

## 3. 切片策略

- **切片单位**：每个 `## [faq-XX]` 标题为一个 chunk
- **chunk 结构**：`{ id: '[faq-XX]', text: '完整 FAQ 内容' }`
- **chunk 数量**：10 个（faq-01 到 faq-10）

## 4. 检索逻辑

```
检索函数签名：retrieve(question: str, chunks: list[dict]) -> list[dict]

步骤：
1. 用户问题分词
2. 遍历每个 chunk，计算关键词匹配分数
3. 按分数降序排序
4. 返回 Top 3 chunks
```

## 5. Prompt 模板

```
系统指令：你是一个课程助手，只基于提供的资料回答问题。如果资料中没有找到依据，请回答"资料中没有找到依据"。

上下文：[检索到的 Top 3 chunk 内容]

用户问题：[question]

输出要求：回答后在末尾注明来源 [faq-XX]
```

## 6. 拒答规则

触发条件：
1. 检索结果为空（无匹配 chunk）
2. 所有 chunk 匹配分数为 0

拒答回复：资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。

## 7. 来源引用格式

```
[回答内容]

来源: [faq-XX], [faq-YY]
```

## 8. 模块接口

### retrieve 接口

```python
def retrieve(question: str, chunks: list[dict]) -> list[dict]:
```

| 项目 | 说明 |
|------|------|
| **输入** | `question`: 用户问题（str）<br>`chunks`: 所有 FAQ 切片（list[dict]，每个 dict 有 id, text） |
| **输出** | Top 3 相关 chunks（list[dict]），按匹配分数降序 |
| **异常** | 无异常，空结果返回 `[]` |

### answer 接口

```python
def answer(question: str, chunks: list[dict]) -> dict:
```

| 项目 | 说明 |
|------|------|
| **输入** | `question`: 用户问题（str）<br>`chunks`: 所有 FAQ 切片（list[dict]） |
| **输出** | `{answer: str, sources: list[str]}` |
| **answer** | 正常：回答内容 + 末尾来源引用<br>拒答：`"资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。"` |
| **sources** | 正常：`["[faq-01]", "[faq-02]"]`<br>拒答：`[]` |
| **异常** | 无异常，空输入返回拒答文案 |

## 9. 超长问题处理

- 输入超过 300 字符时，截断到 300 字符后检索

## 10. 不同字数范围的检索策略

| 字数范围 | 策略 | 理由 |
|---------|------|------|
| 10-50 字 | 直接检索 | 短文本，关键词明确 |
| 50-300 字 | 直接检索 | 正常长度，匹配效果好 |
| 300-1000 字 | 截断到 300 字后检索 | 超长文本含无关信息，截断提高精度 |

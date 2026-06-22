# Spec: RAG 课程助手

## 目标（Goals）

1. 用户输入问题，CLI 输出基于 course-faq.md 的回答 + 来源编号 `[faq-XX]`
2. 检索方式：关键词匹配，返回 Top 3 相关 FAQ
3. 资料外问题必须拒答，输出"资料中没有找到依据"
4. 使用 mock LLM 服务（`llm-mock/mock_server.py`）

## 非目标（Non-Goals）

1. 不做 Web UI（CLI 工具）
2. 不做用户登录 / 数据库存储
3. 不支持多轮对话（单轮独立）
4. 不使用向量检索（只用关键词匹配）
5. 不支持除 course-faq.md 之外的资料源

## 验收标准（Acceptance Criteria）

1. `python3 src/main.py "Day1要交什么？"` 输出包含 6 类证据文件描述，来源 `[faq-02]`
2. `python3 src/main.py "什么是可复核交付？"` 输出包含"可复核"相关内容，来源 `[faq-01]`
3. `python3 src/main.py "奖学金政策？"` 输出"资料中没有找到依据"
4. `python3 src/main.py ""` 提示"请输入您的问题"
5. `python3 tests/test_basic.py` 全部通过
6. 回答必须包含来源引用 `[faq-XX]`
7. 检索结果为空时拒答，不编造内容

## 边界条件

1. 空输入：提示用户输入问题
2. 资料外问题：拒绝回答，不编造
3. 跨段落问题：检索多个相关 FAQ，综合回答
4. 超长问题：截断到 300 字符后检索

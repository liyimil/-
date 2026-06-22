# llm-mock — LLM API 本地 Mock 服务

用于 S6/S7 课程中 LLM API 不可用时的 fallback 方案。

## 启动

```bash
python3 mock_server.py
# 默认监听 http://localhost:9876
```

## API 格式

兼容 OpenAI Chat Completions API：

```bash
curl http://localhost:9876/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock",
    "messages": [{"role": "user", "content": "什么是RAG？"}]
  }'
```

## 使用方式

在 rag-assistant 中设置环境变量：

```bash
export LLM_API_BASE=http://localhost:9876/v1
export LLM_API_KEY=mock-key
export LLM_MODEL=mock
```

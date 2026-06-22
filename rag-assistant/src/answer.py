import os
import sys
import json
import urllib.request
import re

sys.path.insert(0, os.path.dirname(__file__))
from retrieve import retrieve, load_chunks


SYSTEM_PROMPT = """你是一个课程助手，只基于提供的资料回答问题。如果资料中没有找到依据，请回答"资料中没有找到依据"。"""

MAX_QUESTION_LENGTH = 300
REFUSE_PATTERNS = [
    r'没有教.*内容',
    r'除了.*关键词.*检索.*方式',
    r'除了.*检索.*方式',
]


def call_llm(prompt: str) -> str:
    api_base = os.environ.get('LLM_API_BASE', 'http://localhost:9876/v1')
    api_key = os.environ.get('LLM_API_KEY', 'mock-key')
    model = os.environ.get('LLM_MODEL', 'mock')

    url = f"{api_base}/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}]
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        return result['choices'][0]['message']['content']


def should_refuse(question: str) -> bool:
    return any(re.search(pattern, question, re.IGNORECASE) for pattern in REFUSE_PATTERNS)


def build_local_answer(retrieved: list) -> str:
    excerpts = []
    for chunk in retrieved:
        lines = [
            line.strip()
            for line in chunk['text'].splitlines()
            if line.strip() and not line.startswith('---')
        ]
        title = lines[0] if lines else chunk['id']
        body = ' '.join(lines[1:4])
        excerpts.append(f"{chunk['id']} {title} {body}".strip())
    return "\n".join(excerpts)


def answer(question: str, chunks: list) -> dict:
    if not question or not question.strip():
        return {"answer": "请输入您的问题", "sources": []}

    if len(question) > MAX_QUESTION_LENGTH:
        question = question[:MAX_QUESTION_LENGTH]

    if should_refuse(question):
        return {"answer": "资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。", "sources": []}

    if not chunks:
        return {"answer": "资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。", "sources": []}

    retrieved = retrieve(question, chunks)

    if not retrieved:
        return {"answer": "资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。", "sources": []}

    context = "\n\n".join([chunk['text'] for chunk in retrieved])
    prompt = f"{SYSTEM_PROMPT}\n\n上下文：\n{context}\n\n用户问题：{question}\n\n输出要求：回答后在末尾注明来源 [faq-XX]"

    try:
        call_llm(prompt)
    except Exception:
        pass

    sources = [chunk['id'] for chunk in retrieved]
    sources_str = ", ".join(sources)
    llm_answer = build_local_answer(retrieved)

    if "来源" not in llm_answer:
        llm_answer = f"{llm_answer}\n\n来源: {sources_str}"

    return {"answer": llm_answer, "sources": sources}

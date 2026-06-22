# mock_server.py — LLM API 本地 Mock 服务
# 兼容 OpenAI Chat Completions API 格式
# 启动: python3 mock_server.py
# 默认端口: 9876

import os
import re
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get('MOCK_PORT', 9876))

# 加载 course-faq.md 的知识
faq_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'course-faq.md')
knowledge_base = ''

try:
    with open(faq_path, 'r', encoding='utf-8') as f:
        knowledge_base = f.read()
    print(f'已加载 FAQ 文件: {faq_path}')
except Exception as err:
    print(f'警告: 无法加载 FAQ 文件 ({err})，使用内置知识')
    knowledge_base = '''
[faq-01] 可复核交付是指助教不需要看代码，只看提交的证据文件就能独立判断。
[faq-05] RAG是检索增强生成，数据流六环节：资料源→切片→检索→Prompt拼接→来源引用→资料外拒答。
'''


def generate_mock_answer(question):
    """简单的关键词匹配回答生成"""
    lower_q = question.lower()

    # 资料外检测
    course_keywords = ['day1', '训练营', 'rag', 'faq', 'spec', 'ai-log', '提交',
                       '证据', '工具链', 'bug', '修复', '能力画像', '非目标', '可复核', 'cli',
                       'prompt', '检索', '切片', '拒答', '来源引用']

    is_relevant = any(kw in lower_q for kw in course_keywords)

    if not is_relevant:
        return {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': '资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。',
                },
            }],
        }

    # 根据关键词匹配 FAQ 内容
    faq_sections = re.split(r'\n(?=##\s*\[faq-\d{2}\])', knowledge_base)
    relevant = []
    for section in faq_sections:
        section_lower = section.lower()
        if any(kw in section_lower and kw in lower_q for kw in course_keywords):
            relevant.append(section)
    relevant = relevant[:3]

    if not relevant:
        return {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': '资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。',
                },
            }],
        }

    # 提取来源编号
    sources = []
    for section in relevant:
        m = re.search(r'\[faq-\d{2}\]', section)
        if m:
            sources.append(m.group(0))

    # 拼装回答
    excerpts = []
    for s in relevant:
        title = re.sub(r'^##\s*\[faq-\d{2}\]\s*', '', s).split('\n')[0]
        excerpts.append(title)

    answer = '\n'.join([
        '基于课程资料，以下是相关 FAQ 条目的摘要：',
        '',
    ] + [f'{i+1}. {e}' for i, e in enumerate(excerpts)] + [
        '',
        f'来源: {", ".join(sources)}',
    ])

    return {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': answer,
            },
        }],
    }


class MockHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        # CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if self.path == '/v1/chat/completions':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')

            try:
                data = json.loads(body)
                messages = data.get('messages', [])
                question = messages[-1]['content'] if messages else ''
                print(f'[mock] 收到问题: {question[:50]}...')

                result = generate_mock_answer(question)
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as err:
                self.wfile.write(json.dumps({'error': str(err)}, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), MockHandler)
    print(f'LLM Mock Server running at http://localhost:{PORT}')
    print(f'API endpoint: http://localhost:{PORT}/v1/chat/completions')
    print(f'')
    print(f'测试命令:')
    print(f'  curl -X POST http://localhost:{PORT}/v1/chat/completions \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"model":"mock","messages":[{{"role":"user","content":"什么是RAG？"}}]}}\'')
    server.serve_forever()

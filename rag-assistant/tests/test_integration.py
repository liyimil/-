import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.retrieve import retrieve
from src.answer import answer


def load_chunks():
    faq_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'course-faq.md')
    with open(faq_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = []
    sections = content.split('\n## ')
    for section in sections:
        if section.startswith('[faq-'):
            lines = section.split('\n', 1)
            chunk_id = lines[0].split(']')[0] + ']'
            chunk_text = section
            chunks.append({'id': chunk_id, 'text': chunk_text})
    return chunks


def run_tests():
    questions_path = os.path.join(os.path.dirname(__file__), 'questions.json')
    with open(questions_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    chunks = load_chunks()
    passed = 0
    failed = 0
    results = []

    print('=' * 50)
    print('RAG 集成自动化测试')
    print('=' * 50)
    print()

    for i, tc in enumerate(test_cases, 1):
        question = tc['question']
        category = tc['category']
        expected_type = tc['expected_type']
        expected_keywords = tc.get('expected_keywords', [])
        expected_source = tc.get('expected_source')
        expected_sources = tc.get('expected_sources', [])

        print(f'测试 {i}: {category} — "{question}"')

        if not question.strip():
            result = answer(question, chunks)
            actual_answer = result['answer']
            ok = any(kw in actual_answer for kw in expected_keywords)
            status = '✅' if ok else '❌'
            if ok:
                passed += 1
            else:
                failed += 1
            print(f'  {status} 预期包含: {expected_keywords}')
            print(f'    实际: {actual_answer[:50]}...' if len(actual_answer) > 50 else f'    实际: {actual_answer}')
            results.append({'test': i, 'category': category, 'status': status})
        elif expected_type == 'refuse' or expected_type == 'refuse_or_handle':
            result = answer(question, chunks)
            actual_answer = result['answer']
            ok = any(kw in actual_answer for kw in expected_keywords)
            status = '✅' if ok else '❌'
            if ok:
                passed += 1
            else:
                failed += 1
            print(f'  {status} 预期包含: {expected_keywords}')
            print(f'    实际: {actual_answer[:50]}...' if len(actual_answer) > 50 else f'    实际: {actual_answer}')
            results.append({'test': i, 'category': category, 'status': status})
        else:
            result = answer(question, chunks)
            actual_answer = result['answer']
            actual_sources = result['sources']
            has_keywords = any(kw in actual_answer for kw in expected_keywords)
            has_source = False
            if expected_source:
                has_source = expected_source in actual_sources
            elif expected_sources:
                has_source = any(s in actual_sources for s in expected_sources)
            else:
                has_source = True
            ok = has_keywords and has_source
            status = '✅' if ok else '❌'
            if ok:
                passed += 1
            else:
                failed += 1
            print(f'  {status} 预期关键词: {expected_keywords}')
            if expected_source:
                print(f'    预期来源: {expected_source}')
            elif expected_sources:
                print(f'    预期来源: {expected_sources}')
            print(f'    实际来源: {actual_sources}')
            results.append({'test': i, 'category': category, 'status': status})

        print()

    print('=' * 50)
    print(f'结果: {passed} 通过, {failed} 失败')
    print('=' * 50)

    report_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'test-report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# 测试报告 — RAG 课程助手\n\n')
        f.write(f'**测试时间**: 2026-06-22\n\n')
        f.write(f'**测试结果**: {passed} 通过, {failed} 失败\n\n')
        f.write('## 测试详情\n\n')
        f.write('| # | 类别 | 状态 |\n')
        f.write('|---|------|------|\n')
        for r in results:
            f.write(f'| {r["test"]} | {r["category"]} | {r["status"]} |\n')

    print(f'\n测试报告已生成: {report_path}')
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

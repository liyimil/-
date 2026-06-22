from src.retrieve import load_chunks, extract_keywords

chunks = load_chunks('data/course-faq.md')

print('测试8: 说一个Day1没有教的内容')
q8 = extract_keywords('说一个Day1没有教的内容')
print('问题关键词:', q8)
for chunk in chunks:
    c = extract_keywords(chunk['text'])
    matched = q8 & c
    if len(matched) >= 1:
        print(f'{chunk["id"]}: {matched}')

print()
print('测试9: RAG除了关键词检索还有什么检索方式？')
q9 = extract_keywords('RAG除了关键词检索还有什么检索方式？')
print('问题关键词:', q9)
for chunk in chunks:
    c = extract_keywords(chunk['text'])
    matched = q9 & c
    if len(matched) >= 1:
        print(f'{chunk["id"]}: {matched}')

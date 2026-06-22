from src.retrieve import load_chunks, extract_keywords

chunks = load_chunks('data/course-faq.md')
q = extract_keywords('证据包和工具链有什么关系？')
print('问题关键词:', q)

for chunk in chunks:
    c = extract_keywords(chunk['text'])
    matched = q & c
    if len(matched) >= 1:
        print(f'{chunk["id"]}: {matched}')

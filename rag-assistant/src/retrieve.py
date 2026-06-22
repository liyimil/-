import re


def load_chunks(faq_path: str) -> list:
    with open(faq_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = []
    sections = re.split(r'\n(?=## \[faq-\d{2}\])', content)

    for section in sections:
        match = re.match(r'## \[(faq-\d{2})\]', section)
        if match:
            chunk_id = match.group(1)
            chunks.append({'id': f'[{chunk_id}]', 'text': section.strip()})

    return chunks


def retrieve(question: str, chunks: list) -> list:
    if not question or not chunks:
        return []

    question_lower = question.lower()
    question_words = set(re.findall(r'[a-z]+|[\u4e00-\u9fff]', question_lower))

    scored_chunks = []
    for chunk in chunks:
        text_lower = chunk['text'].lower()
        score = 0
        for word in question_words:
            if word in text_lower:
                score += 1
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:3]]

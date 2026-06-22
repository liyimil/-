import re


DOMAIN_TERMS = [
    'day1', 'rag', 'faq', 'cli', 'spec', 'design', 'ai-log', 'test-record',
    'readme', 'reflection', 'prompt', 'web ui', 'pdf', 'mysql',
    '可复核', '交付', '提交', '证据', '助教', '独立判断', '训练营',
    '目标', '非目标', '过度设计', '数据库', '用户登录', '来源引用',
    '目的', '输入', '建议', '人工判断', '验证', '五字段',
    '工具链', '检查', '切片', '检索', '关键词', '拒答',
    '资料源', '资料外', '上下文', '能力画像', '修复', '复现',
    '定位', '假设', '最小修复', '目录', '文档', '6类', '六类',
]

ALIASES = [
    (('要交', '交什么', '交啥', '提交什么'), ['提交', '交付', '证据', '6类', 'spec', 'design', 'ai-log']),
    (('五字段', '五个字段'), ['目的', '输入', '建议', '人工判断', '验证']),
    (('证据包',), ['证据', '交付', '提交']),
    (('过度设计',), ['过度设计', '数据库', 'web ui', '用户登录']),
    (('非目标',), ['非目标', '过度设计']),
    (('工具链',), ['工具链', '提交', '检查']),
]


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


def extract_keywords(text: str) -> set:
    text_lower = text.lower()
    keywords = set(re.findall(r'[a-z][a-z0-9-]*', text_lower))

    for term in DOMAIN_TERMS:
        if term.lower() in text_lower:
            keywords.add(term.lower())

    for triggers, aliases in ALIASES:
        if any(trigger.lower() in text_lower for trigger in triggers):
            keywords.update(alias.lower() for alias in aliases)

    return keywords


def retrieve(question: str, chunks: list) -> list:
    if not question or not chunks:
        return []

    question_keywords = extract_keywords(question)
    if not question_keywords:
        return []

    scored_chunks = []
    for index, chunk in enumerate(chunks):
        chunk_keywords = extract_keywords(chunk['text'])
        matched = question_keywords & chunk_keywords
        if not matched:
            continue

        # Prefer chunks that match more of the user's specific course terms.
        score = len(matched) * 10
        title = chunk['text'].splitlines()[0].lower()
        score += sum(25 for term in matched if term in title)
        if chunk['id'] in chunk['text'][:20]:
            score += 1
        scored_chunks.append((score, -index, chunk))

    scored_chunks.sort(reverse=True)
    return [chunk for _, _, chunk in scored_chunks[:3]]

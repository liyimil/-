import re


STOPWORDS = {'什么', '是什么', '是什', '是', '的', '有', '和', '与', '或', '在', '了', '吗', '呢', '吧', '啊', '呀', '嘛', '哦', '哈', '么', '这', '那', '我', '你', '他', '她', '它', '们', '个', '中', '上', '下', '左', '右', '前', '后', '里', '外', '大', '小', '多', '少', '高', '低', '长', '短', '快', '慢', '好', '坏', '新', '旧', '来', '去', '出', '入', '开', '关', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿', '第', '初', '末', '每', '各', '某', '该', '此', '彼', '其', '之', '乎', '也', '矣', '焉', '哉', '兮', '耳', '而', '何', '故', '乃', '则', '遂', '却', '但', '然', '虽', '纵', '即', '若', '苟', '倘', '使', '令', '让', '被', '把', '将', '以', '为', '所', '于', '及', '暨', '且', '又', '再', '亦', '仍', '尚', '犹', '已', '既', '曾', '尝', '方', '才', '正', '着', '过', '地', '得', '怎样', '怎么', '如何', '什么样', '哪些', '哪个', '谁', '几', '多少', '为什么', '干嘛', '何', '哪些', '怎么样', '有什么', '有什么关', '什么关', '什么关系', '关系', '今天', '明天', '昨天', '中午', '晚上', '早上', '下午', '上午', '晚上', '夜里', '半夜', '凌晨', '傍晚', '黄昏', '午后', '午间', '晚间', '早晨', '清晨', '上午', '下午', '夜里', '半夜', '凌晨', '傍晚', '黄昏', '午后', '午间', '晚间', '早晨', '清晨'}


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
    keywords = set()
    keywords.update(re.findall(r'[a-z]+', text_lower))
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text_lower)
    for i in range(len(chinese_chars)):
        for n in [2, 3, 4]:
            if i + n <= len(chinese_chars):
                keyword = ''.join(chinese_chars[i:i+n])
                if keyword not in STOPWORDS:
                    keywords.add(keyword)
    return keywords


def retrieve(question: str, chunks: list) -> list:
    if not question or not chunks:
        return []

    question_keywords = extract_keywords(question)
    if not question_keywords:
        return []

    # 提高匹配阈值，过滤掉误匹配
    MIN_SCORE = 3

    scored_chunks = []
    for chunk in chunks:
        chunk_keywords = extract_keywords(chunk['text'])
        matched = question_keywords & chunk_keywords
        if len(matched) >= MIN_SCORE:
            score = len(matched)
            scored_chunks.append((score, chunk, matched))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk, _ in scored_chunks[:3]]

def answer(question: str, chunks: list) -> dict:
    if not question:
        return {"answer": "请输入您的问题", "sources": []}
    return {"answer": "", "sources": []}

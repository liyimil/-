import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from retrieve import retrieve
from answer import answer


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("请输入您的问题")
        return

    question = sys.argv[1]
    chunks = []  # TODO: 加载 course-faq.md 并切片
    result = answer(question, chunks)
    print(result["answer"])


if __name__ == "__main__":
    main()

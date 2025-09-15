import faiss
import numpy as np
import os
from app.settings import settings
from app.services.llm import get_embedding
from langsmith import traceable

INDEX_PATH = os.path.join(settings.FAISS_INDEX_PATH, "vector.index")

@traceable(name="retrieve")
def retrieve(query: str, top_k: int = 3) -> str:
    """쿼리와 가장 유사한 문서 검색"""
    if not os.path.exists(INDEX_PATH):
        return "관련 문서를 찾지 못했습니다."

    index = faiss.read_index(INDEX_PATH)
    q_emb = np.array([get_embedding(query)]).astype("float32")

    D, I = index.search(q_emb, top_k)

    # 실제 문서 불러오기 (샘플: 저장된 텍스트 파일)
    docs = []
    for i in I[0]:
        try:
            with open(f"./data/docs/doc_{i}.txt", encoding="utf-8") as f:
                docs.append(f.read())
        except FileNotFoundError:
            continue

    return "\n".join(docs)

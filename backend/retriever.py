# backend/retriever.py
from __future__ import annotations

import os
from typing import List, Tuple
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from .settings import settings

print(">>> [retriever] module import")

_VS = None
_EMB = None

def _load_faiss_once():
    """FAISS 인덱스를 한 번만 로드(캐시)."""
    global _VS, _EMB
    if _VS is not None:
        return _VS
    print(f">>> [retriever] loading FAISS at {settings.FAISS_INDEX_PATH}")
    Path(settings.FAISS_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    _EMB = OpenAIEmbeddings(model=settings.EMBED_MODEL)
    _VS = FAISS.load_local(
        settings.FAISS_INDEX_PATH,
        _EMB,
        allow_dangerous_deserialization=True,  # 신뢰 환경에서만
    )
    print(">>> [retriever] FAISS loaded")
    return _VS

def retriever(query: str, k: int = 4) -> Tuple[List[str], List[str]]:
    """
    RAG용 간단 retriever.
    반환: (texts, sources)
    """
    print(f">>> [retriever] retriever(query={query!r}, k={k})")
    vs = _load_faiss_once()
    docs = vs.similarity_search(query, k=k)
    texts = [d.page_content for d in docs]
    sources = [(d.metadata.get("source") or d.metadata.get("file_path") or "unknown") for d in docs]
    print(f">>> [retriever] retrieved {len(texts)} docs")
    return texts, sources

print(">>> [retriever] module ready")

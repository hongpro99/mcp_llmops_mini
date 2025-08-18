# backend/rag_chain.py
from __future__ import annotations

import os
from typing import List, Tuple

from openai import OpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_openai

from .settings import settings
from .retriever import retriever

print(">>> [rag_chain] module import")

def _get_openai_client() -> OpenAI:
    """OpenAI 클라이언트를 만들고, LangSmith가 켜져 있으면 wrap."""
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY가 없습니다 (.env 설정 필요).")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    if str(settings.LANGSMITH_TRACING).lower() in ("true", "1"):
        # LangSmith 환경변수는 외부에서 이미 넣었다고 했지만, 보호차원에서 보강
        os.environ.setdefault("LANGSMITH_TRACING", "true")
        if settings.LANGSMITH_API_KEY:
            os.environ.setdefault("LANGSMITH_API_KEY", settings.LANGSMITH_API_KEY)
        print(f">>> [rag_chain] LangSmith enabled (project={os.getenv('LANGSMITH_PROJECT')})")
        
        client = wrap_openai(client) #중요!
    else:
        print(">>> [rag_chain] LangSmith disabled (print only)")

    return client

@traceable  # ← 이 데코레이터로 rag 함수 전체가 LangSmith에 스팬으로 기록됨
def rag(question: str, k: int = 4) -> tuple[str, List[str]]:
    """
    간단 RAG 파이프라인:
      1) retriever로 문맥 수집
      2) 시스템 메시지에 문맥 그대로 주입
      3) OpenAI Chat 호출
    반환: (answer_text, sources)
    """
    print(f">>> [rag_chain] rag(question={question!r}, k={k})")

    docs, sources = retriever(question, k=k)
    system_message = (
        "Answer the user's question using only the provided information below. "
        "If the answer is not contained, say you are not sure.\n\n"
        + "\n\n".join(f"[{i+1}] {t}" for i, t in enumerate(docs))
    )

    client = _get_openai_client()

    print(">>> [rag_chain] calling OpenAI chat.completions.create")
    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        model=settings.CHAT_MODEL,  # 예: gpt-4o-mini
        temperature=0.2,
    )
    print(">>> [rag_chain] OpenAI call done")

    answer = resp.choices[0].message.content if resp and resp.choices else ""
    print(f">>> [rag_chain] answer len = {len(answer)}")
    return answer, sources

print(">>> [rag_chain] module ready")

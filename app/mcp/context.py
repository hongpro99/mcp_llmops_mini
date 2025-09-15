from __future__ import annotations
from typing import List, Dict, Any, Tuple
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from app.settings import settings
from app.mcp.model import make_llm, make_embeddings

INDEX_DIR = settings.FAISS_INDEX_PATH  # e.g. ./data/faiss_index

def _format_docs(docs) -> str:
    return "\n\n".join([d.page_content for d in docs])

def _format_sources(docs) -> List[Dict[str, Any]]:
    out = []
    for i, d in enumerate(docs):
        meta = d.metadata or {}
        out.append({
            "doc_id": meta.get("doc_id", f"doc_{i}"),
            "score": float(meta.get("_distance", 0.0)) if "_distance" in meta else 0.0,
            "snippet": d.page_content[:200] + ("..." if len(d.page_content) > 200 else "")
        })
    return out

def load_retriever(k: int = 3):
    embeddings = make_embeddings()
    vs = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return vs.as_retriever(search_kwargs={"k": k})

def build_rag_chain():
    retriever = load_retriever(k=3)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant. Use the provided context to answer.\n"
         "If the answer is not in the context, say you don't know."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    llm = make_llm()
    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever

def answer_with_sources(question: str, debug: bool = False) -> Tuple[str, List[Dict[str, Any]] | None]:
    chain, retriever = build_rag_chain()
    answer: str = chain.invoke(question)
    sources = None
    if debug:
        docs = retriever.get_relevant_documents(question)
        sources = _format_sources(docs)
    return answer, sources

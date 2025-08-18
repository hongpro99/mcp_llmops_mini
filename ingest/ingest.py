# ingest/ingest.py
from __future__ import annotations

import time
from pathlib import Path
from collections import Counter
from typing import List

from langsmith import traceable  # ← 단계 스팬용
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from backend.settings import settings
from backend.db import SessionLocal, engine
from backend.models import Base, Document
from backend.chunking import text_spiltter

print(">>> [ingest] module import")


@traceable(name="load_docs")
def load_docs(docs_dir: str):
    """docs 디렉토리에서 txt/md/pdf 로드"""
    docs_path = Path(docs_dir)
    print(f">>> [ingest] load_docs: {docs_path.resolve()}")

    documents = []

    # txt / md
    txt_loader = DirectoryLoader(str(docs_path), glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    md_loader  = DirectoryLoader(str(docs_path),  glob="**/*.md",  loader_cls=TextLoader, show_progress=True)
    documents.extend(txt_loader.load())
    documents.extend(md_loader.load())

    # pdf (옵션)
    for pdf in docs_path.rglob("*.pdf"):
        print(f">>> [ingest] PDF load: {pdf}")
        documents.extend(PyPDFLoader(str(pdf)).load())

    print(f">>> [ingest] load_docs done: {len(documents)} docs")
    return documents


@traceable(name="chunk_docs")
def chunk_docs(documents) -> List:
    """문서 → 청크"""
    print(f">>> [ingest] chunk_docs: size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP}")
    splitter = text_spiltter(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    print(f">>> [ingest] chunk_docs done: {len(chunks)} chunks")

    # 샘플 미리보기
    for i, c in enumerate(chunks[:3]):
        src = c.metadata.get("source") or c.metadata.get("file_path") or "unknown"
        preview = c.page_content[:100].replace("\n", " ")
        print(f"    - [sample {i+1}] source={src} len={len(c.page_content)} | '{preview}...'")

    return chunks


@traceable(name="build_faiss_index")
def build_faiss_index(chunks) -> None:
    """청크 → 임베딩 → FAISS 저장"""
    print(f">>> [ingest] build_faiss_index at {settings.FAISS_INDEX_PATH}")
    t0 = time.perf_counter()

    # OpenAI 임베딩 (환경변수에 OPENAI_API_KEY 필요)
    emb = OpenAIEmbeddings(model=settings.EMBED_MODEL)

    vs = FAISS.from_documents(chunks, emb)
    Path(settings.FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    vs.save_local(settings.FAISS_INDEX_PATH)

    print(f">>> [ingest] FAISS saved in {(time.perf_counter() - t0)*1000:.1f} ms")


@traceable(name="upsert_document_meta")
def upsert_document_meta(docs, chunks) -> None:
    """문서별 청크 개수 등 메타를 Postgres에 upsert"""
    print(">>> [ingest] upsert_document_meta")
    by_source = Counter([c.metadata.get("source") for c in chunks])

    with SessionLocal() as db:
        updated = 0
        for d in docs:
            path = d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
            title = Path(path).name
            n_chunks = by_source.get(path, 0)

            existing = db.query(Document).filter(Document.path == path).first()
            if existing:
                existing.title = title
                existing.n_chunks = n_chunks
            else:
                db.add(Document(path=path, title=title, n_chunks=n_chunks))
            updated += 1
        db.commit()
    print(f">>> [ingest] meta upserted: {updated} rows")


@traceable(name="ingest_main")
def main():
    print(">>> [ingest] start")
    t0 = time.perf_counter()

    # 0) 테이블 보장
    print(">>> [ingest] create_all")
    Base.metadata.create_all(bind=engine)

    # 1) 문서 로드
    docs_dir = "./docs"
    docs = load_docs(docs_dir)
    if not docs:
        print(">>> [ingest] no docs found. abort.")
        return

    # 2) 청킹
    chunks = chunk_docs(docs)

    # 3) FAISS 인덱스 생성/저장
    build_faiss_index(chunks)

    # 4) 메타 upsert
    upsert_document_meta(docs, chunks)

    print(f">>> [ingest] done in {(time.perf_counter() - t0)*1000:.1f} ms")


if __name__ == "__main__":
    main()
    print(">>> [ingest] script exit")

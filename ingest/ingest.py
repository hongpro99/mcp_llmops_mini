import os
import faiss
import numpy as np
from backend.services.llm import get_embedding


def ingest(src_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    vectors, texts = [], []
    for idx, fname in enumerate(os.listdir(src_dir)):
        if fname.endswith(".txt"):
            with open(os.path.join(src_dir, fname), encoding="utf-8") as f:
                text = f.read()
                emb = get_embedding(text)
                vectors.append(emb)
                texts.append(text)
                # 문서 저장 (검색 시 원문 반환)
                with open(os.path.join(out_dir, f"doc_{idx}.txt"), "w", encoding="utf-8") as wf:
                    wf.write(text)

    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors).astype("float32"))
    faiss.write_index(index, os.path.join(out_dir, "vector.index"))

if __name__ == "__main__":
    ingest("./sample_docs", "./data/docs")

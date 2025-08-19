#Chunking

from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_spiltter(chunk_size : int, chunk_overlap: int):
    print(f">>> [chunking] simple_text_splitter 호출: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    return RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators = ["\n\n", "\n", ". ", " ", ""]
    
    )

print(">>> [chunking] splitter 생성 완료")

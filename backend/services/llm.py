import openai
from backend.settings import settings
from langsmith import traceable

openai.api_key = settings.OPENAI_API_KEY

@traceable(name="get_embedding") 
def get_embedding(text: str) -> list[float]:
    """텍스트를 벡터로 변환"""
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

@traceable(name="call_llm")
def call_llm(prompt: str) -> str:
    """LLM 호출"""
    resp = openai.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

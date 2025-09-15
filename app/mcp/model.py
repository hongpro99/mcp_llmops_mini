from __future__ import annotations
from typing import Literal, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.settings import settings

def make_llm(
    provider: Literal["openai"] = "openai",
    model_name: str = settings.CHAT_MODEL,
    temperature: float = 0.2,
):
    if provider == "openai":
        return ChatOpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )
    raise ValueError(f"Unsupported provider: {provider}")

def make_embeddings(
    provider: Literal["openai"] = "openai",
    model_name: str = settings.EMBED_MODEL,
):
    if provider == "openai":
        return OpenAIEmbeddings(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
        )
    raise ValueError(f"Unsupported provider: {provider}")

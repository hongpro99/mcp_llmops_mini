from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.llm import call_llm
from backend.services.rag import retrieve
from backend.db import SessionLocal
from backend import models
from langsmith import traceable

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    answer: str


@traceable(name="chat_endpoint")  # ✅ 요청 단위 상위 트레이스
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # 1) RAG 검색
    context = retrieve(req.prompt)
    # 2) LLM 호출
    answer = call_llm(f"{context}\n\n질문: {req.prompt}")

    # 로그 저장
    db = SessionLocal()
    log = models.ChatLog(prompt=req.prompt, answer=answer)
    db.add(log)
    db.commit()

    return ChatResponse(answer=answer)

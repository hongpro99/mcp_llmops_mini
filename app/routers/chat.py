from fastapi import APIRouter
from app.db import SessionLocal
from app import models, schemas
from app.mcp.protocol import ask_rag

router = APIRouter()

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat(req: schemas.ChatRequest):
    answer, sources = ask_rag(req.prompt, debug=req.debug)

    db = SessionLocal()
    db.add(models.ChatLog(prompt=req.prompt, answer=answer))
    db.commit()

    return schemas.ChatResponse(
        answer=answer,
        used_tool="RAG",
        sources=[schemas.ChatSource(**s) for s in (sources or [])] if req.debug else None
    )

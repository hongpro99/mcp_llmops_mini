from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import SessionLocal, engine, get_db
from .models import Base, ChatLog
from .schemas import ChatRequest, ChatResponse
from .rag_chain import rag
from .settings import settings
import os



print(">>> [app] 모듈 임포트 시작")

app = FastAPI(title= "Mini RAG Chat")

os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)  # ← 환경변수로 주입

@app.on_event("startup")
def on_startup():
    print(">>> [app] Startup: DB 테이블 생성 시도 (create_all)")
    # 서버 기동 시 1회 테이블 생성 시도
    try:
        Base.metadata.create_all(bind=engine)
        print(">>> [app] Startup: DB init OK")
    except Exception as e:
        print(f"[app] DB init failed: {e}")
        
# #DB 재생성
# Base.metadata.create_all(bind=engine)

        
@app.get("/api/health")
def health():
    print(">>> [app] /api/health")
    try:
        with get_db() as db:
            ver = db.execute(text("SELECT version()")).scalar_one()
        return {"status": "ok", "db_version": ver}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    print(f">>> [app] /api/chat: session={req.session_id}, top_k={req.top_k}")
    print(f">>> [app] /api/chat: query={req.query!r}")
    try:
        answer, sources = rag(req.query, k=req.top_k)  # ← LangSmith traceable
        log = ChatLog(session_id=req.session_id, user_message=req.query, assistant_message=answer)
        db.add(log); db.commit()
        print(">>> [app] /api/chat: chatlog committed")
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        print(f">>> [app] /api/chat: error → rollback: {e}")
        try: db.rollback()
        except: pass
        return ChatResponse(answer=f"오류가 발생했습니다: {e}", sources=[])
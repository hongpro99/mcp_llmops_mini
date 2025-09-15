from fastapi import FastAPI
from app.routers import chat
from app.db import Base, engine

# DB 초기화
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="mcp-llmops-mini")

# 라우터 등록
app.include_router(chat.router)


from fastapi import FastAPI
from backend.routers import chat, embedding, logs, agent
from backend.db import Base, engine

# DB 초기화
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="mcp-llmops-mini")

# 라우터 등록
app.include_router(chat.router)
app.include_router(embedding.router)
app.include_router(logs.router)
app.include_router(agent.router)

# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class _ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ✅ 요청 스키마: prompt가 반드시 있어야 합니다.
class ChatRequest(BaseModel):
    prompt: str
    debug: bool = False

# 디버그용 소스 노출
class ChatSource(BaseModel):
    doc_id: str
    score: float = 0.0
    snippet: str

# 응답 스키마
class ChatResponse(BaseModel):
    answer: str
    used_tool: str | None = None
    sources: list[ChatSource] | None = None

# 로그 조회용 (ORM -> Pydantic)
class ChatLog(_ORMModel):
    id: int
    prompt: str
    answer: str
    created_at: datetime | None = None

# Pydantic 스키마(입출력)

from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    session_id : str
    query : str
    top_k : int = 5
    
    def __init__(self, **data):
        print(f">>> [schemas] ChatRequest 생성: {data}")
        super().__init__(**data)    
    
class ChatResponse(BaseModel):
    answer : str
    
    def __init__(self, **data):
        print(f">>> [schemas] ChatResponse 생성: {data}")
        super().__init__(**data)    
    
class ChatLog(BaseModel):
    id: int
    prompt: str
    answer: str
    created_at: datetime | None = None
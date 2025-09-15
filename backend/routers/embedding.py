from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.llm import get_embedding

router = APIRouter()

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    vector: list[float]

@router.post("/embedding", response_model=EmbeddingResponse)
async def embedding(req: EmbeddingRequest):
    vec = get_embedding(req.text)
    return EmbeddingResponse(vector=vec)

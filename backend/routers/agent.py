# app/routers/agent.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langchain_core.messages import AIMessage, BaseMessage

from backend.agent.react_agent import run_agent_with_messages

router = APIRouter()

class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    answer: str
    used_tool: Optional[str] = None
    sources_hint: Optional[str] = None

@router.post("/agent", response_model=AgentResponse)
async def agent(req: AgentRequest):
    result = run_agent_with_messages(req.prompt)

    # LangGraph prebuilt ReAct는 {"messages": List[BaseMessage]} 형태를 반환
    msgs: list[BaseMessage] = result.get("messages", [])
    answer = ""

    # 뒤에서부터 첫 번째 AIMessage(content가 str 또는 list[dict]일 수 있음)를 찾는다
    for m in reversed(msgs):
        if isinstance(m, AIMessage):
            # content가 보통 str 이지만, tool 호출 결과가 섞이면 list[dict]일 수 있음
            if isinstance(m.content, str):
                answer = m.content
            else:
                # content가 list[dict]인 경우 텍스트만 추출
                try:
                    parts = []
                    for part in m.content:
                        if isinstance(part, dict) and "text" in part:
                            parts.append(part["text"])
                    answer = "\n".join(parts) if parts else str(m.content)
                except Exception:
                    answer = str(m.content)
            break

    sources_hint = "[SOURCES]" if "[SOURCES]" in answer else None
    return AgentResponse(answer=answer, sources_hint=sources_hint)

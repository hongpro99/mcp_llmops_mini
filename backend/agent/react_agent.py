# app/agent/react_agent.py
from __future__ import annotations
from typing import List, Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from backend.settings import settings
from backend.services.rag import retrieve
from backend.db import SessionLocal
from backend import models

# -----------------------
# Tools (ReAct에서 호출)
# -----------------------

@tool("get_weather", return_direct=False)
def get_weather(city: str) -> str:
    """Get weather for a given city (demo). Argument: city name."""
    return f"It's always sunny in {city}!"

@tool("rag_search", return_direct=False)
def rag_search(question: str) -> str:
    """Search internal corpus and return useful context for answering."""
    context, dbg = retrieve(question, top_k=3, debug=True)
    # 디버그 소스 정보를 응답에 포함(워크플로 관찰 시 확인 용이)
    src_lines = []
    for s in (dbg or []):
        src_lines.append(f"- {s['doc_id']} (L2={s['score']:.4f}) : {s['snippet'][:150]}")
    src_block = "\n".join(src_lines) if src_lines else "(no sources)"
    return f"[RAG CONTEXT]\n{context}\n\n[SOURCES]\n{src_block}"

@tool("show_recent_logs", return_direct=False)
def show_recent_logs(limit: int = 5) -> str:
    """Return recent chat logs from database. Optional: limit (int)."""
    db = SessionLocal()
    rows = db.query(models.ChatLog).order_by(models.ChatLog.id.desc()).limit(int(limit)).all()
    if not rows:
        return "No recent chat logs."
    return "\n".join([f"[{r.id}] {r.prompt} -> {r.answer[:120]}" for r in rows])

# 안전한 계산기 (사칙연산 위주)
import ast, operator as op
_ALLOWED = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.FloorDiv: op.floordiv
}
def _eval(node):
    if isinstance(node, ast.Num):  # <3.8
        return node.n
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _ALLOWED[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _ALLOWED[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")

@tool("calc", return_direct=False)
def calc(expr: str) -> str:
    """Safely evaluate a math expression. Use '^' for power if needed."""
    expr = expr.replace("^", "**")
    node = ast.parse(expr, mode="eval").body
    return str(_eval(node))

# -----------------------
# Model (LangChain OpenAI)
# -----------------------
# LangSmith 사용 시: .env에 LANGCHAIN_TRACING_V2/LANGCHAIN_API_KEY/LANGCHAIN_PROJECT 설정
llm = ChatOpenAI(
    model=settings.CHAT_MODEL,                 # 필요 시 변경 가능
    api_key=settings.OPENAI_API_KEY,
    temperature=0.2,
)

TOOLS = [get_weather, rag_search, show_recent_logs, calc]

# ReAct 스타일 에이전트 생성
agent = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt=(
        "You are a helpful assistant.\n"
        "- If the user asks about internal docs, use rag_search first.\n"
        "- If they ask to see recent conversations, use show_recent_logs.\n"
        "- If they ask to calculate, use calc.\n"
        "- Weather questions can use get_weather.\n"
        "Always use tools when helpful, then answer clearly."
    ),
)

def run_agent_with_messages(prompt: str) -> Dict[str, Any]:
    """
    입력: OpenAI 호환 messages 형식의 list
    출력: agent.invoke의 결과(최종 메시지 리스트)
    """
    return agent.invoke({"messages": [HumanMessage(content=prompt)]})

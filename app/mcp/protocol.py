from __future__ import annotations
from typing import Tuple, List, Dict, Any
from app.mcp.context import answer_with_sources

def ask_rag(prompt: str, debug: bool = False) -> Tuple[str, List[Dict[str, Any]] | None]:
    """
    외부(라우터/잡 등)에서 호출하는 서비스 API.
    - 정책/후처리/Guardrail 등도 여기서 캡슐화 가능.
    """
    # 예: 간단한 금칙어 필터(샘플)
    banned = ["DROP TABLE", "rm -rf", "format disk"]
    if any(bad.lower() in prompt.lower() for bad in banned):
        return "안전 정책에 의해 차단된 요청입니다.", None

    return answer_with_sources(prompt, debug=debug)

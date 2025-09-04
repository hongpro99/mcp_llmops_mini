# 🤖 mcp_llmops_mini - LLM 서버 & RAG 파이프라인

## 📌 프로젝트 개요
`mcp_llmops_mini`는 LLM 기반 질의응답 서비스를 제공하는 **경량 RAG 서버** 프로젝트입니다.  
텍스트 문서를 벡터화하여 검색 후 LLM에 컨텍스트를 전달하는 방식으로, 보다 정확하고 근거 있는 답변을 제공합니다.  
또한, MCP 구조를 채택할 예정입니다.

---

## 🎯 프로젝트 목표
- 사용자가 입력한 질문에 대해 **벡터 검색 + LLM**을 활용해 답변 제공
- RAG(Retrieval-Augmented Generation)를 통해 **환각(hallucination) 최소화**
- Docker 기반으로 누구나 손쉽게 **실행 및 배포 가능한 LLM 서버** 구축
- LLMOps(Monitoring/Prompt Tuning 등) 기초 기능 반영

---

## 🛠️ 기술 스택

### Language
- Python

### Backend
- FastAPI (REST API 서버)
- LangChain (프롬프트/체인 구성)

### Infra / DB
- FAISS (Vector Store)
- Docker (컨테이너화)
- AWS ECS / ECR (배포 환경, 옵션)

### ETC
- OpenAI API (Chat/Embedding)
- Pydantic Settings (환경변수 관리)

---

## ⚙️ 아키텍처
```text
사용자 입력
   └── FastAPI 서버 (/api/chat)
          ├── FAISS Vector Store (문서 검색)
          ├── LangChain (프롬프트 구성)
          └── OpenAI API (응답 생성)

---

## 참고 자료

### 🔹 LLM & RAG 
- [OpenAI RAG 소개](https://platform.openai.com/docs/guides/retrieval)  
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)  
- [FAISS: Facebook AI Similarity Search](https://github.com/facebookresearch/faiss)  
- [Pinecone: Vector Database](https://docs.pinecone.io/)  

### 🔹 LLMOps & 모니터링
- [LangSmith (LangChain Observability)](https://docs.smith.langchain.com/)  
- [LangFuse (LLM Observability Tool)](https://langfuse.com/docs)            
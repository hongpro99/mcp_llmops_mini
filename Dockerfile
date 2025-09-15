FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# 엔트리포인트: 인덱스 내려받기 -> 서버 실행
ENTRYPOINT ["bash", "-lc", "python -m tools.sync_index_from_s3 && uvicorn backend.app:app --host 0.0.0.0 --port 8080"]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.settings import settings

# PostgreSQL 연결 URL 생성
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Engine 생성 (DB 커넥션 풀 관리)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # 연결 유효성 검사 (죽은 커넥션 자동 복구)
    pool_size=10,             # 연결 풀 크기
    max_overflow=20           # 초과 연결 허용 개수
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 (모든 모델이 여기서 상속)
Base = declarative_base()

# 의존성 주입용 DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#SQLAlchemy 세션/엔진

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .settings import settings

print(">>> [db] 모듈 임포트 시작")

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future = True)
print(">>> [db] create_engine 완료 (아직 DB 연결 아님)")

SessionLocal = sessionmaker(bind=engine, autocommit = False, autoflush= False)
print(">>> [db] SessionLocal 생성 완료")

def get_db():
    print(" >>> [db] DB 세션 오픈 시도")
    db= SessionLocal()
    try:
        print(">>> [db] DB 세션 획득 완료")
        yield db
    finally:
        db.close()
        print(">>> [db] DB 세션 닫힘")
        
print(">>> [db] 모듈 임포트 완료")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 데이터베이스 연결 엔진
engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)

# 세션 공장 (Session Factory)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델들이 상속받을 기본 클래스
Base = declarative_base()

# ---> 이 함수가 빠져 있었습니다! <---
# API 요청이 올 때마다 DB 세션을 만들고, 일이 끝나면 닫아주는 역할
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""DB 연결. 라우터에서는 Depends(get_db) 로 세션을 받아 쓴다."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 를 여러 요청에서 같이 쓰기 위해 필요
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """모든 테이블 모델의 부모 클래스."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

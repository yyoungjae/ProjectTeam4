"""users 테이블 (Spring 의 Entity)."""

from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    delete_video_after_analysis: Mapped[bool] = mapped_column(default=False)  # 분석 후 영상 삭제 여부
    nickname: Mapped[str] = mapped_column(String(50), unique=True, index=True)  
    

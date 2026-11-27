"""운동 세션(workout_sessions)과 세트(sets) 테이블.

TODO: ERD 정하고 작성
- WorkoutSession: 운동 한 번 (사용자, 시작/종료 시각)
- Set: 세트 하나 (영상 경로, target_reps, rpe, status, 분석 결과 JSON)
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from app.core.database import Base

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    sets: Mapped[list["WorkoutSet"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.set_no",
    )

class WorkoutSet(Base):
    __tablename__ = "sets"
    __table_args__ = (UniqueConstraint("session_id", "set_no"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id"), index=True
    )
    set_no: Mapped[int]
    video_path: Mapped[str | None] = mapped_column(String(255))
    target_reps: Mapped[int]
    rpe: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    error_code: Mapped[str | None] = mapped_column(String(50))
    rep_count: Mapped[int | None]
    change_score: Mapped[float | None]
    rest_sec: Mapped[int | None]
    next_target_reps: Mapped[int | None]
    analysis: Mapped[dict | None] = mapped_column(JSON)  # 1번 측정값
    result: Mapped[dict | None] = mapped_column(JSON)    # 2번 판정/추천 결과
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    analyzed_at: Mapped[datetime | None]
    session: Mapped["WorkoutSession"] = relationship(back_populates="sets")
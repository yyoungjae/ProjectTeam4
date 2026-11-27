"""users 테이블 조회/저장 (Spring 의 Repository). 쿼리는 여기에만 쓴다."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


def find_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def find_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))

def find_by_nickname(db: Session, nickname: str) -> User | None:
    return db.scalar(select(User).where(User.nickname == nickname))

def save(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

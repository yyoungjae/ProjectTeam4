"""사용자 로직. DB 접근은 users.repository 를 통해서만 한다."""

from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.users import repository as user_repository
from app.users.models import User
from app.users.schemas import UserUpdateRequest


def update_me(db: Session, user: User, req: UserUpdateRequest) -> User:
    changes = req.model_dump(exclude_unset=True)  # 요청에 실제로 들어온 필드만

    new_nickname = changes.get("nickname")
    if new_nickname is not None and new_nickname != user.nickname:
        if user_repository.find_by_nickname(db, new_nickname):
            raise AppError(ErrorCode.NICKNAME_TAKEN)
        user.nickname = new_nickname

    if changes.get("delete_video_after_analysis") is not None:
        user.delete_video_after_analysis = changes["delete_video_after_analysis"]

    return user_repository.save(db, user)
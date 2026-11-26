"""라우터에서 같이 쓰는 의존성.

예시:
    @router.get("/me")
    def get_me(user: CurrentUser): ...      # 로그인 필요한 API
    def something(db: DbSession): ...      # DB 만 필요할 때
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError, ErrorCode
from app.core.security import decode_access_token
from app.users import repository as user_repository
from app.users.models import User

bearer = HTTPBearer(auto_error=False)  # 토큰 없을 때 FastAPI 기본 에러 대신 우리 형식으로 401


def get_current_user(
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if cred is None:
        raise AppError(ErrorCode.UNAUTHORIZED)
    user_id = decode_access_token(cred.credentials)
    if user_id is None:
        raise AppError(ErrorCode.UNAUTHORIZED)
    user = user_repository.find_by_id(db, user_id)
    if user is None:
        raise AppError(ErrorCode.UNAUTHORIZED)
    return user


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

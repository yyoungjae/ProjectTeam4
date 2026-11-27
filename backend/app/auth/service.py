"""인증 로직: 이메일 중복 확인, 비밀번호 해시/검증, 토큰 발급.
DB 접근은 users.repository 를 통해서만 한다."""
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, SignupRequest
from app.core.errors import AppError, ErrorCode
from app.core.security import create_access_token, hash_password, verify_password
from app.users import repository as user_repository
from app.users.models import User


def signup(db: Session, req: SignupRequest) -> User:
    if user_repository.find_by_email(db, req.email):
        raise AppError(ErrorCode.EMAIL_TAKEN)
    if user_repository.find_by_nickname(db, req.nickname):
        raise AppError(ErrorCode.NICKNAME_TAKEN)

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.nickname,
    )
    return user_repository.save(db, user)

def login(db: Session, req: LoginRequest) -> str:
    user = user_repository.find_by_email(db, req.email)
    # 이메일이 없든 비밀번호가 틀리든 같은 에러 (어느 쪽이 틀렸는지 알려주지 않음)
    if user is None or not verify_password(req.password, user.password_hash):
        raise AppError(ErrorCode.INVALID_CREDENTIALS)
    return create_access_token(user.id)
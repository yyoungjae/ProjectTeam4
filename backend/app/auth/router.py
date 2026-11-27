"""인증 API. 요청을 받고 service 를 부르기만 한다 (Spring 의 Controller)."""

from fastapi import APIRouter

from app.auth import service
from app.auth.schemas import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.core.deps import DbSession

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(req: SignupRequest, db: DbSession):
    return service.signup(db, req)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: DbSession):
    token = service.login(db, req)
    return TokenResponse(access_token=token)
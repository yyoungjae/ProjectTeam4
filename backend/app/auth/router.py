"""인증 API. 요청을 받고 service 를 부르기만 한다 (Spring 의 Controller)."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["인증"])

# TODO
# POST /api/auth/signup   회원가입
# POST /api/auth/login    로그인 → access_token

from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["사용자"])

# TODO
# GET   /api/users/me   내 정보 조회
# PATCH /api/users/me   내 정보 수정

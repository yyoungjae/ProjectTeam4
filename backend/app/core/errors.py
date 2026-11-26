"""에러 응답 통일: 모든 에러는 {"code": ..., "message": ...} 형식으로 나간다.

사용법: raise AppError(ErrorCode.EMAIL_TAKEN)
새 에러가 필요하면 ErrorCode 에 한 줄 추가하고, Notion 명세 에러 표에도 적기.
"""

from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorCode(Enum):
    # (HTTP 상태, 코드, 메시지)
    VALIDATION_ERROR = (400, "VALIDATION_ERROR", "요청 값이 올바르지 않습니다.")
    UNAUTHORIZED = (401, "UNAUTHORIZED", "로그인이 필요합니다.")
    INVALID_CREDENTIALS = (401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 틀렸습니다.")
    FORBIDDEN = (403, "FORBIDDEN", "접근 권한이 없습니다.")
    NOT_FOUND = (404, "NOT_FOUND", "대상을 찾을 수 없습니다.")
    EMAIL_TAKEN = (409, "EMAIL_TAKEN", "이미 가입된 이메일입니다.")
    INTERNAL_ERROR = (500, "INTERNAL_ERROR", "서버 오류가 발생했습니다.")

    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message


class AppError(Exception):
    def __init__(self, error: ErrorCode, message: str | None = None):
        self.error = error
        self.message = message or error.message  # 필요하면 메시지만 바꿔서 던질 수 있음


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return _error(exc.error.status, exc.error.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        # 첫 번째 에러만 "필드: 이유" 형태로 알려준다
        message = ErrorCode.VALIDATION_ERROR.message
        errors = exc.errors()
        if errors:
            field = ".".join(str(p) for p in errors[0]["loc"] if p != "body")
            message = f"{field}: {errors[0]['msg']}"
        return _error(400, ErrorCode.VALIDATION_ERROR.code, message)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        # 없는 주소(404), 안 되는 메서드(405) 같은 프레임워크 에러도 같은 형식으로
        code = "NOT_FOUND" if exc.status_code == 404 else f"HTTP_{exc.status_code}"
        return _error(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def unknown_error_handler(request: Request, exc: Exception):
        e = ErrorCode.INTERNAL_ERROR
        return _error(e.status, e.code, e.message)

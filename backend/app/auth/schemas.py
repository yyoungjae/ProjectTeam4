"""인증 요청/응답 모양 (Spring 의 DTO)."""

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    email: str = Field(
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        examples=["hankyul@example.com"],
    )
    password: str = Field(min_length=8, max_length=72, examples=["password123"])
    nickname: str = Field(min_length=2, max_length=50, examples=["한결"])


class LoginRequest(BaseModel):
    email: str = Field(examples=["hankyul@example.com"])
    password: str = Field(examples=["password123"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nickname: str
    delete_video_after_analysis: bool   # 추가


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
"""사용자 요청/응답 모양. 예: UserResponse, UserUpdateRequest"""
from pydantic import BaseModel, Field

class UserUpdateRequest(BaseModel):
    """보낸 값만 수정한다. 안 보낸 필드는 그대로 둔다."""

    nickname: str | None = Field(default=None, min_length=2, max_length=50)
    delete_video_after_analysis: bool | None = None
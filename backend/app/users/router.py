from fastapi import APIRouter

from app.auth.schemas import UserResponse
from app.core.deps import CurrentUser, DbSession
from app.users import service
from app.users.schemas import UserUpdateRequest

router = APIRouter(prefix="/api/users", tags=["사용자"])


@router.get("/me", response_model=UserResponse)
def get_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(req: UserUpdateRequest, user: CurrentUser, db: DbSession):
    return service.update_me(db, user, req)
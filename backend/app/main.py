"""앱 시작점. 실행: (backend 폴더에서) uvicorn app.main:app --reload"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.errors import register_exception_handlers
from app.users import models as user_models  # noqa: F401  (테이블 등록용 import)
from app.users.router import router as users_router
from app.workouts import models as workout_models  # noqa: F401  (테이블 등록용 import)
from app.workouts.router import router as workouts_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 서버 켤 때: 테이블 없으면 만들고, 업로드 폴더 준비
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(title="스쿼트 코치 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 프론트(Vite) 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workouts_router)


@app.get("/api/health", tags=["공통"])
def health():
    return {"status": "ok"}

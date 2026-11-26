"""환경 설정. 값은 backend/.env 에서 읽고, 없으면 아래 기본값을 쓴다."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./app.db"
    UPLOAD_DIR: str = "./uploads"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()

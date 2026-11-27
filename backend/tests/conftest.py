"""테스트 공통 설정. 테스트는 진짜 app.db 가 아니라 test.db 를 쓴다."""

import os

# app 을 import 하기 전에 DB 를 테스트용으로 바꿔야 한다 (순서 중요!)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)  # 테스트마다 DB 를 깨끗하게 비우고 시작
    with TestClient(app) as c:           # 서버 시작 시 create_all 이 테이블을 다시 만듦
        yield c

# backend (FastAPI)

## 실행 (Windows)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

- API 문서(Swagger): http://localhost:8000/docs
- 테스트: `pytest`
- 코드 검사: `ruff check .`

## 폴더 구조

```
app/
├─ main.py        앱 시작점: 라우터 등록, CORS, 에러 핸들러
├─ core/          공통: 설정, DB, 에러 형식, 비밀번호·JWT, 로그인 사용자
├─ auth/          회원가입·로그인
├─ users/         내 정보
├─ workouts/      운동 세션 + 세트 + 개인 기준 (API 경로는 /api/sessions, /api/sets)
├─ analysis/      [1번] analyze(): 영상 → rep별 측정값
└─ recommend/     [2번] judge(), recommend(), thresholds
```

도메인 폴더 안 파일 (Spring 대응):

| 파일 | 역할 | Spring |
|---|---|---|
| router.py | 요청 받고 service 호출 | Controller |
| service.py | 비즈니스 로직 | Service |
| repository.py | DB 조회·저장 | Repository |
| models.py | 테이블 | Entity |
| schemas.py | 요청·응답 모양 | DTO |

## 규칙

- 호출 방향은 router → service → repository. router 에서 DB 쿼리 직접 쓰지 않기.
- analysis/, recommend/ 는 DB·파일을 만지지 않는 순수 함수. workouts/service.py 가 불러서 쓴다.
- 에러는 `raise AppError(ErrorCode.XXX)` 로 던진다. 응답은 항상 `{"code", "message"}`.
- 성공 응답은 데이터만 그대로 보낸다 (감싸는 형식 없음).
- analysis/, recommend/ 는 지금 가짜 값을 돌려주는 임시 함수. 반환 형식은 "분석 파이프라인 역할·데이터 규격" 문서 기준이고, 1·2번이 실제 코드로 교체한다.

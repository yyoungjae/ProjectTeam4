# frontend (React + Vite)

## 실행 (Windows)

프로젝트 루트(`ProjectTeam4`)위치에서 터미널을 실행한다.

```powershell
cd frontend
npm.cmd install
npm.cmd run dev -- --open
```

## 폴더 구조


| 위치 | 역할 |
| --- | --- |
| `src/App.jsx` | 현재 화면, 로그인 상태, 운동 진행 흐름 |
| `src/core/` | HTTP 요청, Bearer 토큰, 에러 처리와 값 표시 |
| `src/auth/` | 로그인·회원가입 화면과 API |
| `src/users/` | 내 정보 화면과 조회·수정 API |
| `src/workouts/` | 세트 입력·분석·결과·기록 화면, 운동 API와 결과 변환 |
| `src/api.js` | 기능별 요청을 하나의 클라이언트로 묶는 진입점 |
| `src/demoApi.js` | 서버 없이 시연할 때 사용하는 예시 데이터 |

## 백엔드 연동

개발 서버는 `/api` 요청을 `http://127.0.0.1:8000`으로 넘긴다. 백엔드를 실행한 뒤 `http://localhost:8000/docs`에서 실제 경로와 필드를 확인한다. 배포 시 같은 출처의 `/api`를 쓰거나 Vite 환경 변수 `VITE_API_BASE_URL`에 백엔드 주소를 지정할 수 있다.

현재 팀 백엔드는 `GET /api/health`와 기본 구조가 있는 단계다. 로그인·영상 업로드·결과 조회는 라우터 구현 후 실제 응답으로 확인해야 한다. 프론트 업로드에서 가정하는 `video`, `rpe`, `target_reps` 필드는 `src/workouts/api.js`에서 조정한다.

`src/workouts/result.js`는 백엔드 임시 함수의 `rep_no`, `start_t`·`end_t`, `rest_sec`도 화면에서 읽을 수 있게 변환한다. 운동 API의 최종 응답이 정해지면 이 파일에서 변환 규칙을 맞춘다.

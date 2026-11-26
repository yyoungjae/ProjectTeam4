"""운동 세션 + 세트 API. 경로는 Notion 명세 기준."""

from fastapi import APIRouter

router = APIRouter(tags=["운동"])

# TODO
# POST  /api/sessions                      운동 시작
# GET   /api/sessions/current              진행 중인 운동 조회
# GET   /api/sessions                      운동 기록 목록
# GET   /api/sessions/{session_id}         운동 상세·요약
# PATCH /api/sessions/{session_id}/end     운동 종료
# POST  /api/sessions/{session_id}/sets    세트 영상 업로드 → 202, 분석은 BackgroundTasks
# GET   /api/sets/{set_id}/status          분석 상태 확인 (PENDING/PROCESSING/DONE/FAILED)
# GET   /api/sets/{set_id}                 세트 결과 조회
# GET   /api/baseline                      개인 기준 조회

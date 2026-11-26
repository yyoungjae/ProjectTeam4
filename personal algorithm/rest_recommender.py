"""Configurable rule-based rest-time recommendation."""
from __future__ import annotations
from .config import MIN_REST_SEC, MAX_REST_SEC


def recommend_rest(fatigue_score: float) -> dict:
    """Map a provisional 0..100 score linearly to the configured rest range."""
    score = max(0.0, min(100.0, float(fatigue_score)))
    rest = MIN_REST_SEC + (MAX_REST_SEC - MIN_REST_SEC) * (score / 100.0)
    rest_rounded = int(round(rest / 5.0) * 5)
    rest_rounded = max(MIN_REST_SEC, min(MAX_REST_SEC, rest_rounded))

    if score < 25:
        explanation = "입력 피로도와 영상상 수행 변화 점수가 낮아 기본 휴식 범위에 가깝게 추천했습니다."
    elif score < 60:
        explanation = "입력 피로도 또는 영상상 수행 변화가 중간 수준이어서 휴식 시간을 늘려 추천했습니다."
    else:
        explanation = "입력 피로도 또는 영상상 수행 변화가 높은 편이어서 설정된 범위 내 긴 휴식 시간을 추천했습니다."

    return {
        "recommended_rest_sec": rest_rounded,
        "configured_min_rest_sec": MIN_REST_SEC,
        "configured_max_rest_sec": MAX_REST_SEC,
        "fatigue_score": round(score, 2),
        "explanation": explanation,
        "note": "휴식 시간 범위와 계산식은 초기 프로토타입용 임시 규칙이며, 실험 데이터를 통해 조정해야 합니다.",
    }

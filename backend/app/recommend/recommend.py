"""[2번 담당] 판정 결과 + 피로도 → 휴식 시간, 다음 목표 횟수.

지금은 고정값을 돌려주는 임시 함수. 2번이 교체한다.
"""


def recommend(current: dict, baseline: dict | None, previous_sets: list[dict], rpe: int) -> dict:
    return {
        "rest_sec": 90,
        "next_target_reps": 15,
        "change_score": 0.0,
        "reason": "임시 추천값입니다.",
        "reason_codes": [],
    }

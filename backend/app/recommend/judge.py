"""[2번 담당] 측정값 → rep별 판정 + 피드백.

지금은 전부 통과로 돌려주는 임시 함수. 2번이 교체한다.
규칙: DB 접근 금지 (입력 dict 만 보고 결과 dict 를 돌려준다).
"""


def judge(analysis: dict, baseline: dict | None) -> dict:
    reps = [
        {
            "rep_no": r["rep_no"],
            "depth_ok": True,
            "torso_ok": True,
            "lockout_ok": True,
            "tempo_ok": True,
        }
        for r in analysis["reps"]
    ]
    return {
        "reps": reps,
        "consistency": {"depth_change": 0.0, "ascent_change": 0.0},
        "feedback": [],
    }

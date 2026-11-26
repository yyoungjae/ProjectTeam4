"""[1번 담당] 영상 → rep별 측정값.

지금은 가짜 데이터를 돌려주는 임시 함수다. 백엔드·프론트가 먼저 연결해 볼 수 있게 둔 것이고,
1번이 ml/ 의 분석 코드를 이 함수 안으로 옮겨서 교체한다.
반환 형식은 "분석 파이프라인 역할·데이터 규격" 문서 기준. 필드가 바뀌면 문서도 같이 수정.

규칙: DB 접근 금지, 파일 저장 금지 (영상 경로를 받아 dict 만 돌려준다).
"""


def analyze(video_path: str) -> dict:
    reps = [
        {
            "rep_no": i,
            "start_t": 1.0 + (i - 1) * 2.5,
            "bottom_t": 2.0 + (i - 1) * 2.5,
            "end_t": 3.2 + (i - 1) * 2.5,
            "min_thigh_angle": -4.0,
            "max_torso_angle": 31.0,
            "top_knee_angle": 172.0,
            "top_hip_angle": 171.0,
            "descent_sec": 1.0,
            "ascent_sec": 1.2,
            "pause_sec": 0.1,
        }
        for i in range(1, 11)
    ]
    return {
        "fps": 30.0,
        "duration_sec": 27.0,
        "side": "left",
        "detected_ratio": 0.97,
        "rep_count": len(reps),
        "reps": reps,
    }

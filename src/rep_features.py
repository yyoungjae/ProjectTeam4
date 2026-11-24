import pandas as pd
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 입력 파일
DETECTION_PATH = BASE_DIR / "results" / "squat_detection.csv"
SUMMARY_PATH = BASE_DIR / "results" / "squat_summary.csv"

# 출력 파일
OUTPUT_PATH = BASE_DIR / "results" / "rep_features.csv"


def extract_rep_features():
    # CSV 데이터 불러오기
    detection_df = pd.read_csv(DETECTION_PATH)
    summary_df = pd.read_csv(SUMMARY_PATH)

    features = []

    for _, rep in summary_df.iterrows():
        rep_id = int(rep["rep_id"])

        # 해당 반복에 속하는 프레임만 추출
        rep_frames = detection_df[
            detection_df["rep_id"] == rep_id
        ].copy()

        if rep_frames.empty:
            continue

        # 각 단계별 프레임
        descent = rep_frames[rep_frames["phase"] == "DESCENT"]
        ascent = rep_frames[rep_frames["phase"] == "ASCENT"]

        # 수행 시간 (초)
        duration_sec = rep["duration_ms"] / 1000

        # 하강 및 상승 시간
        descent_duration = (
            descent["timestamp_ms"].max()
            - descent["timestamp_ms"].min()
        ) / 1000 if len(descent) > 0 else 0

        ascent_duration = (
            ascent["timestamp_ms"].max()
            - ascent["timestamp_ms"].min()
        ) / 1000 if len(ascent) > 0 else 0

        # 무릎 가동 범위
        start_angle = rep_frames["smoothed_angle"].iloc[0]
        min_angle = rep["min_knee_angle"]
        range_of_motion = start_angle - min_angle

        features.append({
            "rep_id": rep_id,
            "start_angle": round(start_angle, 2),
            "min_knee_angle": round(min_angle, 2),
            "range_of_motion": round(range_of_motion, 2),
            "duration_sec": round(duration_sec, 2),
            "descent_duration_sec": round(descent_duration, 2),
            "ascent_duration_sec": round(ascent_duration, 2),
            "descent_frames": len(descent),
            "ascent_frames": len(ascent)
        })

    # 결과 저장
    result_df = pd.DataFrame(features)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("\n반복별 특징 추출 완료!")
    print(result_df.to_string(index=False))
    print(f"\n저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_rep_features()
import pandas as pd
import sys

from pathlib import Path

# 파일 경로 설정


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 명령어에서 영상 이름 전달받기
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

if VIDEO_NAME == "squat_test":

    DETECTION_PATH = RESULTS_DIR / "squat_detection.csv"
    SUMMARY_PATH = RESULTS_DIR / "squat_summary.csv"
    OUTPUT_PATH = RESULTS_DIR / "rep_features.csv"

else:

    DETECTION_PATH = RESULTS_DIR / f"{VIDEO_NAME}_squat_detection.csv"
    SUMMARY_PATH = RESULTS_DIR / f"{VIDEO_NAME}_squat_summary.csv"
    OUTPUT_PATH = RESULTS_DIR / f"{VIDEO_NAME}_rep_features.csv"

#  반복별 특징 추출

def extract_rep_features():

    # 입력 파일 확인
    if not DETECTION_PATH.exists():
        raise FileNotFoundError(
            f"반복 감지 파일을 찾을 수 없습니다: {DETECTION_PATH}"
        )

    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"반복 요약 파일을 찾을 수 없습니다: {SUMMARY_PATH}"
        )

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

        # 단계별 프레임 구분
        descent = rep_frames[
            rep_frames["phase"] == "DESCENT"
        ]

        ascent = rep_frames[
            rep_frames["phase"] == "ASCENT"
        ]

        # 전체 수행 시간
        duration_sec = rep["duration_ms"] / 1000

        # 하강 시간
        descent_duration = (
            descent["timestamp_ms"].max()
            - descent["timestamp_ms"].min()
        ) / 1000 if len(descent) > 0 else 0

        # 상승 시간
        ascent_duration = (
            ascent["timestamp_ms"].max()
            - ascent["timestamp_ms"].min()
        ) / 1000 if len(ascent) > 0 else 0

        # 무릎 가동 범위
        start_angle = rep_frames["smoothed_angle"].iloc[0]
        min_angle = rep["min_knee_angle"]

        range_of_motion = start_angle - min_angle

        # 반복별 특징 저장
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

    # 결과 데이터프레임 생성
    result_df = pd.DataFrame(features)

    # 결과 저장
    result_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n반복별 특징 추출 완료!")
    print(f"분석 영상: {VIDEO_NAME}")
    print(f"추출된 반복 횟수: {len(result_df)}회")

    print("\n반복별 분석 결과:")
    print(result_df.to_string(index=False))

    print(f"\n결과 파일 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_rep_features()

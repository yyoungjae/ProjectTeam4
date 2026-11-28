
import pandas as pd
import sys
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 분석할 영상 이름
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

# 입력 및 출력 파일 경로
if VIDEO_NAME == "squat_test":
    DETECTION_PATH = RESULTS_DIR / "squat_detection.csv"
    TORSO_PATH = RESULTS_DIR / "torso_angles.csv"
    SUMMARY_PATH = RESULTS_DIR / "squat_summary.csv"
    OUTPUT_PATH = RESULTS_DIR / "rep_torso_features.csv"
else:
    DETECTION_PATH = RESULTS_DIR / f"{VIDEO_NAME}_squat_detection.csv"
    TORSO_PATH = RESULTS_DIR / f"{VIDEO_NAME}_torso_angles.csv"
    SUMMARY_PATH = RESULTS_DIR / f"{VIDEO_NAME}_squat_summary.csv"
    OUTPUT_PATH = RESULTS_DIR / f"{VIDEO_NAME}_rep_torso_features.csv"


def extract_torso_features():

    # 입력 파일 존재 확인
    for path in [DETECTION_PATH, TORSO_PATH, SUMMARY_PATH]:
        if not path.exists():
            raise FileNotFoundError(
                f"필요한 파일을 찾을 수 없습니다: {path}"
            )

    # CSV 파일 불러오기
    detection_df = pd.read_csv(DETECTION_PATH)
    torso_df = pd.read_csv(TORSO_PATH)
    summary_df = pd.read_csv(SUMMARY_PATH)

    # 프레임 번호를 기준으로 결합
    merged_df = pd.merge(
        detection_df,
        torso_df[["frame", "torso_angle"]],
        on="frame",
        how="inner"
    )

    features = []

    # 완료된 반복만 분석
    completed_reps = summary_df[
        summary_df["rep_id"] != 0
    ]

    for _, rep in completed_reps.iterrows():

        rep_id = int(rep["rep_id"])

        # 해당 반복에 속하는 프레임 추출
        rep_frames = merged_df[
            (merged_df["rep_id"] == rep_id)
            & (merged_df["rep_completed"] == True)
        ].copy()

        if rep_frames.empty:
            continue

        # 반복별 상체 기울기 통계
        mean_angle = rep_frames["torso_angle"].mean()
        max_angle = rep_frames["torso_angle"].max()
        min_angle = rep_frames["torso_angle"].min()

        # 최저점 프레임의 상체 기울기
        bottom_frame = int(rep["bottom_frame"])

        bottom_data = torso_df[
            torso_df["frame"] == bottom_frame
        ]

        if not bottom_data.empty:
            bottom_angle = bottom_data["torso_angle"].iloc[0]
        else:
            bottom_angle = None

        features.append({
            "rep_id": rep_id,
            "mean_torso_angle": round(mean_angle, 2),
            "max_torso_angle": round(max_angle, 2),
            "min_torso_angle": round(min_angle, 2),
            "bottom_frame": bottom_frame,
            "bottom_torso_angle": (
                round(bottom_angle, 2)
                if pd.notna(bottom_angle)
                else None
            ),
            "analyzed_frames": len(rep_frames)
        })

    # 결과 저장
    result_df = pd.DataFrame(features)

    result_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n반복별 상체 기울기 특징 추출 완료!")
    print(f"분석 영상: {VIDEO_NAME}")
    print(f"추출된 반복 횟수: {len(result_df)}회")

    if not result_df.empty:
        print("\n반복별 분석 결과:")
        print(result_df.to_string(index=False))
    else:
        print("분석할 완료된 반복이 없습니다.")

    print(f"\n저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_torso_features()

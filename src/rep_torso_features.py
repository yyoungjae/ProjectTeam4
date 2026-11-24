
import pandas as pd
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 입력 파일
DETECTION_PATH = BASE_DIR / "results" / "squat_detection.csv"
TORSO_PATH = BASE_DIR / "results" / "torso_angles.csv"
SUMMARY_PATH = BASE_DIR / "results" / "squat_summary.csv"

# 출력 파일
OUTPUT_PATH = BASE_DIR / "results" / "rep_torso_features.csv"


def extract_torso_features():

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

    if not result_df.empty:
        print(result_df.to_string(index=False))
    else:
        print("분석할 완료된 반복이 없습니다.")

    print(f"\n저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_torso_features()

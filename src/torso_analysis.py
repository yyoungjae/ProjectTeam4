import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 분석할 영상 이름
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

# 입력 및 출력 파일 경로
if VIDEO_NAME == "squat_test":
    LANDMARK_PATH = RESULTS_DIR / "landmarks.csv"
    OUTPUT_PATH = RESULTS_DIR / "torso_angles.csv"
else:
    LANDMARK_PATH = RESULTS_DIR / f"{VIDEO_NAME}_landmarks.csv"
    OUTPUT_PATH = RESULTS_DIR / f"{VIDEO_NAME}_torso_angles.csv"

# MediaPipe Landmark ID
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_HIP = 23
RIGHT_HIP = 24

VISIBILITY_THRESHOLD = 0.5


def calculate_torso_angle(shoulder, hip):
    
    # 어깨 중심과 엉덩이 중심을 연결한 선이수직 방향에서 얼마나 기울어졌는지 계산한다.
    
    dx = shoulder[0] - hip[0]
    dy = hip[1] - shoulder[1]

    angle = np.degrees(np.arctan2(abs(dx), abs(dy)))

    return angle


def analyze_torso():

    if not LANDMARK_PATH.exists():
        raise FileNotFoundError(
            f"랜드마크 파일을 찾을 수 없습니다: {LANDMARK_PATH}"
        )

    df = pd.read_csv(LANDMARK_PATH)

    results = []

    for frame, group in df.groupby("frame"):

        landmarks = group.set_index("landmark_id")

        required_ids = [
            LEFT_SHOULDER,
            RIGHT_SHOULDER,
            LEFT_HIP,
            RIGHT_HIP
        ]

        # 필요한 랜드마크 확인
        if not all(i in landmarks.index for i in required_ids):
            continue

        # 랜드마크 신뢰도 확인
        if any(
            landmarks.loc[i, "visibility"] < VISIBILITY_THRESHOLD
            for i in required_ids
        ):
            continue

        # 어깨 중심 좌표
        shoulder_x = (
            landmarks.loc[LEFT_SHOULDER, "x"]
            + landmarks.loc[RIGHT_SHOULDER, "x"]
        ) / 2

        shoulder_y = (
            landmarks.loc[LEFT_SHOULDER, "y"]
            + landmarks.loc[RIGHT_SHOULDER, "y"]
        ) / 2

        # 엉덩이 중심 좌표
        hip_x = (
            landmarks.loc[LEFT_HIP, "x"]
            + landmarks.loc[RIGHT_HIP, "x"]
        ) / 2

        hip_y = (
            landmarks.loc[LEFT_HIP, "y"]
            + landmarks.loc[RIGHT_HIP, "y"]
        ) / 2

        shoulder = (shoulder_x, shoulder_y)
        hip = (hip_x, hip_y)

        torso_angle = calculate_torso_angle(shoulder, hip)

        results.append({
            "frame": int(frame),
            "torso_angle": round(torso_angle, 2),
            "shoulder_x": round(shoulder_x, 5),
            "shoulder_y": round(shoulder_y, 5),
            "hip_x": round(hip_x, 5),
            "hip_y": round(hip_y, 5)
        })

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n상체 기울기 분석 완료!")
    print(f"분석 영상: {VIDEO_NAME}")
    print(f"분석된 프레임: {len(result_df)}")

    if not result_df.empty:
        print("\n상체 기울기 통계:")
        print(result_df["torso_angle"].describe())

    print(f"\n저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze_torso()


import sys
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 분석할 영상 이름
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

# 입력 및 출력 파일 경로
if VIDEO_NAME == "squat_test":
    INPUT_PATH = RESULTS_DIR / "torso_angles.csv"
    OUTPUT_PATH = RESULTS_DIR / "torso_angle_graph.png"
else:
    INPUT_PATH = RESULTS_DIR / f"{VIDEO_NAME}_torso_angles.csv"
    OUTPUT_PATH = RESULTS_DIR / f"{VIDEO_NAME}_torso_angle_graph.png"


def visualize_torso_angle():

    # CSV 파일 존재 여부 확인
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {INPUT_PATH}")

    # CSV 파일 불러오기
    df = pd.read_csv(INPUT_PATH)

    if df.empty:
        print("분석 데이터가 없습니다.")
        return

    # 결측값 제거
    df = df.dropna(subset=["torso_angle"]).copy()

    if df.empty:
        print("계산된 상체 각도 데이터가 없습니다.")
        return

    # 그래프 크기 설정
    plt.figure(figsize=(12, 6))

    # 상체 기울기 그래프
    plt.plot(
        df["frame"],
        df["torso_angle"],
        label="Torso Lean Angle",
        linewidth=2
    )

    # 평균 기울기 표시
    mean_angle = df["torso_angle"].mean()

    plt.axhline(
        y=mean_angle,
        linestyle="--",
        label=f"Mean: {mean_angle:.2f} degrees"
    )

    # 그래프 제목 및 축 설정
    plt.title(f"Squat Torso Lean Angle Analysis - {VIDEO_NAME}")
    plt.xlabel("Frame")
    plt.ylabel("Torso Lean Angle (degrees)")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # 그래프 저장
    plt.savefig(OUTPUT_PATH, dpi=300)

    plt.show()

    print("\n상체 기울기 그래프 생성 완료!")
    print(f"분석 영상: {VIDEO_NAME}")
    print(f"저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    visualize_torso_angle()

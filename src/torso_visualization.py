
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 입력 파일
INPUT_PATH = BASE_DIR / "results" / "torso_angles.csv"

# 출력 파일
OUTPUT_PATH = BASE_DIR / "results" / "torso_angle_graph.png"


def visualize_torso_angle():
    # CSV 파일 불러오기
    df = pd.read_csv(INPUT_PATH)

    if df.empty:
        print("분석 데이터가 없습니다.")
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
    plt.title("Squat Torso Lean Angle Analysis")
    plt.xlabel("Frame")
    plt.ylabel("Torso Lean Angle (degrees)")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # 그래프 저장
    plt.savefig(OUTPUT_PATH, dpi=300)

    plt.show()

    print("\n상체 기울기 그래프 생성 완료!")
    print(f"저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    visualize_torso_angle()


import sys
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 분석할 영상 이름 설정
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

# 입력 및 출력 파일 경로 설정
if VIDEO_NAME == "squat_test":
    INPUT_CSV = RESULTS_DIR / "knee_angles.csv"
    OUTPUT_IMAGE = RESULTS_DIR / "knee_angle_graph.png"
else:
    INPUT_CSV = RESULTS_DIR / f"{VIDEO_NAME}_knee_angles.csv"
    OUTPUT_IMAGE = RESULTS_DIR / f"{VIDEO_NAME}_knee_angle_graph.png"

# 데이터 불러오기
if not INPUT_CSV.exists():
    raise FileNotFoundError(f"입력 파일이 없습니다: {INPUT_CSV}")

df = pd.read_csv(INPUT_CSV)

# 왼쪽 무릎 각도가 존재하는 데이터만 사용
df = df.dropna(subset=["left_knee_angle"]).copy()

if df.empty:
    raise ValueError("계산된 왼쪽 무릎 각도 데이터가 없습니다.")

# 시간 및 각도 데이터
time_seconds = df["timestamp_ms"] / 1000
knee_angles = df["left_knee_angle"]

# 그래프 생성
plt.figure(figsize=(12, 6))

plt.plot(
    time_seconds,
    knee_angles,
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="Left Knee Angle"
)

# 최소 각도 표시
min_index = knee_angles.idxmin()

min_time = time_seconds.loc[min_index]
min_angle = knee_angles.loc[min_index]

plt.scatter(
    min_time,
    min_angle,
    s=80,
    label="Minimum Knee Angle",
    zorder=3
)

plt.annotate(
    f"Minimum: {min_angle:.2f} degrees",
    xy=(min_time, min_angle),
    xytext=(10, 15),
    textcoords="offset points"
)

# 그래프 제목 및 축 설정
plt.title(f"Squat Knee Angle Analysis - {VIDEO_NAME}")
plt.xlabel("Time (seconds)")
plt.ylabel("Knee Angle (degrees)")

plt.ylim(0, 190)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# 그래프 저장 및 표시
plt.savefig(OUTPUT_IMAGE, dpi=150)

print("무릎 각도 그래프 생성 완료!")
print(f"분석 영상: {VIDEO_NAME}")
print(f"저장 위치: {OUTPUT_IMAGE}")

plt.show()

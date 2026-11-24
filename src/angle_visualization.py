
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


# ==========================================
# 1. 파일 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_CSV = BASE_DIR / "results" / "knee_angles.csv"
OUTPUT_IMAGE = BASE_DIR / "results" / "knee_angle_graph.png"


# ==========================================
# 2. 데이터 불러오기
# ==========================================

if not INPUT_CSV.exists():
    raise FileNotFoundError("knee_angles.csv 파일이 없습니다.")

df = pd.read_csv(INPUT_CSV)

# 왼쪽 무릎 각도가 존재하는 데이터만 사용
df = df.dropna(subset=["left_knee_angle"]).copy()

if df.empty:
    raise ValueError("계산된 왼쪽 무릎 각도 데이터가 없습니다.")


# ==========================================
# 3. 시간 데이터 계산
# ==========================================

# 밀리초를 초 단위로 변환
time_seconds = df["timestamp_ms"] / 1000

knee_angles = df["left_knee_angle"]


# ==========================================
# 4. 그래프 생성
# ==========================================

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
plt.title("Squat Knee Angle Analysis")

plt.xlabel("Time (seconds)")
plt.ylabel("Knee Angle (degrees)")

plt.ylim(0, 190)

plt.grid(True, alpha=0.3)

plt.legend()

plt.tight_layout()


# ==========================================
# 5. 그래프 저장 및 표시
# ==========================================

plt.savefig(
    OUTPUT_IMAGE,
    dpi=150
)

print("무릎 각도 그래프 생성 완료!")
print(f"저장 위치: {OUTPUT_IMAGE}")

plt.show()

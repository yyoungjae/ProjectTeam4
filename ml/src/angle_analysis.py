import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 파일 경로 설정

BASE_DIR = Path(__file__).resolve().parent.parent

#인풋 데이터 셋을 현재 수동으로 바꾸면서 파일을 생성하고 있음.
#어느정도 기준이 확립되면 자동파일 생성 프로세스 구축 예정.
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

INPUT_CSV = (
    BASE_DIR / "results" / f"{VIDEO_NAME}_landmarks.csv"
)

OUTPUT_CSV = (
    BASE_DIR / "results" / f"{VIDEO_NAME}_knee_angles.csv"
)

# 랜드마크 ID  무릎ㅁ각도 계산에 피요한 관절들을 선택하는 부분

# 왼쪽 다리
LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27

# 오른쪽 다리
RIGHT_HIP = 24
RIGHT_KNEE = 26
RIGHT_ANKLE = 28

# 신뢰도 기준(임시 설정) 추후해 영상별 검출 결과를 확인하면서 맞춤 조정 할 계획
VISIBILITY_THRESHOLD = 0.5


#  세 점을 이용한 각도 계산 함수

def calculate_angle(a, b, c):

    # 무릎을 기준으로 두 벡터 생성
    vector_1 = a - b
    vector_2 = c - b

    # 내적을 활용해서 벡터 크기 계산
    norm_1 = np.linalg.norm(vector_1)
    norm_2 = np.linalg.norm(vector_2)

    # 길이가 0인 벡터는 계산할 수 없음
    if norm_1 == 0 or norm_2 == 0:
        return np.nan

    # 두 벡터의 내적을 이용해 cos 값 계산
    cosine = np.dot(vector_1, vector_2) / (
        norm_1 * norm_2
    )

    # 부동소수점 오차 방지
    cosine = np.clip(cosine, -1.0, 1.0)

    # 라디안 -> 도(degree) 변환
    angle = np.degrees(np.arccos(cosine))

    return angle


# 한쪽 무릎 각도 계산

def calculate_knee_angle(frame_data, hip_id, knee_id, ankle_id):

    # 현재 프레임의 랜드마크를 ID로 검색
    points = {
        int(row.landmark_id): row
        for row in frame_data.itertuples()
    }

    required_ids = [hip_id, knee_id, ankle_id]

    # 필요한 관절 데이터가 없는 경우
    if not all(lm_id in points for lm_id in required_ids):
        return np.nan, np.nan

    hip = points[hip_id]
    knee = points[knee_id]
    ankle = points[ankle_id]

    # 세 관절의 신뢰도 중 가장 낮은 값
    min_visibility = min(
        hip.visibility,
        knee.visibility,
        ankle.visibility
    )

    # 신뢰도가 기준보다 낮으면 계산하지 않음
    if (
        pd.isna(min_visibility)
        or min_visibility < VISIBILITY_THRESHOLD
    ):
        return np.nan, min_visibility

    # 2D 좌표 사용
    a = np.array([hip.x, hip.y])
    b = np.array([knee.x, knee.y])
    c = np.array([ankle.x, ankle.y])

    angle = calculate_angle(a, b, c)

    return angle, min_visibility


# 전체 프레임 분석

def main():

    print("=" * 50)
    print("무릎 관절 각도 분석 시작")
    print("=" * 50)

    # 입력 파일 확인
    if not INPUT_CSV.exists():
        print("오류: landmarks.csv 파일이 없습니다.")
        return

    # CSV 읽기
    df = pd.read_csv(INPUT_CSV)

    # 필요한 열 확인
    required_columns = {
        "frame",
        "timestamp_ms",
        "landmark_id",
        "x",
        "y",
        "visibility"
    }

    if not required_columns.issubset(df.columns):
        print("오류: CSV 데이터 구조가 올바르지 않습니다.")
        return

    results = []

    # 프레임 번호별로 그룹화
    for frame_number, frame_data in df.groupby("frame", sort=True):

        timestamp_ms = frame_data["timestamp_ms"].iloc[0]

        # 왼쪽 무릎 각도
        left_angle, left_visibility = calculate_knee_angle(
            frame_data,
            LEFT_HIP,
            LEFT_KNEE,
            LEFT_ANKLE
        )

        # 오른쪽 무릎 각도
        right_angle, right_visibility = calculate_knee_angle(
            frame_data,
            RIGHT_HIP,
            RIGHT_KNEE,
            RIGHT_ANKLE
        )

        results.append({
            "frame": frame_number,
            "timestamp_ms": timestamp_ms,
            "left_knee_angle": left_angle,
            "right_knee_angle": right_angle,
            "left_visibility": left_visibility,
            "right_visibility": right_visibility
        })

    # 결과를 DataFrame으로 변환
    result_df = pd.DataFrame(results)

    # CSV 저장
    result_df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # 분석 결과 출력
    print("\n분석 완료!")
    print(f"전체 프레임: {len(result_df)}")

    print(
        "왼쪽 무릎 각도 계산 성공:",
        result_df["left_knee_angle"].notna().sum()
    )

    print(
        "오른쪽 무릎 각도 계산 성공:",
        result_df["right_knee_angle"].notna().sum()
    )

    print(f"\n결과 저장 위치: {OUTPUT_CSV}")

    print("\n앞부분 분석 결과:")
    print(result_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()

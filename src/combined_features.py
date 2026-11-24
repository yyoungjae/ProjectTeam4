
import pandas as pd
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 입력 파일
KNEE_PATH = BASE_DIR / "results" / "rep_features.csv"
TORSO_PATH = BASE_DIR / "results" / "rep_torso_features.csv"

# 출력 파일
OUTPUT_PATH = BASE_DIR / "results" / "combined_features.csv"


def combine_features():

    # CSV 파일 불러오기
    knee_df = pd.read_csv(KNEE_PATH)
    torso_df = pd.read_csv(TORSO_PATH)

    # rep_id 기준으로 데이터 통합
    combined_df = pd.merge(
        knee_df,
        torso_df,
        on="rep_id",
        how="inner",
        validate="one_to_one"
    )

    # 분석 결과 정렬
    combined_df = combined_df.sort_values("rep_id")

    # CSV 저장
    combined_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n무릎 + 상체 분석 데이터 통합 완료!")
    print(f"통합된 반복 횟수: {len(combined_df)}회")

    print("\n통합 분석 결과:")
    print(combined_df.to_string(index=False))

    print(f"\n저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    combine_features()

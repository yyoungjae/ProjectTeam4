
import pandas as pd
import numpy as np
import sys

from pathlib import Path


#파일 경로 설정


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# 명령어에서 영상 이름 전달
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

# 무릎 각도 CSV 경로
INPUT_CSV = RESULTS_DIR / f"{VIDEO_NAME}_knee_angles.csv"

# 기존 첫 번째 영상 파일명 호환
if VIDEO_NAME == "squat_test" and not INPUT_CSV.exists():
    INPUT_CSV = RESULTS_DIR / "knee_angles.csv"

# 분석 결과 저장 경로
OUTPUT_CSV = RESULTS_DIR / f"{VIDEO_NAME}_squat_detection.csv"
SUMMARY_CSV = RESULTS_DIR / f"{VIDEO_NAME}_squat_summary.csv"



# 스쿼트 분석 기준 설정( 논문이나 실제 공신력이 있는 출처에서 참고해 확립 우선 임시 알고리즘)

# 스쿼트 시작 기준
START_ANGLE = 150

# 최저점 도달 기준
BOTTOM_ANGLE = 110

# 다시 일어서는 기준
RETURN_ANGLE = 160

# 상승 여부 확인을 위한 각도 증가량
RISE_CONFIRM_DEG = 5

# 각도 데이터의 노이즈 완화
SMOOTHING_WINDOW = 5

# 데이터 불러오기

def load_data():

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"무릎 각도 파일을 찾을 수 없습니다.\n"
            f"확인 경로: {INPUT_CSV}"
        )

    df = pd.read_csv(INPUT_CSV)

    required_columns = [
        "frame",
        "timestamp_ms",
        "left_knee_angle"
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"필요한 컬럼이 없습니다: {column}"
            )

    df = df.sort_values("frame").reset_index(drop=True)

    df["left_knee_angle"] = pd.to_numeric(
        df["left_knee_angle"],
        errors="coerce"
    )

    return df

#  무릎 각도 평활화

def smooth_angles(df):

    # 중앙값 필터를 이용해 각도 변화의 노이즈 완화
    df["smoothed_angle"] = (
        df["left_knee_angle"]
        .rolling(
            window=SMOOTHING_WINDOW,
            center=True,
            min_periods=1
        )
        .median()
    )

    return df


# 스쿼트 반복 동작 감지

def detect_squats(df):

    state = "STANDING"

    candidate_id = 0

    min_angle = None
    min_index = None
    start_index = None

    bottom_reached = False

    records = []
    summaries = []

    completed_rep_ids = set()

    for i, row in df.iterrows():

        angle = row["smoothed_angle"]

        # 각도를 계산할 수 없는 프레임
        if pd.isna(angle):

            records.append({
                "frame": row["frame"],
                "timestamp_ms": row["timestamp_ms"],
                "left_knee_angle": row["left_knee_angle"],
                "smoothed_angle": angle,
                "phase": "UNKNOWN",
                "rep_id": candidate_id if state != "STANDING" else 0,
                "rep_completed": False
            })

            continue

        phase = state
        rep_id = candidate_id if state != "STANDING" else 0

        # 상태 1: 서 있는 자세

        if state == "STANDING":

            if angle <= START_ANGLE:

                candidate_id += 1

                start_index = i
                min_angle = angle
                min_index = i

                bottom_reached = False

                state = "DESCENT"
                phase = "DESCENT"
                rep_id = candidate_id

        # 상태2: 하강

        elif state == "DESCENT":

            phase = "DESCENT"
            rep_id = candidate_id

            if angle < min_angle:

                min_angle = angle
                min_index = i

            if angle <= BOTTOM_ANGLE:

                bottom_reached = True

            if (
                bottom_reached
                and angle >= min_angle + RISE_CONFIRM_DEG
            ):

                state = "ASCENT"
                phase = "ASCENT"

        # 상태3: 상승

        elif state == "ASCENT":

            phase = "ASCENT"
            rep_id = candidate_id

            if angle >= RETURN_ANGLE:

                # 최저점 프레임 기록
                records[min_index]["phase"] = "BOTTOM"

                # 완료된 반복 번호 기록
                completed_rep_ids.add(candidate_id)

                summaries.append({
                    "rep_id": candidate_id,
                    "start_frame": df.loc[start_index, "frame"],
                    "bottom_frame": df.loc[min_index, "frame"],
                    "end_frame": row["frame"],
                    "min_knee_angle": min_angle,
                    "start_time_ms": df.loc[start_index, "timestamp_ms"],
                    "bottom_time_ms": df.loc[min_index, "timestamp_ms"],
                    "end_time_ms": row["timestamp_ms"],
                    "duration_ms": (
                        row["timestamp_ms"]
                        - df.loc[start_index, "timestamp_ms"]
                    )
                })

                # 다음 스쿼트를 위한 초기화
                state = "STANDING"

                min_angle = None
                min_index = None
                start_index = None

                bottom_reached = False

                phase = "STANDING"

        # 프레임별 분석 결과 저장
        records.append({
            "frame": row["frame"],
            "timestamp_ms": row["timestamp_ms"],
            "left_knee_angle": row["left_knee_angle"],
            "smoothed_angle": angle,
            "phase": phase,
            "rep_id": rep_id,
            "rep_completed": False
        })

    # 완료된 반복 여부 반영

    frame_results = pd.DataFrame(records)

    frame_results["rep_completed"] = (
        frame_results["rep_id"].isin(completed_rep_ids)
        & (frame_results["rep_id"] != 0)
    )

    # 영상 종료 시 미완료 동작 표시
    if state != "STANDING" and start_index is not None:

        frame_results.loc[
            start_index:,
            "phase"
        ] = "INCOMPLETE"

    return frame_results, pd.DataFrame(summaries)

# 결과 저장 및 출력

def main():

    print("=" * 50)
    print("스쿼트 반복 횟수 자동 분석")
    print("=" * 50)

    print(f"분석 영상 이름: {VIDEO_NAME}")
    print(f"입력 파일: {INPUT_CSV}")

    # 결과 폴더 생성
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 데이터 불러오기
    df = load_data()

    # 각도 평활화
    df = smooth_angles(df)

    # 반복 동작 감지
    frame_results, squat_results = detect_squats(df)

    # 프레임별 결과 저장
    frame_results.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # 반복별 결과 저장
    squat_results.to_csv(
        SUMMARY_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # 최종 결과 출력
    print("\n분석 완료!")
    print(f"전체 프레임: {len(frame_results)}")
    print(f"완료된 스쿼트 횟수: {len(squat_results)}")

    incomplete_count = (
        frame_results["phase"] == "INCOMPLETE"
    ).any()

    if incomplete_count:
        print("영상 마지막에 미완료 동작이 존재합니다.")

    print(f"\n프레임별 결과: {OUTPUT_CSV}")
    print(f"반복별 결과: {SUMMARY_CSV}")

    if not squat_results.empty:

        print("\n반복별 분석 결과:")

        print(
            squat_results.to_string(index=False)
        )


if __name__ == "__main__":
    main()

import cv2
import mediapipe as mp
import csv
import sys
from pathlib import Path

# 프로젝트 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 명령어에서 영상 이름을 전달받음
# 이름을 전달하지 않으면 squat_test 사용
VIDEO_NAME = sys.argv[1] if len(sys.argv) > 1 else "squat_test"

MODEL_PATH = Path(r"C:\squat-analysis\models\pose_landmarker_lite.task")

VIDEO_PATH = BASE_DIR / "videos" / "input" / f"{VIDEO_NAME}.mp4"

OUTPUT_CSV = (
    BASE_DIR / "results" / f"{VIDEO_NAME}_landmarks.csv"
)

OUTPUT_VIDEO = (
    BASE_DIR / "videos" / "output" / f"{VIDEO_NAME}_result.mp4"
)

# MediaPipe 설정
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=RunningMode.VIDEO,
    num_poses=1
)

def main():
    # 영상 파일 확인
    if not VIDEO_PATH.exists():
        print("테스트 영상을 찾을 수 없습니다.")
        print("영상 위치:", VIDEO_PATH)
        return

    # 영상 열기
    cap = cv2.VideoCapture(str(VIDEO_PATH))

    if not cap.isOpened():
        print("영상을 열 수 없습니다.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        fps = 30.0

    # 결과 영상 저장 설정
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(OUTPUT_VIDEO), fourcc, fps, (width, height)
    )

    frame_index = 0
    detected_frames = 0

    # CSV 저장
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow([
            "frame",
            "timestamp_ms",
            "landmark_id",
            "x",
            "y",
            "z",
            "visibility"
        ])

        # MediaPipe 모델 실행
        with PoseLandmarker.create_from_options(options) as landmarker:

            while True:
                success, frame = cap.read()

                if not success:
                    break

                # OpenCV BGR -> RGB
                rgb_frame = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                timestamp_ms = int(frame_index * 1000 / fps)

                # 관절 추정
                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )

                if result.pose_landmarks:
                    detected_frames += 1

                    landmarks = result.pose_landmarks[0]

                    for landmark_id, landmark in enumerate(landmarks):
                        csv_writer.writerow([
                            frame_index,
                            timestamp_ms,
                            landmark_id,
                            landmark.x,
                            landmark.y,
                            landmark.z,
                            landmark.visibility
                        ])

                        # 관절 위치를 영상에 표시
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)

                        if 0 <= x < width and 0 <= y < height:
                            cv2.circle(
                                frame,
                                (x, y),
                                4,
                                (0, 255, 0),
                                -1
                            )

                writer.write(frame)
                frame_index += 1

                if frame_index % 30 == 0:
                    print(f"{frame_index} 프레임 처리 완료")

    cap.release()
    writer.release()

    print("\n분석 완료!")
    print("전체 프레임:", frame_index)
    print("관절 인식 프레임:", detected_frames)
    print("CSV 저장 위치:", OUTPUT_CSV)
    print("결과 영상 위치:", OUTPUT_VIDEO)


if __name__ == "__main__":
    main()

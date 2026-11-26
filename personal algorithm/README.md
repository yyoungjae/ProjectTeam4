# Formfit 개인화 및 휴식 추천 알고리즘 (초기 프로토타입)

이 폴더는 Role-1이 제공한 `combined_features.csv` 구조를 입력으로 사용합니다.

## 구성

- `baseline.py`: 사용자 기준 동작 프로필 생성
- `performance.py`: 기준 대비 반복별 변화 및 세트 내 초반/후반 변화 분석
- `fatigue.py`: 사용자 피로도 입력과 영상 기반 수행 변화 점수 결합
- `rest_recommender.py`: 임시 규칙으로 권장 휴식 시간 계산
- `main.py`: 전체 알고리즘 실행
- `config.py`: 임시 기준값과 가중치 관리
- `io_utils.py`: CSV 로딩 및 컬럼 검증

## 설치

```bash
pip install -r requirements.txt
```

## 실행 예시

아래 예시는 `squat_test_02_combined_features.csv`를 기준 영상으로, `squat_test_03_combined_features.csv`를 현재 분석 영상으로 사용하는 **코드 동작 확인용 예시**입니다.

```bash
python -m formfit_personalization.main \
  --baseline squat_test_02_combined_features.csv \
  --input squat_test_03_combined_features.csv \
  --fatigue 6 \
  --out ./formfit_demo_output
```

Windows PowerShell에서는 한 줄로 실행해도 됩니다.

```powershell
python -m formfit_personalization.main --baseline squat_test_02_combined_features.csv --input squat_test_03_combined_features.csv --fatigue 6 --out .\formfit_demo_output
```

## 입력 데이터

Role-1 CSV의 주요 컬럼을 사용합니다.

- `rep_id`
- `range_of_motion`
- `duration_sec`
- `descent_duration_sec`
- `ascent_duration_sec`
- `mean_torso_angle`
- `bottom_torso_angle`
- `analyzed_frames`

`range_of_motion`은 Role-1 명세에 따라 `start_angle - min_knee_angle`로 취급합니다.

## 알고리즘 개요

1. 기준 영상(들)의 반복 데이터를 모아 특징별 중앙값을 개인 기준으로 계산합니다.
2. 현재 영상의 각 반복을 개인 기준과 비교합니다.
3. ROM 감소, 전체/상승 시간 증가, 최저점 상체 기울기 편차를 임시 가중 점수로 결합합니다.
4. 반복이 4회 이상이면 세트 초반과 후반의 중앙값을 비교해 세트 내 변화 추세를 추가 계산합니다.
5. 사용자 피로도(1~10)가 주어지면 영상 변화 점수와 결합합니다.
6. 0~100 점수를 60~180초의 임시 휴식 시간 범위에 선형 매핑합니다.

## 매우 중요한 제한사항

- 현재 점수는 생리학적 피로도를 직접 측정하지 않습니다. 영상에서 관찰된 움직임 변화와 사용자의 주관적 피로 입력을 조합한 프로토타입 점수입니다.
- 권장 휴식 시간(60~180초), 가중치, 임계값은 확정된 운동 처방이 아니라 개발 초기 테스트용 임시 규칙입니다.
- 기준 영상과 현재 영상은 카메라 위치/각도/거리, 운동 지시, 촬영 환경을 가능한 한 동일하게 유지해야 합니다.
- 기준 반복이 5회 미만이면 기준값 신뢰도가 낮다는 경고를 표시합니다.
- 현재 데이터는 한 명의 촬영 자료로 알려져 있으나, 영상별 촬영 조건이 동일하다는 보장은 없습니다. 서로 다른 영상의 차이를 곧바로 피로나 수행 저하로 해석하지 마세요.
- 실제 사용자에게 권장하기 전, 추가 데이터와 라벨링된 실험을 통해 임계값 및 추천식을 검증해야 합니다.

## 백엔드 연결

웹 API에서 사용하려면 각 단계 함수를 직접 import하여 호출할 수 있습니다.

```python
from formfit_personalization import (
    build_baseline, analyze_repetitions, estimate_fatigue, recommend_rest
)

profile = build_baseline(["calibration.csv"])
rep_df, performance = analyze_repetitions("current_set.csv", profile)
fatigue = estimate_fatigue(performance["performance_change_score"], subjective_fatigue=6)
rest = recommend_rest(fatigue["score"])
```

`profile`, `rep_df`, `performance`, `fatigue`, `rest`를 API 응답 형식에 맞춰 변환하면 됩니다.

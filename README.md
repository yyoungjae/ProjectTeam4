# P-실무 프로잭트 (스쿼트 자세 분석 시스템)
역할 2번(도건우)께서 확인해야 될 내용
작성자: 양영재

사용할 동영상 별 반복별 분석 데이터 파일들이 handoff_to_roleB에 올려뒀습니다.
우선 초기에는 이 파일들을 가지고 진행해주시고 추후에 역할 1번(양영재)가 세부 기준 수정 후 추가 파일들을 제공예정
그리고 데이터 보고서(pdf)에 각 데이터 항목에 대한 정보가 있기 때문에 보고서 내용을 지키면서 프로젝트 진행해주시면 됩니다.

-각 파일 역할
1.pose_test.py 영상 → MediaPipe 랜드마크
2.angle_analysis.py 무릎 각도 계산
3.torso_analysis.py 상체 기울기 계산
4.squat_detection.py 반복 및 구간 검출
5.rep_features.py 무릎 특징 추출
6.rep_torso_features.py 상체 특징 추출
7.combined_features.py 무릎 + 상체 데이터 통합

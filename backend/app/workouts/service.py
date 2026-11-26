"""운동/세트 로직.

세트 분석 흐름 (백그라운드에서 실행):
    status = PROCESSING
    analysis = analyze(video_path)                       # 1번
    verdict  = judge(analysis, baseline)                 # 2번
    rec      = recommend(verdict, baseline, prev_sets, rpe)  # 2번
    결과 저장, status = DONE   (예외 나면 FAILED)
"""

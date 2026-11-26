"""CLI entry point for the Formfit personalization prototype.

Example:
  python main.py --baseline ../squat_test_02_combined_features.csv \
      --input ../squat_test_03_combined_features.csv --fatigue 6
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

from .baseline import build_baseline, save_baseline
from .performance import analyze_repetitions, compare_capture_conditions
from .fatigue import estimate_fatigue
from .rest_recommender import recommend_rest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Formfit personalization prototype")
    parser.add_argument("--baseline", nargs="+", required=True,
                        help="One or more calibration combined_features CSV files")
    parser.add_argument("--input", required=True,
                        help="Current set combined_features CSV file")
    parser.add_argument("--fatigue", type=float, default=None,
                        help="User-entered fatigue rating from 1 to 10")
    parser.add_argument("--out", default="formfit_output",
                        help="Output directory (default: formfit_output)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = build_baseline(args.baseline)
    profile_path = save_baseline(profile, output_dir / "personal_baseline.json")

    per_rep, performance_summary = analyze_repetitions(args.input, profile)
    capture_warnings = compare_capture_conditions(profile, args.input)
    fatigue_result = estimate_fatigue(
        performance_summary["performance_change_score"], args.fatigue
    )
    rest_result = recommend_rest(fatigue_result["score"])

    per_rep_path = output_dir / "rep_performance_analysis.csv"
    per_rep.to_csv(per_rep_path, index=False, encoding="utf-8-sig")

    recommendation_status = (
        "촬영 조건 비교 경고가 있어 영상 기반 개인화 결과를 참고용으로만 사용"
        if capture_warnings else "프로토타입 규칙에 따른 임시 추천"
    )

    report = {
        "recommendation_status": recommendation_status,
        "input_csv": str(Path(args.input)),
        "baseline_profile": str(profile_path),
        "baseline": profile,
        "performance": performance_summary,
        "fatigue": fatigue_result,
        "rest_recommendation": rest_result,
        "capture_warnings": capture_warnings,
    }
    report_path = output_dir / "formfit_analysis_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n========== FORMFIT 분석 결과 ==========")
    print(f"분석 반복 수: {performance_summary['repetitions_analyzed']}회")
    print(f"수행 변화 점수: {performance_summary['performance_change_score']}/100")
    print(f"수행 상태: {performance_summary['performance_status']}")
    trend = performance_summary["within_set_trend"]
    print(f"세트 내 추세 분석: {trend['status']}")
    print(f"피로 관련 점수: {fatigue_result['score']}/100")
    print(f"권장 휴식 시간: {rest_result['recommended_rest_sec']}초")
    print(f"추천 설명: {rest_result['explanation']}")
    print(f"추천 상태: {recommendation_status}")

    if profile.get("warnings"):
        print("\n[기준값 경고]")
        for warning in profile["warnings"]:
            print(f"- {warning}")
    if capture_warnings:
        print("\n[촬영 조건 확인 경고]")
        for warning in capture_warnings:
            print(f"- {warning}")

    print("\n[저장 파일]")
    print(f"- 개인 기준값: {profile_path}")
    print(f"- 반복별 분석: {per_rep_path}")
    print(f"- 전체 리포트: {report_path}")
    print("\n주의: 현재 점수와 휴식 시간은 초기 프로토타입용 임시 규칙입니다.")


if __name__ == "__main__":
    main()

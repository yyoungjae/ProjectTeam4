"""Compare repetitions with a personal reference and estimate performance drift."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .config import (
    BASELINE_DEVIATION_WEIGHT,
    DURATION_INCREASE_FOR_MAX_SCORE_PCT,
    MIN_REPS_FOR_TREND,
    PERFORMANCE_WEIGHTS,
    ROM_DROP_FOR_MAX_SCORE_PCT,
    TORSO_DEVIATION_FOR_MAX_SCORE_DEG,
    TREND_WEIGHTS,
    WITHIN_SET_TREND_WEIGHT,
    ASCENT_INCREASE_FOR_MAX_SCORE_PCT,
    ROM_SETUP_DIFFERENCE_WARNING_PCT,
    TORSO_SETUP_DIFFERENCE_WARNING_DEG,
)
from .io_utils import load_feature_csv


def _clip_score(value: float, scale: float) -> float:
    if not np.isfinite(value) or scale <= 0:
        return 0.0
    return float(np.clip(value / scale * 100.0, 0.0, 100.0))


def _baseline_median(profile: dict, feature: str) -> float | None:
    item = profile.get("features", {}).get(feature, {})
    value = item.get("median")
    return float(value) if value is not None and np.isfinite(float(value)) else None


def _relative_increase(current: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return max(0.0, (current - baseline) / baseline * 100.0)


def _relative_drop(current: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return max(0.0, (baseline - current) / baseline * 100.0)


def _score_status(score: float) -> str:
    if score < 20:
        return "기준과 유사"
    if score < 40:
        return "일부 변화"
    if score < 65:
        return "변화 관찰 필요"
    return "큰 변화 관찰"


def analyze_repetitions(csv_path: str | Path, profile: dict) -> tuple[pd.DataFrame, dict]:
    """Return per-rep baseline deviations and a within-set early/late trend."""
    df = load_feature_csv(csv_path)
    required_baselines = [
        "range_of_motion", "duration_sec", "ascent_duration_sec",
        "bottom_torso_angle",
    ]
    missing_baselines = [f for f in required_baselines if _baseline_median(profile, f) is None]
    if missing_baselines:
        raise ValueError(f"Baseline is missing required feature medians: {missing_baselines}")

    base_rom = _baseline_median(profile, "range_of_motion")
    base_duration = _baseline_median(profile, "duration_sec")
    base_ascent = _baseline_median(profile, "ascent_duration_sec")
    base_torso = _baseline_median(profile, "bottom_torso_angle")

    rows: list[dict] = []
    for _, row in df.iterrows():
        rom = float(row["range_of_motion"])
        duration = float(row["duration_sec"])
        ascent = float(row["ascent_duration_sec"])
        torso = float(row["bottom_torso_angle"])

        rom_drop_pct = _relative_drop(rom, base_rom)
        duration_increase_pct = _relative_increase(duration, base_duration)
        ascent_increase_pct = _relative_increase(ascent, base_ascent)
        torso_deviation_deg = abs(torso - base_torso)

        component_scores = {
            "rom_drop_score": _clip_score(rom_drop_pct, ROM_DROP_FOR_MAX_SCORE_PCT),
            "duration_increase_score": _clip_score(duration_increase_pct, DURATION_INCREASE_FOR_MAX_SCORE_PCT),
            "ascent_increase_score": _clip_score(ascent_increase_pct, ASCENT_INCREASE_FOR_MAX_SCORE_PCT),
            "torso_deviation_score": _clip_score(torso_deviation_deg, TORSO_DEVIATION_FOR_MAX_SCORE_DEG),
        }
        score = (
            component_scores["rom_drop_score"] * PERFORMANCE_WEIGHTS["rom_drop"]
            + component_scores["duration_increase_score"] * PERFORMANCE_WEIGHTS["duration_increase"]
            + component_scores["ascent_increase_score"] * PERFORMANCE_WEIGHTS["ascent_increase"]
            + component_scores["torso_deviation_score"] * PERFORMANCE_WEIGHTS["torso_deviation"]
        )

        rows.append({
            "rep_id": int(row["rep_id"]),
            "range_of_motion": rom,
            "duration_sec": duration,
            "ascent_duration_sec": ascent,
            "bottom_torso_angle": torso,
            "rom_drop_pct_vs_baseline": round(rom_drop_pct, 2),
            "duration_increase_pct_vs_baseline": round(duration_increase_pct, 2),
            "ascent_increase_pct_vs_baseline": round(ascent_increase_pct, 2),
            "bottom_torso_deviation_deg": round(torso_deviation_deg, 2),
            **{key: round(value, 2) for key, value in component_scores.items()},
            "performance_change_score": round(float(score), 2),
            "status": _score_status(float(score)),
        })

    per_rep = pd.DataFrame(rows).sort_values("rep_id").reset_index(drop=True)

    # Within-set early-versus-late comparison. This is a movement-drift signal,
    # not a direct measurement of physiological fatigue.
    trend: dict = {
        "available": False,
        "repetitions": int(len(df)),
        "score": None,
        "status": "반복 수 부족으로 세트 내 추세를 계산하지 않음",
    }
    if len(df) >= MIN_REPS_FOR_TREND:
        ordered = df.sort_values("rep_id").reset_index(drop=True)
        split = len(ordered) // 2
        early = ordered.iloc[:split]
        late = ordered.iloc[split:]

        early_rom = float(early["range_of_motion"].median())
        late_rom = float(late["range_of_motion"].median())
        early_duration = float(early["duration_sec"].median())
        late_duration = float(late["duration_sec"].median())
        early_ascent = float(early["ascent_duration_sec"].median())
        late_ascent = float(late["ascent_duration_sec"].median())
        early_torso = float(early["bottom_torso_angle"].median())
        late_torso = float(late["bottom_torso_angle"].median())

        rom_drop = _relative_drop(late_rom, early_rom)
        duration_up = _relative_increase(late_duration, early_duration)
        ascent_up = _relative_increase(late_ascent, early_ascent)
        torso_change = abs(late_torso - early_torso)

        trend_components = {
            "rom_drop_score": _clip_score(rom_drop, ROM_DROP_FOR_MAX_SCORE_PCT),
            "duration_increase_score": _clip_score(duration_up, DURATION_INCREASE_FOR_MAX_SCORE_PCT),
            "ascent_increase_score": _clip_score(ascent_up, ASCENT_INCREASE_FOR_MAX_SCORE_PCT),
            "torso_change_score": _clip_score(torso_change, TORSO_DEVIATION_FOR_MAX_SCORE_DEG),
        }
        trend_score = (
            trend_components["rom_drop_score"] * TREND_WEIGHTS["rom_drop"]
            + trend_components["duration_increase_score"] * TREND_WEIGHTS["duration_increase"]
            + trend_components["ascent_increase_score"] * TREND_WEIGHTS["ascent_increase"]
            + trend_components["torso_change_score"] * TREND_WEIGHTS["torso_change"]
        )
        trend_status = _score_status(float(trend_score))
        trend = {
            "available": True,
            "repetitions": int(len(df)),
            "early_reps": [int(x) for x in early["rep_id"].tolist()],
            "late_reps": [int(x) for x in late["rep_id"].tolist()],
            "early_median": {
                "range_of_motion": round(early_rom, 2),
                "duration_sec": round(early_duration, 2),
                "ascent_duration_sec": round(early_ascent, 2),
                "bottom_torso_angle": round(early_torso, 2),
            },
            "late_median": {
                "range_of_motion": round(late_rom, 2),
                "duration_sec": round(late_duration, 2),
                "ascent_duration_sec": round(late_ascent, 2),
                "bottom_torso_angle": round(late_torso, 2),
            },
            "changes": {
                "rom_drop_pct": round(rom_drop, 2),
                "duration_increase_pct": round(duration_up, 2),
                "ascent_increase_pct": round(ascent_up, 2),
                "bottom_torso_change_deg": round(torso_change, 2),
            },
            "components": {k: round(v, 2) for k, v in trend_components.items()},
            "score": round(float(trend_score), 2),
            "status": trend_status,
        }

    baseline_score = float(per_rep["performance_change_score"].median())
    if trend["available"]:
        overall_score = (
            baseline_score * BASELINE_DEVIATION_WEIGHT
            + float(trend["score"]) * WITHIN_SET_TREND_WEIGHT
        )
    else:
        overall_score = baseline_score

    summary = {
        "repetitions_analyzed": int(len(per_rep)),
        "baseline_deviation_score": round(baseline_score, 2),
        "within_set_trend": trend,
        "performance_change_score": round(overall_score, 2),
        "performance_status": _score_status(overall_score),
        "interpretation_note": (
            "This score represents changes in measured movement features. "
            "It is not a direct or validated measurement of physiological fatigue."
        ),
    }
    return per_rep, summary


def compare_capture_conditions(profile: dict, current_csv: str | Path) -> list[str]:
    """Flag large baseline/current shifts that may reflect capture setup changes."""
    df = load_feature_csv(current_csv)
    warnings: list[str] = []
    base_rom = _baseline_median(profile, "range_of_motion")
    base_torso = _baseline_median(profile, "bottom_torso_angle")
    current_rom = float(df["range_of_motion"].median())
    current_torso = float(df["bottom_torso_angle"].median())

    if base_rom and base_rom > 0:
        diff = abs(current_rom - base_rom) / base_rom * 100.0
        if diff > ROM_SETUP_DIFFERENCE_WARNING_PCT:
            warnings.append(
                f"Current median ROM differs from baseline by {diff:.1f}%. "
                "Check squat depth, camera view, and recording conditions before interpreting this as performance decline."
            )
    if base_torso is not None:
        diff = abs(current_torso - base_torso)
        if diff > TORSO_SETUP_DIFFERENCE_WARNING_DEG:
            warnings.append(
                f"Current median bottom torso angle differs from baseline by {diff:.1f} degrees. "
                "Camera position/viewpoint may differ; torso-angle comparison may be unreliable."
            )
    return warnings

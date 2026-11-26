"""Build and save an individual's provisional reference profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd

from .config import BASELINE_FEATURES, MIN_BASELINE_REPS
from .io_utils import load_many_feature_csv


def _finite_values(series: pd.Series) -> list[float]:
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    return values[np.isfinite(values)].tolist()


def build_baseline(csv_paths: Iterable[str | Path]) -> dict:
    """Use the median of the supplied calibration repetitions as a baseline.

    Important: callers should only combine videos recorded with comparable
    camera position, distance, view angle, and exercise instructions.
    """
    df = load_many_feature_csv(csv_paths)
    metrics: dict[str, dict[str, float | int | None]] = {}

    for feature in BASELINE_FEATURES:
        values = _finite_values(df[feature])
        if not values:
            metrics[feature] = {"median": None, "mean": None, "std": None, "count": 0}
            continue
        metrics[feature] = {
            "median": round(float(np.median(values)), 4),
            "mean": round(float(np.mean(values)), 4),
            "std": round(float(np.std(values, ddof=1)), 4) if len(values) > 1 else 0.0,
            "count": len(values),
        }

    warnings: list[str] = []
    if len(df) < MIN_BASELINE_REPS:
        warnings.append(
            f"Baseline has only {len(df)} repetitions; at least {MIN_BASELINE_REPS} are preferred. "
            "Treat this profile as provisional."
        )
    if df["analyzed_frames"].notna().any():
        med_frames = float(df["analyzed_frames"].median())
        if med_frames < 10:
            warnings.append(
                "Median analyzed_frames is low. Check landmark visibility and torso-feature reliability."
            )

    return {
        "profile_version": 1,
        "profile_type": "provisional_personal_reference",
        "baseline_reps": int(len(df)),
        "source_files": sorted(df["source_file"].unique().tolist()),
        "features": metrics,
        "warnings": warnings,
        "notes": [
            "This profile represents the user's observed reference movement, not a medically validated ideal posture.",
            "Only combine recordings made under comparable camera and exercise conditions.",
            "The input range_of_motion follows Role-1's definition: start_angle - min_knee_angle.",
        ],
    }


def save_baseline(profile: dict, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_baseline(path: str | Path) -> dict:
    profile_path = Path(path)
    if not profile_path.exists():
        raise FileNotFoundError(f"Baseline profile not found: {profile_path}")
    return json.loads(profile_path.read_text(encoding="utf-8"))

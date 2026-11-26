"""Combine subjective fatigue input with measured movement-change signals."""
from __future__ import annotations
import math
from .config import SUBJECTIVE_FATIGUE_WEIGHT, VIDEO_PERFORMANCE_WEIGHT


def estimate_fatigue(performance_change_score: float, subjective_fatigue: int | float | None) -> dict:
    """Return a provisional 0..100 fatigue-related score.

    subjective_fatigue uses a 1..10 user-entered scale. The video component is
    a movement-change score, not a direct physiological fatigue measurement.
    """
    performance = max(0.0, min(100.0, float(performance_change_score)))
    if subjective_fatigue is None:
        score = performance
        return {
            "score": round(score, 2),
            "subjective_input": None,
            "subjective_score": None,
            "performance_change_score": round(performance, 2),
            "method": "video_only_provisional",
            "note": "No subjective fatigue rating was supplied; score uses movement-change signals only.",
        }

    rating = float(subjective_fatigue)
    if not math.isfinite(rating) or not 1 <= rating <= 10:
        raise ValueError("subjective_fatigue must be between 1 and 10.")
    subjective_score = (rating - 1.0) / 9.0 * 100.0
    score = (
        subjective_score * SUBJECTIVE_FATIGUE_WEIGHT
        + performance * VIDEO_PERFORMANCE_WEIGHT
    )
    return {
        "score": round(score, 2),
        "subjective_input": rating,
        "subjective_score": round(subjective_score, 2),
        "performance_change_score": round(performance, 2),
        "method": "subjective_plus_video_provisional",
        "note": "This is a prototype decision score, not a medical or physiological fatigue measurement.",
    }

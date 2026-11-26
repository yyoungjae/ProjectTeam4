"""Temporary, configurable parameters for the Formfit personalization prototype.

These values are engineering placeholders for early integration tests. They are
not clinically validated exercise or recovery recommendations.
"""

REQUIRED_COLUMNS = [
    "rep_id",
    "range_of_motion",
    "duration_sec",
    "descent_duration_sec",
    "ascent_duration_sec",
    "mean_torso_angle",
    "bottom_torso_angle",
    "analyzed_frames",
]

BASELINE_FEATURES = [
    "range_of_motion",
    "duration_sec",
    "descent_duration_sec",
    "ascent_duration_sec",
    "mean_torso_angle",
    "bottom_torso_angle",
]

# Baseline statistics are more stable with more repetitions. The application
# still runs below this threshold, but marks the result as provisional.
MIN_BASELINE_REPS = 5

# A within-set early-vs-late trend is only reported with enough repetitions.
MIN_REPS_FOR_TREND = 4

# Thresholds used to map feature changes onto 0..100 sub-scores.
# These are initial heuristics and should be tuned with labelled test sessions.
ROM_DROP_FOR_MAX_SCORE_PCT = 30.0
DURATION_INCREASE_FOR_MAX_SCORE_PCT = 50.0
ASCENT_INCREASE_FOR_MAX_SCORE_PCT = 50.0
TORSO_DEVIATION_FOR_MAX_SCORE_DEG = 15.0

# Performance-change score weights. They sum to 1.
PERFORMANCE_WEIGHTS = {
    "rom_drop": 0.35,
    "duration_increase": 0.25,
    "ascent_increase": 0.25,
    "torso_deviation": 0.15,
}

# Within-set trend weights. They sum to 1.
TREND_WEIGHTS = {
    "rom_drop": 0.40,
    "duration_increase": 0.30,
    "ascent_increase": 0.20,
    "torso_change": 0.10,
}

# Overall performance score combines baseline deviation and within-set drift.
BASELINE_DEVIATION_WEIGHT = 0.60
WITHIN_SET_TREND_WEIGHT = 0.40

# Subjective fatigue rating is expected on a 1..10 scale.
SUBJECTIVE_FATIGUE_WEIGHT = 0.60
VIDEO_PERFORMANCE_WEIGHT = 0.40

# Initial rest recommendation range. This is only a configurable demo rule.
MIN_REST_SEC = 60
MAX_REST_SEC = 180

# Large baseline/current differences may reflect camera setup or movement
# differences, not fatigue. The system warns rather than silently interpreting.
ROM_SETUP_DIFFERENCE_WARNING_PCT = 30.0
TORSO_SETUP_DIFFERENCE_WARNING_DEG = 12.0

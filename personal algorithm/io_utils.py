"""CSV loading and validation helpers for Formfit."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd

from .config import REQUIRED_COLUMNS


def load_feature_csv(path: str | Path) -> pd.DataFrame:
    """Load one Role-1 combined_features CSV and validate its schema."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"{csv_path.name}: required columns are missing: {', '.join(missing)}"
        )
    if df.empty:
        raise ValueError(f"{csv_path.name}: CSV contains no repetitions.")

    # Convert expected numeric columns while preserving the original CSV.
    numeric_cols = [c for c in REQUIRED_COLUMNS if c != "rep_id"]
    numeric_cols += ["rep_id"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["rep_id", "range_of_motion", "duration_sec"])
    removed = before - len(df)
    if df.empty:
        raise ValueError(f"{csv_path.name}: no usable repetition rows remain.")

    df["rep_id"] = df["rep_id"].astype(int)
    df = df.sort_values("rep_id").reset_index(drop=True)
    df.attrs["source_file"] = csv_path.name
    df.attrs["dropped_rows"] = removed
    return df


def load_many_feature_csv(paths: Iterable[str | Path]) -> pd.DataFrame:
    """Load multiple baseline CSVs and keep each source name for traceability."""
    frames: list[pd.DataFrame] = []
    for path in paths:
        df = load_feature_csv(path)
        df = df.copy()
        df["source_file"] = Path(path).name
        frames.append(df)

    if not frames:
        raise ValueError("At least one baseline CSV path is required.")

    combined = pd.concat(frames, ignore_index=True)
    combined["baseline_row_id"] = range(1, len(combined) + 1)
    return combined

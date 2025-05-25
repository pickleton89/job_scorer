"""
Scoring Engine Module
====================

This module contains the core scoring logic for the job_scorer project:
- emphasis_modifier: Detects emphasis in requirement text
- CoreGapSkill: Dataclass for representing core gap skills
- compute_scores: Main scoring function

All scoring-related logic is isolated here for maintainability and testability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict

import pandas as pd

# Local imports
from .config import SCORING_CONFIG, CLASS_WT, ClassificationConfig, ScoringConfig

if TYPE_CHECKING:
    from pandas import DataFrame

# --- Emphasis Modifier ---
def emphasis_modifier(text: str, config: ScoringConfig = SCORING_CONFIG) -> float:
    """Determine the emphasis modifier for a requirement text."""
    if not isinstance(text, str):
        return 0.0
    text_lower = text.lower()
    high = any(k in text_lower for k in config.emphasis_indicators.high_emphasis)
    low = any(k in text_lower for k in config.emphasis_indicators.low_emphasis)
    if high:
        return config.emphasis_modifier_high
    if low:
        return config.emphasis_modifier_low
    return 0.0

# --- Core Gap Skill Dataclass ---
@dataclass(frozen=True, order=True)
class CoreGapSkill:
    name: str
    classification: str
    self_score: int
    threshold: int

    @property
    def severity(self) -> str:
        """Returns severity level for this core gap skill."""
        if self.classification == "Essential":
            if self.self_score <= 1:
                return "High"
            elif self.self_score == 2:
                return "Medium"
            else:
                return "Low"
        elif self.classification == "Important":
            if self.self_score == 0:
                return "Medium"
            else:
                return "Low"
        return "Low"

# --- Scoring Result Type ---
class ScoreResult(TypedDict):
    core_gap: bool
    core_gap_skills: list[CoreGapSkill]
    actual_points: float
    max_points: float
    pct_fit: float

# --- Compute Scores ---
def compute_scores(df: pd.DataFrame) -> ScoreResult:
    """Compute core-gap flag, points and %-fit using the scoring system."""
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    req_col = "Requirement" if "Requirement" in df.columns else ("Skill" if "Skill" in df.columns else None)
    if not {"Classification", "SelfScore"}.issubset(df.columns) or req_col is None:
        raise ValueError("Missing required columns")

    # Identify core gap skills
    core_gap_skills: list[CoreGapSkill] = []
    for _, row in df.iterrows():
        classification = row["Classification"]
        self_score = row["SelfScore"]
        threshold = ClassificationConfig.get_gap_thresholds().get(classification, 0)
        if classification in {"Essential", "Important"} and self_score <= threshold:
            core_gap_skills.append(CoreGapSkill(
                name=row[req_col],
                classification=classification,
                self_score=self_score,
                threshold=threshold,
            ))
    # Sort core_gap_skills for deterministic output (classification, self_score, name)
    core_gap_skills = sorted(core_gap_skills, key=lambda g: (g.classification, g.self_score, g.name))
    core_gap = bool(core_gap_skills)

    # Calculate raw and normalized scores (per-row normalization)
    theoretical_max = SCORING_CONFIG.theoretical_max_raw_score_per_row
    df["RowScoreRaw"] = (
        df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]
    )
    df["RowScoreNorm"] = df["RowScoreRaw"] / theoretical_max
    actual_points = round(float(df["RowScoreNorm"].sum()), 2)
    max_points = round(float(len(df)), 2)
    pct_fit = round(actual_points / max_points, 2) if max_points else 0.0

    return ScoreResult(
        core_gap=core_gap,
        core_gap_skills=core_gap_skills,
        actual_points=actual_points,
        max_points=max_points,
        pct_fit=pct_fit,
    )

"""
Scoring Engine Module
====================

This module contains the core scoring logic for the job_scorer project, providing
the algorithms and data structures needed to evaluate job skill matrices.

Key Components:
- `CoreGapSkill`: Dataclass representing a skill with a core gap
- `compute_scores()`: Main function that calculates scores from a skill matrix
- `emphasis_modifier()`: Determines emphasis level based on requirement text
- `ScoreResult`: TypedDict containing scoring results

Usage Example:
    ```python
    import pandas as pd
    from scoring.scoring_engine import compute_scores
    from scoring.data_loader import load_matrix

    # Load and validate skill matrix
    df = load_matrix("skills.csv")

    # Calculate scores
    result = compute_scores(df)

    # Access results
    print(f"Core gap present: {result.core_gap}")
    print(f"Percentage fit: {result.pct_fit:.1%}")

    # Check core gap skills
    for skill in result.core_gap_skills:
        print(f"{skill.name}: {skill.severity} severity")
    ```

Note: This module is designed to work with data loaded by `data_loader.py` and is
typically used through the CLI interface in `cli.py`.

All scoring-related logic is isolated here for maintainability and testability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypedDict

from pandas import DataFrame

# Local imports
from .config import (
    SCORING_CONFIG,
    ClassificationConfig,
    ClassificationName,
    ScoringConfig,
)

if TYPE_CHECKING:
    from pandas import DataFrame

    from .config import ClassificationName

# Type for severity levels
SeverityLevel: TypeAlias = Literal["High", "Medium", "Low"]

# Type for core gap skill attributes
CoreGapSkillDict: TypeAlias = dict[
    str, str | int | float
]  # name, classification, self_score, threshold


def emphasis_modifier(text: str | Any, config: ScoringConfig = SCORING_CONFIG) -> float:
    """Determine the emphasis modifier for a requirement text.

    Args:
        text: The requirement text to analyze. Can be any type, but only strings are processed.
              Non-string inputs will be treated as having no emphasis.
        config: Scoring configuration containing emphasis settings.

    Returns:
        float: The emphasis modifier to apply to the score:
            - config.emphasis_modifier_high for high emphasis
            - config.emphasis_modifier_low for low emphasis
            - 0.0 for neutral or invalid input
    """
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
    """Represents a skill that has a core gap between requirement and self-assessment.

    Attributes:
        name: The name of the skill (must be non-empty string)
        classification: The classification of the skill (Essential/Important/Desirable/Implicit)
        self_score: The self-assessed score (0-5)
        threshold: The minimum required score (non-negative integer)
    """

    name: str
    classification: ClassificationName
    self_score: int
    threshold: int

    def __post_init__(self) -> None:
        """Validate the CoreGapSkill attributes after initialization."""
        # Validate name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Skill name must be a non-empty string")

        # Validate classification
        valid_classifications = ["Essential", "Important", "Desirable", "Implicit"]
        if self.classification not in valid_classifications:
            raise ValueError(
                f"Invalid classification: {self.classification}. "
                f"Must be one of: {', '.join(valid_classifications)}"
            )

        # Validate self_score
        if not isinstance(self.self_score, int) or not (0 <= self.self_score <= 5):
            raise ValueError("Self score must be an integer between 0 and 5")

        # Validate threshold
        if not isinstance(self.threshold, int) or self.threshold < 0:
            raise ValueError("Threshold must be a non-negative integer")

    @property
    def severity(self) -> SeverityLevel:
        """Determine the severity level for this core gap skill.

        Returns:
            SeverityLevel: The severity level based on classification and self score:
                - 'High' for Essential skills with score <= 1
                - 'Medium' for Essential skills with score = 2 or Important skills with score = 0
                - 'Low' for all other cases
        """
        if self.classification == "Essential":
            if self.self_score <= 1:
                return "High"
            if self.self_score == 2:
                return "Medium"
            return "Low"
        if self.classification == "Important" and self.self_score == 0:
            return "Medium"
        return "Low"


class ScoreResult(TypedDict):
    """Typed dictionary representing the result of the scoring calculation.

    Attributes:
        core_gap: Boolean indicating if any core gaps were found
        core_gap_skills: List of CoreGapSkill objects representing skills with gaps
        actual_points: Total points achieved (normalized)
        max_points: Maximum possible points (normalized)
        pct_fit: Percentage fit (actual_points / max_points)
    """

    core_gap: bool
    core_gap_skills: list[CoreGapSkill]
    actual_points: float
    max_points: float
    pct_fit: float


# --- Compute Scores ---
def compute_scores(df: DataFrame) -> ScoreResult:
    """Compute core-gap flag, points and %-fit using the scoring system.

    Args:
        df: Input DataFrame containing skill matrix data with required columns:
            - 'Classification': Skill classification (Essential/Important/Desirable/Implicit)
            - 'SelfScore': Self-assessment score (0-5)
            - Either 'Requirement' or 'Skill' column for skill names
            - 'ClassWt': Classification weight
            - 'EmphMod': Emphasis modifier

    Returns:
        ScoreResult: Dictionary containing scoring results with core gap info and metrics

    Raises:
        TypeError: If input is not a pandas DataFrame
        ValueError: If required columns are missing or data is invalid
    """
    # Validate input
    if not isinstance(df, DataFrame):
        raise TypeError("Expected pandas DataFrame")

    # Determine the requirement/skill column name
    req_col = None
    for col in ["Requirement", "Skill"]:
        if col in df.columns:
            req_col = col
            break

    if req_col is None or not {"Classification", "SelfScore", "ClassWt", "EmphMod"}.issubset(
        df.columns
    ):
        raise ValueError(
            "Missing required columns. Need: Classification, SelfScore, ClassWt, EmphMod, and either Requirement or Skill"
        )

    # Identify core gap skills
    core_gap_skills: list[CoreGapSkill] = []
    gap_thresholds = ClassificationConfig.get_gap_thresholds()

    for _, row in df.iterrows():
        try:
            classification: ClassificationName = row["Classification"]
            self_score: int = int(row["SelfScore"])

            # Skip if not Essential or Important
            if classification not in ("Essential", "Important"):
                continue

            threshold = gap_thresholds.get(classification, 0)

            if self_score <= threshold:
                core_gap_skills.append(
                    CoreGapSkill(
                        name=str(row[req_col]),
                        classification=classification,
                        self_score=self_score,
                        threshold=threshold,
                    )
                )
        except (ValueError, KeyError) as e:
            # Log warning but continue processing other rows
            skill_name = str(row.get(req_col, "Unknown"))
            print(f"Warning: Invalid data for skill '{skill_name}': {e}")
            continue

    # Sort core_gap_skills for deterministic output (classification, self_score, name)
    core_gap_skills = sorted(
        core_gap_skills, key=lambda g: (g.classification, g.self_score, g.name)
    )
    core_gap = bool(core_gap_skills)

    # Calculate raw and normalized scores (per-row normalization)
    try:
        theoretical_max = SCORING_CONFIG.theoretical_max_raw_score_per_row

        # Calculate scores with type safety
        df["RowScoreRaw"] = df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]
        df["RowScoreNorm"] = df["RowScoreRaw"] / theoretical_max

        # Calculate final metrics with proper type conversion and rounding
        actual_points = round(float(df["RowScoreNorm"].sum()), 2)
        max_points = round(float(len(df)), 2)
        pct_fit = round(actual_points / max_points, 2) if max_points else 0.0

    except (KeyError, TypeError) as e:
        # Handle potential missing columns or type mismatches
        raise ValueError(
            f"Error calculating scores. Required columns or valid data missing: {e}"
        ) from e

    return ScoreResult(
        core_gap=core_gap,
        core_gap_skills=core_gap_skills,
        actual_points=actual_points,
        max_points=max_points,
        pct_fit=pct_fit,
    )

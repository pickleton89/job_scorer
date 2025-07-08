"""
Scoring Engine Module
====================

This module contains the core scoring logic for the job_scorer project, providing
the algorithms and data structures needed to evaluate job skill matrices.

Key Components:
- `CoreGapSkill`: Dataclass representing a skill with a core gap
- `compute_scores()`: Main function that calculates scores from a skill matrix
- `compute_scores_enhanced()`: Enhanced scoring with strategic positioning features
- `emphasis_modifier()`: Determines emphasis level based on requirement text
- `ScoreResult`: TypedDict containing scoring results

Enhancement Functions:
- `classify_requirement_type()`: Classifies requirements as executive/IC/hybrid
- `dual_track_modifier()`: Calculates dual-track scoring adjustments
- `categorize_skill()`: Categorizes skills by type (leadership, technical, etc.)
- `experience_level_modifier()`: Applies experience-level calibration
- `assess_cross_functional_complexity()`: Evaluates cross-functional complexity
- `cross_functional_modifier()`: Calculates cross-functional bonuses
- `get_role_weights()`: Gets role-specific weight adjustments
- `matches_proven_strength()`: Checks for proven strength matches

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
from typing import TYPE_CHECKING, Literal, TypeAlias, TypedDict

from pandas import DataFrame

# Local imports
from .config import (
    SCORING_CONFIG,
    DUAL_TRACK_CONFIG,
    EXPERIENCE_CONFIG,
    CROSS_FUNCTIONAL_CONFIG,
    ROLE_LEVEL_CONFIG,
    ClassificationConfig,
    ClassificationName,
    ScoringConfig,
    DualTrackConfig,
    ExperienceLevelConfig,
    CrossFunctionalConfig,
    RoleLevelConfig,
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


def emphasis_modifier(
    text: str | object,
    config: ScoringConfig = SCORING_CONFIG
) -> float:
    """Determine the emphasis modifier for a requirement text.

    Args:
        text: The requirement text to analyze. Only string values will be processed.
              Non-string inputs will be treated as having no emphasis.
        config: Scoring configuration containing emphasis settings.

    Returns:
        The emphasis modifier to apply to the score:
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


class ScoreResult(TypedDict, total=False):
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


# --- Enhancement Modifier Functions ---

def classify_requirement_type(
    text: str,
    config: DualTrackConfig = DUAL_TRACK_CONFIG
) -> Literal["executive", "ic", "hybrid"]:
    """Classify a requirement as executive-focused, IC-focused, or hybrid.
    
    Args:
        text: The requirement text to analyze
        config: Dual-track configuration containing indicator keywords
        
    Returns:
        Classification of the requirement type
    """
    text_lower = text.lower()
    
    exec_count = sum(1 for ind in config.executive_indicators if ind in text_lower)
    ic_count = sum(1 for ind in config.ic_indicators if ind in text_lower)
    
    if exec_count > ic_count * 1.5:
        return "executive"
    elif ic_count > exec_count * 1.5:
        return "ic"
    else:
        return "hybrid"


def dual_track_modifier(
    requirement_type: str,
    target_role_type: str,
    config: DualTrackConfig = DUAL_TRACK_CONFIG
) -> float:
    """Calculate scoring modifier based on requirement and role alignment.
    
    Args:
        requirement_type: Type of requirement (executive/ic/hybrid)
        target_role_type: Target role type (executive/ic)
        config: Dual-track configuration
        
    Returns:
        Scoring modifier to apply
    """
    if requirement_type == "hybrid":
        return config.aligned_multiplier
    
    if requirement_type == "ic" and target_role_type == "executive":
        return config.ic_for_executive_multiplier
    elif requirement_type == "executive" and target_role_type == "ic":
        return config.executive_for_ic_multiplier
    else:
        return config.aligned_multiplier


def categorize_skill(
    skill_text: str,
    config: ExperienceLevelConfig = EXPERIENCE_CONFIG
) -> str | None:
    """Categorize a skill based on keyword detection.
    
    Args:
        skill_text: The skill description text
        config: Experience level configuration
        
    Returns:
        Skill category name or None if no match found
    """
    skill_lower = skill_text.lower()
    
    for category, keywords in config.skill_categories.items():
        if any(keyword in skill_lower for keyword in keywords):
            return category
    
    return None


def experience_level_modifier(
    skill_category: str | None,
    self_score: int,
    years_experience: int,
    config: ExperienceLevelConfig = EXPERIENCE_CONFIG
) -> float:
    """Calculate experience-level appropriate score modifier.
    
    Args:
        skill_category: Category of the skill
        self_score: Self-assessed score for the skill
        years_experience: Years of professional experience
        config: Experience level configuration
        
    Returns:
        Scoring modifier to apply
    """
    if skill_category is None or years_experience < 15:
        return 1.0
    
    # Get baseline for this skill category
    baseline = getattr(config.senior_executive_baselines, skill_category, 0)
    
    if self_score < baseline:
        # Apply penalty for below-baseline scores
        return config.below_baseline_penalty
    elif self_score > baseline:
        # Apply bonus for exceeding baseline
        return 1.0 + (self_score - baseline) * config.above_baseline_bonus_rate
    else:
        return 1.0


def assess_cross_functional_complexity(
    text: str,
    config: CrossFunctionalConfig = CROSS_FUNCTIONAL_CONFIG
) -> tuple[str, int]:
    """Assess the cross-functional complexity of a requirement.
    
    Args:
        text: The requirement text to analyze
        config: Cross-functional configuration
        
    Returns:
        Tuple of (complexity_level, indicator_count)
    """
    text_lower = text.lower()
    
    # Count indicators from each category
    indicator_count = 0
    for indicator_set in [
        config.collaboration_indicators,
        config.domain_bridging_indicators,
        config.translation_indicators,
        config.integration_indicators
    ]:
        if any(ind in text_lower for ind in indicator_set):
            indicator_count += 1
    
    # Determine complexity level
    if indicator_count >= config.high_complexity_threshold:
        return "high", indicator_count
    elif indicator_count >= config.medium_complexity_threshold:
        return "medium", indicator_count
    else:
        return "low", indicator_count


def cross_functional_modifier(
    complexity: str,
    matches_proven_strength: bool,
    is_executive_role: bool,
    config: CrossFunctionalConfig = CROSS_FUNCTIONAL_CONFIG
) -> float:
    """Calculate cross-functional leadership scoring modifier.
    
    Args:
        complexity: Complexity level (high/medium/low)
        matches_proven_strength: Whether this matches a proven strength
        is_executive_role: Whether target role is executive
        config: Cross-functional configuration
        
    Returns:
        Scoring modifier to apply
    """
    base_multiplier = 1.0
    
    if complexity == "high":
        base_multiplier = config.high_complexity_multiplier
    elif complexity == "medium":
        base_multiplier = config.medium_complexity_multiplier
    
    # Add bonuses
    if matches_proven_strength:
        base_multiplier += config.proven_strength_bonus
    if is_executive_role:
        base_multiplier += config.executive_role_bonus
    
    return base_multiplier


def get_role_weights(
    target_role_level: str,
    config: RoleLevelConfig = ROLE_LEVEL_CONFIG
) -> RoleLevelConfig.RoleWeights:
    """Get role weights for a specific target role level.
    
    Args:
        target_role_level: Target role level
        config: Role level configuration
        
    Returns:
        Role weights for the specified level
    """
    weights_map = {
        "c_suite": config.c_suite_weights,
        "senior_executive": config.senior_executive_weights,
        "director_vp": config.director_vp_weights,
        "senior_ic": config.senior_ic_weights
    }
    
    return weights_map.get(target_role_level, config.senior_executive_weights)


def matches_proven_strength(
    requirement_text: str,
    proven_strengths: list[str] | None
) -> bool:
    """Check if a requirement matches any proven strengths.
    
    Args:
        requirement_text: The requirement text to check
        proven_strengths: List of proven strength keywords
        
    Returns:
        True if requirement matches any proven strength
    """
    if not proven_strengths:
        return False
    
    req_lower = requirement_text.lower()
    return any(strength.lower() in req_lower for strength in proven_strengths)


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

    Note:
        The function modifies the input DataFrame in-place by adding calculated columns.
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


def compute_scores_enhanced(
    df: DataFrame,
    enable_enhancements: bool = False,
    target_role_type: str = "executive",
    years_experience: int = 20,
    target_role_level: str = "senior_executive",
    proven_strengths: list[str] | None = None
) -> ScoreResult:
    """Compute scores with optional strategic positioning enhancements.
    
    This function extends the standard compute_scores() with four enhancement modules:
    1. Dual-Track Scoring: Aligns executive vs IC requirements
    2. Experience-Level Scoring: Calibrates for career stage
    3. Cross-Functional Leadership: Rewards integration capabilities  
    4. Role-Level Calibration: Adjusts for target position level
    
    Args:
        df: Input DataFrame containing skill matrix data
        enable_enhancements: Whether to apply enhancement framework
        target_role_type: Target role type ("executive" or "ic")
        years_experience: Years of professional experience for calibration
        target_role_level: Target role level ("c_suite", "senior_executive", "director_vp", "senior_ic")
        proven_strengths: List of proven strength keywords for bonuses
        
    Returns:
        ScoreResult: Dictionary containing enhanced scoring results
        
    Raises:
        TypeError: If input is not a pandas DataFrame
        ValueError: If required columns are missing or data is invalid
        
    Note:
        When enhancements are disabled, this function behaves identically to compute_scores().
        The function modifies the input DataFrame in-place by adding calculated columns.
    """
    # If enhancements are disabled, use standard scoring
    if not enable_enhancements:
        return compute_scores(df)
    
    # Validate input (same as compute_scores)
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

    # Apply Enhancement 1: Dual-Track Scoring
    df["ReqType"] = df[req_col].apply(lambda x: classify_requirement_type(str(x)))
    df["DualTrackMod"] = df["ReqType"].apply(
        lambda x: dual_track_modifier(x, target_role_type)
    )
    
    # Apply Enhancement 2: Experience-Level Scoring
    df["SkillCategory"] = df[req_col].apply(lambda x: categorize_skill(str(x)))
    df["ExpLevelMod"] = df.apply(
        lambda row: experience_level_modifier(
            row["SkillCategory"], 
            int(row["SelfScore"]), 
            years_experience
        ), 
        axis=1
    )
    
    # Apply Enhancement 3: Cross-Functional Leadership
    complexity_results = df[req_col].apply(
        lambda x: assess_cross_functional_complexity(str(x))
    )
    df["CrossFuncComplexity"] = complexity_results.apply(lambda x: x[0])
    df["IndicatorCount"] = complexity_results.apply(lambda x: x[1])
    
    df["MatchesStrength"] = df[req_col].apply(
        lambda x: matches_proven_strength(str(x), proven_strengths)
    )
    df["CrossFuncMod"] = df.apply(
        lambda row: cross_functional_modifier(
            row["CrossFuncComplexity"],
            row["MatchesStrength"],
            target_role_type == "executive"
        ),
        axis=1
    )
    
    # Apply Enhancement 4: Role-Level Calibration
    role_weights = get_role_weights(target_role_level)
    df["RoleLevelMod"] = df["SkillCategory"].apply(
        lambda cat: getattr(role_weights, cat, 1.0) if cat else 1.0
    )
    
    # Calculate enhanced raw scores
    df["RowScoreRaw"] = (
        df["ClassWt"] * 
        (1 + df["EmphMod"]) * 
        df["SelfScore"] * 
        df["DualTrackMod"] * 
        df["ExpLevelMod"] * 
        df["CrossFuncMod"] * 
        df["RoleLevelMod"]
    )
    
    # Apply bonus capping (similar to standard scoring)
    # Separate core (Essential/Important) from bonus (Desirable/Implicit) skills
    core_mask = df["Classification"].isin(["Essential", "Important"])
    bonus_mask = df["Classification"].isin(["Desirable", "Implicit"])
    
    core_points = df.loc[core_mask, "RowScoreRaw"].sum() if core_mask.any() else 0.0
    bonus_points = df.loc[bonus_mask, "RowScoreRaw"].sum() if bonus_mask.any() else 0.0
    
    # Apply 25% bonus cap
    max_bonus = core_points * SCORING_CONFIG.bonus_cap_percentage
    capped_bonus = min(bonus_points, max_bonus)
    
    # Adjust bonus scores if capping is needed
    if bonus_points > max_bonus and bonus_mask.any():
        bonus_factor = max_bonus / bonus_points if bonus_points > 0 else 0
        df.loc[bonus_mask, "RowScoreRaw"] *= bonus_factor
    
    # Normalize scores
    theoretical_max = SCORING_CONFIG.theoretical_max_raw_score_per_row
    df["RowScoreNorm"] = df["RowScoreRaw"] / theoretical_max
    
    # Calculate final metrics
    actual_points = round(float(df["RowScoreNorm"].sum()), 2)
    max_points = round(float(len(df)), 2)
    pct_fit = round(actual_points / max_points, 2) if max_points else 0.0
    
    # Core gap detection (same logic as standard scoring)
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

    # Sort core_gap_skills for deterministic output
    core_gap_skills = sorted(
        core_gap_skills, key=lambda g: (g.classification, g.self_score, g.name)
    )
    core_gap = bool(core_gap_skills)

    return ScoreResult(
        core_gap=core_gap,
        core_gap_skills=core_gap_skills,
        actual_points=actual_points,
        max_points=max_points,
        pct_fit=pct_fit,
    )

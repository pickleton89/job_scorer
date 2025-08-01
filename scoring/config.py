"""
Configuration Module for Job Scorer
Configuration Settings Module
===========================
This module centralizes all configuration settings for the job_scorer project,
including classification weights, emphasis indicators, and other tunable parameters.

Key Components:
- `CLASS_WT`: Weights for different skill classifications
- `EMPHASIS_INDICATORS`: Text patterns that indicate emphasis in requirements
- `CORE_GAP_THRESHOLD`: Threshold for identifying core gaps
- `BONUS_CAP_PCT`: Maximum bonus as a percentage of base score

Usage Example:
    ```python
    from scoring.config import CLASS_WT, EMPHASIS_INDICATORS

    # Access configuration values
    essential_weight = CLASS_WT['Essential']  # 4.0
    # Check for emphasis indicators
    has_emphasis = any(ind in requirement for ind in EMPHASIS_INDICATORS)
```
Configuration Details:
Classification Weights (CLASS_WT):
    - Essential: 4.0
    - Important: 2.0
    - Desirable: 1.0
    - Implicit: 0.5

Emphasis Indicators (EMPHASIS_INDICATORS):
    - "*" (asterisk)
    - "(must)"
    - "(required)"
    - "(critical)"

Note: These settings directly impact scoring results. Modify with caution and
ensure thorough testing after making changes.

Classes:
    EmphasisIndicators: Keywords for detecting emphasis in requirement text
    UIConfig: UI-related configuration constants
    ScoringConfig: Core scoring system configuration
    ClassificationConfig: Skill classification rules and weights

Global Instances:
    SCORING_CONFIG: Default scoring configuration
    UI_CONFIG: Default UI configuration
    CLASS_WT: Classification weights dictionary
    CORE_GAP_THRESHOLDS: Core gap threshold dictionary
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Literal, NamedTuple, TypeAlias

# Type aliases for better readability
EmphasisLevel: TypeAlias = Literal["high", "low", "neutral"]
ClassificationName: TypeAlias = Literal["Essential", "Important", "Desirable", "Implicit"]
SeverityLevel: TypeAlias = Literal["high", "medium", "low"]


class EmphasisIndicators(NamedTuple):
    """Container for emphasis indicator keywords with type hints.

    Attributes:
        high_emphasis: Tuple of keywords indicating high emphasis requirements
        low_emphasis: Tuple of keywords indicating low emphasis requirements
    """
    high_emphasis: tuple[str, ...] = (
        "expert", "extensive", "strong", "proven", "deep", "comprehensive",
        "advanced", "thorough", "significant", "considerable", "demonstrated",
        "extensively", "expertise", "mastery", "proficiency", "fluent"
    )
    low_emphasis: tuple[str, ...] = (
        "basic", "familiarity", "familiar", "awareness", "aware", "some",
        "knowledge of", "understanding of", "exposure to", "introduction",
        "fundamental", "beginner", "novice", "entry-level", "basic understanding"
    )


@dataclass(frozen=True)
class UIConfig:
    """Configuration for UI-related constants with type hints.

    Attributes:
        separator_length: Length of separator lines in console output
        default_indent: Default indentation for nested output
        max_line_width: Maximum line width for console output
        progress_bar_width: Width of progress bars in characters
        decimal_places: Number of decimal places for numeric output
        pct_decimal_places: Number of decimal places for percentages
    """
    separator_length: int = 50
    default_indent: int = 2
    max_line_width: int = 80
    progress_bar_width: int = 40
    decimal_places: int = 2
    pct_decimal_places: int = 1


@dataclass(frozen=True)
class ScoringConfig:
    """Configuration for the scoring system.

    Attributes:
        max_self_score: Maximum possible self-assessment score (0-5 scale).
        bonus_cap_percentage: Maximum bonus points as a percentage of core points.
        emphasis_modifier_high: Modifier for high-emphasis requirements.
        emphasis_modifier_low: Modifier for low-emphasis requirements.
        emphasis_indicators: Keywords for detecting emphasis in requirement text.
        ui: UI-related configuration
    """
    max_self_score: int = 5
    bonus_cap_percentage: float = 0.25
    emphasis_modifier_high: float = 0.5
    emphasis_modifier_low: float = -0.5
    emphasis_indicators: EmphasisIndicators = field(default_factory=EmphasisIndicators)
    ui: UIConfig = field(default_factory=UIConfig)

    @property
    def theoretical_max_raw_score_per_row(self) -> float:
        """Calculate the theoretical maximum raw score per row."""
        return (
            ClassificationConfig.ESSENTIAL.weight
            * (1 + self.emphasis_modifier_high)
            * self.max_self_score  # 3 * 1.5 * 5 = 22.5
        )


@dataclass(frozen=True)
class ClassificationConfig:
    """Configuration for skill classifications with type hints.

    Attributes:
        name: The name of the classification (Essential/Important/Desirable/Implicit)
        weight: The weight multiplier for this classification
        gap_threshold: The minimum score below which this is considered a gap
    """
    name: ClassificationName
    weight: float
    gap_threshold: int = 0  # Default: no gap detection

    # Class variables for predefined classifications with type hints
    ESSENTIAL: ClassVar[ClassificationConfig]
    IMPORTANT: ClassVar[ClassificationConfig]
    DESIRABLE: ClassVar[ClassificationConfig]
    IMPLICIT: ClassVar[ClassificationConfig]
    @classmethod
    def get_all(cls) -> list[ClassificationConfig]:
        """Get all classification configurations.

        Returns:
            list[ClassificationConfig]: List of all classification configurations
        """
        return [cls.ESSENTIAL, cls.IMPORTANT, cls.DESIRABLE, cls.IMPLICIT]

    @classmethod
    def get_weights_dict(cls) -> dict[ClassificationName, float]:
        """Get classification weights as a typed dictionary.

        Returns:
            dict[ClassificationName, float]: Mapping of classification names to their weights
        """
        return {config.name: config.weight for config in cls.get_all()}

    @classmethod
    def get_gap_thresholds(cls) -> dict[ClassificationName, int]:
        """Get core gap thresholds as a typed dictionary.

        Returns:
            dict[ClassificationName, int]: Mapping of classification names to gap thresholds
        """
        return {config.name: config.gap_threshold for config in cls.get_all()}


# Initialize classification configurations
ClassificationConfig.ESSENTIAL = ClassificationConfig(
    name="Essential",
    weight=3.0,
    gap_threshold=2  # Score <= 2 is a gap
)
ClassificationConfig.IMPORTANT = ClassificationConfig(
    name="Important",
    weight=2.0,
    gap_threshold=1  # Score <= 1 is a gap
)
ClassificationConfig.DESIRABLE = ClassificationConfig(
    name="Desirable",
    weight=1.0,
    gap_threshold=0  # No gaps
)
ClassificationConfig.IMPLICIT = ClassificationConfig(
    name="Implicit",
    weight=0.5,
    gap_threshold=0  # No gaps
)

# Type aliases for configuration dictionaries
ClassificationWeights: TypeAlias = dict[ClassificationName, float]
GapThresholds: TypeAlias = dict[ClassificationName, int]

# Global configuration instances with type hints
SCORING_CONFIG: ScoringConfig = ScoringConfig()
UI_CONFIG: UIConfig = SCORING_CONFIG.ui
CLASS_WT: ClassificationWeights = ClassificationConfig.get_weights_dict()
CORE_GAP_THRESHOLDS: GapThresholds = ClassificationConfig.get_gap_thresholds()

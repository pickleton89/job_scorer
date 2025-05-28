"""
Job Scorer Package
=================

A tool for scoring job applications against skill matrices.

This package provides functionality to:
- Load and validate skill matrix data
- Compute scores based on self-assessments
- Generate detailed reports with recommendations

Modules:
- cli: Command line interface
- config: Configuration and constants
- data_loader: Loading and validation of skill matrices
- scoring_engine: Core scoring logic
"""

# --- CLI entry points ---
from .cli import main, parse_args

# --- Configuration and constants ---
from .config import (
    CLASS_WT,
    CORE_GAP_THRESHOLDS,
    SCORING_CONFIG,
    UI_CONFIG,
    ClassificationConfig,
    EmphasisIndicators,
    ScoringConfig,
    UIConfig,
)

# --- Data loading and validation ---
from .data_loader import load_matrix

# --- Core scoring logic ---
from .scoring_engine import CoreGapSkill, compute_scores, emphasis_modifier

# Define __all__ to explicitly specify the public API
__all__ = [
    'main',
    'parse_args',
    'load_matrix',
    'compute_scores',
    'emphasis_modifier',
    'CoreGapSkill',
    'CLASS_WT',
    'CORE_GAP_THRESHOLDS',
    'SCORING_CONFIG',
    'UI_CONFIG',
    'ClassificationConfig',
    'ScoringConfig',
    'UIConfig',
    'EmphasisIndicators'
]

# Set version info
__version__ = "2.0.0"

"""
Data Loading and Validation Module
==================================

This module provides functionality to load, validate, and process skill matrix CSV files
for the job scoring system. It ensures data integrity and prepares the data for scoring.

Key Features:
- Validates file existence, format, and permissions
- Checks for required columns and valid data types
- Processes and normalizes input data
- Handles various edge cases and error conditions

Main Functions:
- `load_matrix()`: Load and validate skill matrix CSV files
- `emphasis_modifier()`: Determine emphasis level from requirement text

Usage Example:
    ```python
    from pathlib import Path
    from scoring.data_loader import load_matrix

    try:
        # Load and validate a skill matrix
        df = load_matrix(Path("skills.csv"))
        print(f"Successfully loaded {len(df)} skills")

        # Display the first few rows
        print(df.head())

    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading skill matrix: {e}")
    ```

Input CSV Format:
    The CSV file must include these required columns:
    - `Requirement`: Description of the skill/requirement
    - `Classification`: One of: Essential, Important, Desirable, Implicit
    - `SelfScore`: Numeric score (0-5)

Dependencies:
- pandas: For data manipulation and CSV handling
- pathlib: For cross-platform path handling
- config: For scoring configuration defaults

Note: This module is designed to work with the rest of the scoring package
and is typically used through the main CLI interface."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pandas as pd
from pandas import DataFrame

# Local application/library specific imports
if TYPE_CHECKING:
    from .config import ScoringConfig

# Type aliases for better readability
EmphasisModifier = float  # Type alias for emphasis modifier values

# Handle imports with fallback for different execution contexts
try:
    # Attempt relative import for normal package use
    from .config import CLASS_WT, SCORING_CONFIG, ScoringConfig
except ImportError:
    try:
        # Fallback for direct script execution or when module is not part of a package
        from config import CLASS_WT, SCORING_CONFIG, ScoringConfig  # type: ignore[import-not-found,no-redef]
    except ImportError as ie:
        raise ImportError(
            "Failed to import configuration. Make sure the module is properly installed "
            "or run from the correct directory."
        ) from ie


def emphasis_modifier(text: str | Any, config: ScoringConfig = SCORING_CONFIG) -> EmphasisModifier:
    """Determine the emphasis modifier for a given requirement text.

    Analyzes the text of a requirement to determine if it indicates a higher or lower
    level of emphasis, which affects the scoring weight. This helps in identifying
    how critical each requirement is to the role.

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
    """Determine the emphasis modifier for a given requirement text.

    Analyzes the text of a requirement to determine if it indicates a higher or lower
    level of emphasis, which affects the scoring weight. This helps in identifying
    how critical each requirement is to the role.

    Args:
        text: The requirement text to analyze. Should be a string, but will handle
              non-string inputs gracefully by treating them as standard emphasis.
        config: Scoring configuration containing emphasis settings.

    Returns:
        float: The emphasis modifier to apply to the score (config.emphasis_modifier_high for high,
              config.emphasis_modifier_low for low, 0.0 for neutral).
    """
    if not isinstance(text, str):
        return 0.0

    t = text.lower().strip()

    # Check for high emphasis indicators first
    if any(keyword in t for keyword in config.emphasis_indicators.high_emphasis):
        return config.emphasis_modifier_high

    # Then check for low emphasis indicators
    if any(keyword in t for keyword in config.emphasis_indicators.low_emphasis):
        return config.emphasis_modifier_low

    return 0.0  # No emphasis modifier


def load_matrix(path: str | Path) -> DataFrame:
    """Load and validate the skill matrix CSV file.

    Loads a CSV file containing skill matrix data, validates its structure and content,
    and returns a processed DataFrame with derived columns for scoring.

    Args:
        path: Path to the CSV file containing skill matrix data.
            Expected to have at minimum the columns: Classification, Requirement, and SelfScore.

    Returns:
        DataFrame: Processed DataFrame with the following columns:
            - Original columns from the input CSV
            - ClassWt: Numeric weight based on Classification
            - EmphMod: Emphasis modifier (-0.5 to +0.5) based on requirement text
            - Weight: Same as ClassWt (for backward compatibility)
            - SelfScore: Validated and normalized to integer 0-5

    Raises:
        TypeError: If path is not a string or Path object.
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the path is not a file, file is empty, required columns are missing,
                   data is malformed, or contains invalid values.
        pd.errors.EmptyDataError: If the file is empty (subclass of ValueError).
        PermissionError: If the file cannot be read due to permissions.
    """
    """Load and validate the skill matrix CSV file.

    Loads a CSV file containing skill matrix data, validates its structure and content,
    and returns a processed DataFrame with derived columns for scoring.

    Args:
        path: Path to the CSV file containing skill matrix data.
            Expected to have at minimum the columns: Classification, Requirement, and SelfScore.

    Returns:
        pd.DataFrame: Processed DataFrame with the following columns:
            - Original columns from the input CSV
            - ClassWt: Numeric weight based on Classification
            - EmphMod: Emphasis modifier (-0.5 to +0.5) based on requirement text
            - Weight: Same as ClassWt (for backward compatibility)
            - SelfScore: Validated and normalized to integer 0-5

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read due to permissions.
        pd.errors.EmptyDataError: If the file is empty.
        ValueError: If required columns are missing, data is malformed, or contains
                   invalid values that cannot be processed.
    """
    # Define required columns and their expected data types
    required_columns = {"Classification", "Requirement", "SelfScore"}
    valid_classifications = set(CLASS_WT.keys())

    # 1. Validate input path
    if not isinstance(path, str | Path):
        raise TypeError(f"Expected str or Path, got {type(path).__name__}")

    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path}")

    # 2. Read the CSV file with error handling
    try:
        df: DataFrame = pd.read_csv(path_obj)
    except pd.errors.EmptyDataError as e:
        raise pd.errors.EmptyDataError("The CSV file is empty") from e
    except UnicodeDecodeError as e:
        raise ValueError(
            f"Unable to decode CSV file. Ensure it's a valid CSV file. Error: {e}"
        ) from e
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}") from e

    # 3. Validate required columns
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(sorted(missing_columns))}. "
            f"Required columns are: {', '.join(sorted(required_columns))}"
        )

    # 4. Validate Classification values
    invalid_classifications = set(df["Classification"]) - valid_classifications
    if invalid_classifications:
        raise ValueError(
            f"Invalid Classification values found: {', '.join(sorted(invalid_classifications))}. "
            f"Valid values are: {', '.join(sorted(valid_classifications))}"
        )

    # 5. Process and validate SelfScore
    try:
        # Convert to numeric, coerce non-numeric to NaN, then fill with 0
        df["SelfScore"] = (
            pd.to_numeric(df["SelfScore"], errors="coerce")
            .fillna(0.0)
            .clip(0, SCORING_CONFIG.max_self_score)
            .astype(int)
        )
    except Exception as e:
        raise ValueError(f"Error processing SelfScore values: {e}") from e

    # 6. Add derived columns
    try:
        df["ClassWt"] = df["Classification"].map(CLASS_WT).fillna(0.0)
        df["EmphMod"] = df["Requirement"].apply(
            lambda text: emphasis_modifier(cast(str, text) if pd.notna(text) else "", SCORING_CONFIG)
        )
        df["Weight"] = df["ClassWt"]  # For backward compatibility
    except Exception as e:
        raise ValueError(f"Error processing derived columns: {e}") from e

    return df

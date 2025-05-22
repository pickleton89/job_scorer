# -*- coding: utf-8 -*-
"""
Skill-Matrix Scoring Utility
===========================
Reads a CSV exported from your scorecard (must include at minimum the columns
`Requirement/Skill`, `Weight`, and `SelfScore`) and returns:

• A per-row **core-gap** flag (Weight == 3 AND SelfScore ≤ 1)
• A bonus-weight cap (default = 25 % of core weight *or* a fixed max-row cap)
• The effective denominator, max points, actual points and %-fit
• A human-readable verdict tier

Bug-fix 2025-05-20
------------------
Earlier logic could mis-count bonus rows if the bonus cap was already hit *before*
the last Weight-1 row in sequence.

Usage
-----
```bash
python job-skill-matrix-scoring.py skills.csv               # default 25 % bonus cap
python job-skill-matrix-scoring.py skills.csv --cap 0.30     # % cap override
python job-skill-matrix-scoring.py skills.csv --cap 5        # row-limit mode (max 5 W1 rows)
```
The script is dependency-light (pandas only).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Dict, List, Union
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


# --- Constants ---
# Classification weights
CLASS_WT = {
    "Essential": 3.0,
    "Important": 2.0,
    "Desirable": 1.0,
    "Implicit": 0.5,
}

# Scoring system constants
MAX_SELF_SCORE = 5  # Maximum self-assessment score (0-5 scale)
BONUS_CAP_PERCENTAGE = 0.25  # Bonus points capped at 25% of core points
EMPHASIS_MODIFIER_HIGH = +0.5  # For critical/advanced requirements
EMPHASIS_MODIFIER_LOW = -0.5   # For basic/familiarity requirements
THEORETICAL_MAX_RAW_SCORE_PER_ROW = (
    CLASS_WT["Essential"] * (1 + EMPHASIS_MODIFIER_HIGH) * MAX_SELF_SCORE  # 3 * 1.5 * 5 = 22.5
)

# Core gap detection thresholds
CORE_GAP_THRESHOLDS = {
    "Essential": 2,   # Score <= 2 is a gap
    "Important": 1,   # Score <= 1 is a gap
    "Desirable": 0,   # No gaps for Desirable
    "Implicit": 0     # No gaps for Implicit
}

def emphasis_modifier(text: str) -> float:
    """Determine the emphasis modifier for a given requirement text.
    
    Analyzes the text of a requirement to determine if it indicates a higher or lower
    level of emphasis, which affects the scoring weight. This helps in identifying
    how critical each requirement is to the role.
    
    Args:
        text: The requirement text to analyze. Should be a string, but will handle
              non-string inputs gracefully by treating them as standard emphasis.
    
    Returns:
        float: The emphasis modifier to apply to the score calculation.
            - +0.5: For critical/high-emphasis requirements (e.g., "expert", "extensive")
            - 0.0: For standard requirements (default)
            - -0.5: For minimal/low-emphasis requirements (e.g., "familiarity", "exposure")
            
    Examples:
        >>> emphasis_modifier("Expert knowledge of Python")
        0.5
        >>> emphasis_modifier("Basic familiarity with Git")
        -0.5
        >>> emphasis_modifier("Experience with cloud platforms")
        0.0
        >>> emphasis_modifier("")
        0.0
        >>> emphasis_modifier(None)
        0.0
    """
    # Handle non-string input gracefully
    if not isinstance(text, str) or not text.strip():
        return 0.0
    
    try:
        t = text.lower()
        
        # Keywords indicating critical/high-emphasis requirements
        high_emphasis_keywords = {
            "expert", "extensive", "demonstrated", "proven", "advanced",
            "strong", "deep", "comprehensive", "thorough", "mastery",
            "extensively", "proficient", "extensive", "proven"
        }
        
        # Keywords indicating minimal/low-emphasis requirements
        low_emphasis_keywords = {
            "familiarity", "exposure", "limited", "basic", "awareness",
            "some", "introductory", "beginner", "novice", "entry-level",
            "basic understanding", "conceptual knowledge"
        }
        
        # Check for high emphasis keywords
        if any(keyword in t for keyword in high_emphasis_keywords):
            return +0.5
            
        # Check for low emphasis keywords
        if any(keyword in t for keyword in low_emphasis_keywords):
            return -0.5
            
        return 0.0
        
    except Exception as e:
        # Log the error and return default value
        print(f"Warning: Error processing emphasis for text: {text[:50]}... Error: {e}", file=sys.stderr)
        return 0.0

def load_matrix(path: Path) -> pd.DataFrame:
    """Load and validate the skill matrix CSV file.
    
    Loads a CSV file containing skill matrix data, validates its structure and content,
    and returns a processed DataFrame with derived columns for scoring.
    
    Args:
        path: Path to the CSV file containing skill matrix data.
            Expected to have at least the columns: Classification, Requirement, and SelfScore.
            
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
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Expected str or Path, got {type(path).__name__}")
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    # 2. Read the CSV file with error handling
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("The CSV file is empty")
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to decode CSV file. Ensure it's a valid CSV file. Error: {e}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
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
            .fillna(0)
            .clip(0, MAX_SELF_SCORE)
            .astype(int)
        )
    except Exception as e:
        raise ValueError(f"Error processing SelfScore values: {e}")
    
    # 6. Add derived columns
    try:
        df["ClassWt"] = df["Classification"].map(CLASS_WT).fillna(0)
        df["EmphMod"] = df["Requirement"].apply(emphasis_modifier)
        df["Weight"] = df["ClassWt"]  # For backward compatibility
    except Exception as e:
        raise ValueError(f"Error processing derived columns: {e}")
    
    return df


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------


@dataclass
class CoreGapSkill:
    """Represents a skill that has a core gap (below threshold score).
    
    This class encapsulates information about a skill that has been identified as having
    a core gap, meaning the self-assessed score is below the minimum threshold for its
    classification. It provides methods to determine the severity of the gap.
    
    Attributes:
        name: The name or description of the skill/requirement.
        classification: The classification of the skill (e.g., 'Essential', 'Important').
        self_score: The self-assessed score (0-5) for this skill.
        threshold: The minimum acceptable score for this skill's classification.
    
    Example:
        >>> gap = CoreGapSkill(
        ...     name="Python programming",
        ...     classification="Essential",
        ...     self_score=2,
        ...     threshold=3
        ... )
        >>> gap.severity
        'Medium'
    """
    name: str
    classification: str
    self_score: int
    threshold: int
    
    def __post_init__(self) -> None:
        """Validate the input values after initialization."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Skill name must be a non-empty string")
            
        if self.classification not in {"Essential", "Important", "Desirable", "Implicit"}:
            raise ValueError(f"Invalid classification: {self.classification}")
            
        if not isinstance(self.self_score, int) or not 0 <= self.self_score <= 5:
            raise ValueError("Self score must be an integer between 0 and 5")
            
        if not isinstance(self.threshold, int) or self.threshold < 0:
            raise ValueError("Threshold must be a non-negative integer")
    
    @property
    def severity(self) -> str:
        """Determine the severity level of the core gap.
        
        Returns:
            str: The severity level, one of:
                - 'High': For Essential skills with score ≤ 1
                - 'Medium': For Essential skills with score > 1, or Important skills with score = 0
                - 'Low': For Important skills with score > 0
                
        Note:
            Desirable and Implicit skills should not have core gaps, but if encountered,
            they will be treated as 'Low' severity.
        """
        if self.classification == "Essential":
            return "High" if self.self_score <= 1 else "Medium"
        return "Medium" if self.self_score == 0 else "Low"

def compute_scores(df: pd.DataFrame) -> Dict[str, Union[bool, List[CoreGapSkill], float]]:
    """Compute core-gap flag, points and %-fit using the new scoring system.
    
    This function processes a DataFrame containing skill matrix data and calculates:
    - Core gaps based on classification and self-scores
    - Raw and normalized scores for each requirement
    - Bonus points with capping for Desirable/Implicit skills
    - Overall fit percentage
    
    Scoring Formula:
        Raw Score = ClassWt * (1 + EmphMod) * SelfScore
        Where:
        - ClassWt: Weight based on classification (Essential=3.0, Important=2.0, etc.)
        - EmphMod: Emphasis modifier from -0.5 to +0.5 based on requirement text
        - SelfScore: Self-assessment score from 0-5
    
    Core Gap Detection:
        A core gap is identified when:
        - Essential items with SelfScore <= 2
        - Important items with SelfScore <= 1
        - Thresholds are configurable via CORE_GAP_THRESHOLDS
    
    Args:
        df: Input DataFrame containing skill matrix data. Must include columns:
            - Classification: Skill classification (Essential/Important/Desirable/Implicit)
            - ClassWt: Numeric weight based on classification
            - EmphMod: Emphasis modifier (-0.5 to +0.5)
            - SelfScore: Self-assessment score (0-5)
            - Plus a column containing the requirement/skill name
    
    Returns:
        Dict containing the following keys:
        - core_gap: bool - True if any core gaps exist, False otherwise
        - core_gap_skills: List[CoreGapSkill] - Sorted list of skills with core gaps
        - actual_points: float - Total points scored (rounded to 2 decimal places)
        - max_points: float - Maximum possible points (rounded to 2 decimal places)
        - pct_fit: float - Percentage fit (0.0 to 1.0)
        
    Raises:
        ValueError: If required columns are missing or data is invalid
        KeyError: If expected columns are not found in the DataFrame
        TypeError: If input types are incorrect
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    required_columns = {"Classification", "ClassWt", "EmphMod", "SelfScore"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns in input DataFrame: {', '.join(sorted(missing_columns))}")
    
    # Find the requirement/skill column name
    req_col = next(
        (col for col in df.columns 
         if any(term in col.lower() for term in ["requirement", "skill", "description"])),
        "Requirement"  # Default fallback
    )
    
    try:
        # Calculate raw scores with emphasis modifiers
        df["RowScoreRaw"] = df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]
        
        # Core gap detection based on classification and score thresholds
        core_gap_mask = pd.Series(False, index=df.index)
        core_gap_skills: List[CoreGapSkill] = []
        
        for class_type, threshold in CORE_GAP_THRESHOLDS.items():
            if threshold > 0:  # Only check if threshold is set
                class_mask = (df["Classification"] == class_type) & (df["SelfScore"] <= threshold)
                core_gap_mask = core_gap_mask | class_mask
                
                # Add gap skills for this classification
                if class_mask.any():
                    gap_rows = df[class_mask]
                    for _, row in gap_rows.iterrows():
                        core_gap_skills.append(CoreGapSkill(
                            name=row[req_col],
                            classification=row["Classification"],
                            self_score=row["SelfScore"],
                            threshold=threshold
                        ))
        
        # Sort gaps by classification (Essential first) and then by self_score (lowest first)
        classification_order = {"Essential": 0, "Important": 1, "Desirable": 2, "Implicit": 3}
        core_gap_skills.sort(key=lambda x: (classification_order[x.classification], x.self_score))
        
        core_gap = len(core_gap_skills) > 0
        
        # Calculate core weight (sum of weights for Essential and Important items)
        core_weight = df[df["Classification"].isin(["Essential", "Important"])]["ClassWt"].sum()
        
        # Calculate bonus points and apply cap if needed
        max_bonus_points = core_weight * BONUS_CAP_PERCENTAGE * MAX_SELF_SCORE
        bonus_mask = df["Classification"].isin(["Desirable", "Implicit"])
        actual_bonus_points = df.loc[bonus_mask, "RowScoreRaw"].sum()
        
        # Apply bonus cap if needed
        if actual_bonus_points > max_bonus_points and actual_bonus_points > 0:
            bonus_scale = max_bonus_points / actual_bonus_points
            df.loc[bonus_mask, "RowScoreRaw"] *= bonus_scale
        
        # Normalize scores and calculate final metrics
        df["RowScoreNorm"] = df["RowScoreRaw"] / THEORETICAL_MAX_RAW_SCORE_PER_ROW
        actual_points = df["RowScoreNorm"].sum()
        max_points = len(df) * 1.0  # Each row contributes up to 1.0 after normalization
        pct_fit = (actual_points / max_points) if max_points > 0 else 0.0
        
        return {
            "core_gap": core_gap,
            "core_gap_skills": core_gap_skills,
            "actual_points": round(actual_points, 2),
            "max_points": round(max_points, 2),
            "pct_fit": pct_fit,
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating scores: {str(e)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Main entry point for the job skill matrix scoring tool.
    
    This function:
    1. Parses command line arguments
    2. Loads and validates the skill matrix CSV
    3. Computes scores and identifies core gaps
    4. Generates a detailed report with recommendations
    
    Usage:
        python scoring_v2.py path/to/skills.csv
    
    The CSV must contain the following columns:
    - Classification: One of 'Essential', 'Important', 'Desirable', or 'Implicit'
    - Requirement: The skill or requirement description (used for emphasis detection)
    - SelfScore: Your self-assessment score from 0 to 5
    
    Returns:
        None: Outputs results to stdout and exits with appropriate status code
        
    Raises:
        FileNotFoundError: If the specified CSV file doesn't exist
        PermissionError: If the file cannot be read due to permissions
        ValueError: If the CSV is malformed or contains invalid data
        SystemExit: With status code 1 if an error occurs during processing
    """
    # Set up argument parser with detailed help
    parser = argparse.ArgumentParser(
        description=(
            "Score your job application fit against a skill matrix.\n\n"
            "The tool analyzes your self-assessed skills against job requirements\n"
            "and provides a detailed report with recommendations."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python scoring_v2.py my_skills.csv\n\n"
            "For best results, ensure your CSV follows the required format:\n"
            "  - One requirement per row\n"
            "  - Use valid Classification values\n"
            "  - SelfScore should be an integer 0-5"
        )
    )
    
    parser.add_argument(
        "csv",
        type=Path,
        help="Path to CSV file containing skill matrix data"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0",
        help="Show program's version number and exit"
    )
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Load and validate the skill matrix
    try:
        if not args.csv.exists():
            raise FileNotFoundError(f"File not found: {args.csv}")
            
        df_raw = load_matrix(args.csv)
        
        # Basic validation of the loaded data
        if df_raw.empty:
            raise ValueError("The CSV file is empty or contains no valid data")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPlease ensure the CSV file exists and follows the required format.", file=sys.stderr)
        print("Use --help for more information.", file=sys.stderr)
        sys.exit(1)
    
    # Process the matrix and calculate metrics
    try:
        metrics = compute_scores(df_raw)
    except Exception as e:
        print(f"Error calculating scores: {e}", file=sys.stderr)
        print("\nThe skill matrix data appears to be invalid. Please check your input.", file=sys.stderr)
        sys.exit(1)


    # ----- Report -----
    pd.set_option("display.max_rows", None)
    # Display the processed matrix with scores
    print(df_raw[[c for c in df_raw.columns if c != "RowScoreRaw"] + ["RowScoreRaw"]])

    print("\n" + "="*50)
    print("SCORECARD SUMMARY")
    print("="*50)
    
    # Core gap status
    core_gap_status = "YES" if metrics["core_gap"] else "NO"
    print(f"\n1. Core gap present : {core_gap_status}")
    
    if metrics["core_gap"]:
        # Report on each classification with gaps
        essential_gaps = [g for g in metrics["core_gap_skills"] if g.classification == "Essential"]
        important_gaps = [g for g in metrics["core_gap_skills"] if g.classification == "Important"]
        
        if essential_gaps:
            print(f"   ⚠️  {len(essential_gaps)} Essential skill(s) scored ≤ {CORE_GAP_THRESHOLDS['Essential']}.")
        if important_gaps:
            print(f"   ⚠️  {len(important_gaps)} Important skill(s) scored ≤ {CORE_GAP_THRESHOLDS['Important']}.")
        
        print("   ⚠️  Treat as a red flag — address these gaps before applying.")
    else:
        print("   ✓  All essential and important skills meet the minimum score requirements.")
    
    # Points calculation
    print(f"\n2. Actual points    : {metrics['actual_points']} / {metrics['max_points']}")
    print(f"   • Your weighted evidence of fit: {metrics['actual_points']} points")
    print(f"   • Maximum possible score: {metrics['max_points']} points")
    
    # Percentage fit
    pct = metrics["pct_fit"]
    print(f"\n3. % Fit            : {pct:.1%}")
    
    # Add disclaimer about % Fit when core gaps are present
    if metrics["core_gap"]:
        print("   ⚠️  DISCLAIMER: % Fit is misleading when core gaps are present.")
        print("   ⚠️  Address core gaps first before considering the % Fit value.")
    
    fit_guidance = (
        "   ✓  Excellent overall fit → Apply immediately, emphasize strengths"
        if pct >= 0.80 else
        "   ✓  Good fit; minor gaps → Apply; line up examples or quick up-skilling"
        if pct >= 0.65 else
        "   ⚠️  Possible fit; several gaps → Decide whether to apply now or build skills first"
        if pct >= 0.50 else
        "   ⚠️  Significant gaps → Up-skill before investing in an application"
    )
    print(fit_guidance)
    
    # Verdict
    if metrics["core_gap"]:
        # Core gap present = YES
        verdict = "Critical gap — address before applying."
        print(f"\n4. Verdict          : {verdict}")
        print("   Note: Core gap overrides the %-Fit tier.")
        
        # Print the core gap skills
        print("\n5. Core Gap Skills:")
        for gap in metrics["core_gap_skills"]:
            print(f"   • \"{gap.name}\" (Classification: {gap.classification}, SelfScore: {gap.self_score})")
        
        print("\n   Use as a to-do list: supply stronger evidence or up-skill")
        print("   until you can honestly self-score above the threshold for these items.")
    else:
        # No core gap present, verdict based on % Fit
        pct = metrics["pct_fit"]
        if pct >= 0.80:
            # No core gap and Fit ≥ 80 %
            verdict = "Excellent match"
        elif pct >= 0.65:
            # No core gap and 65 % ≤ Fit < 80 %
            verdict = "Good match (minor gaps)"
        elif pct >= 0.50:
            # No core gap and 50 % ≤ Fit < 65 %
            verdict = "Possible match — several gaps"
        else:
            # No core gap and Fit < 50 %
            verdict = "Significant gaps — consider learning first"
        
        print(f"\n4. Verdict          : {verdict}")
    
    # Add next steps guidance
    print("\n" + "-"*50)
    print("RECOMMENDED NEXT STEPS")
    print("-"*50)
    
    if metrics["core_gap"]:
        print("1. Focus on closing the high and medium severity gaps first.")
        print("2. Re-evaluate after addressing these critical skills.")
        print("3. For each gap, consider:")
        print("   - Can you find stronger evidence from your experience?")
        print("   - What specific training or practice would improve your score?")
        print("   - Are there alternative skills you could highlight to compensate?")
    else:
        if pct >= 0.80:
            print("1. Apply immediately - you're an excellent match!")
            print("2. Prepare to highlight your strengths in these areas.")
        elif pct >= 0.65:
            print("1. Apply with confidence - you're a good match.")
            print("2. Prepare examples for your interview that address the minor gaps.")
        elif pct >= 0.50:
            print("1. Consider whether to apply now or build skills first.")
            print("2. If applying now, be prepared to discuss your development plan.")
        else:
            print("1. Focus on skill development before applying.")
            print("2. Target the Weight 3 and Weight 2 items with low self-scores.")
    
    # Add reminder about self-scoring
    print("\nReminder: Use concrete metrics (projects, KPIs) to justify your self-scores.")
    print("Run this tool again after improving skills or gathering better evidence.")



if __name__ == "__main__":
    """Main entry point when run as a script.
    
    This block is executed when the script is run directly from the command line.
    It wraps the main() function call in a try-except block to ensure that any
    unhandled exceptions are caught and reported with a clean error message.
    
    The script will exit with a non-zero status code if an error occurs,
    which is useful for scripting and automation.
    
    Example:
        $ python scoring_v2.py skills.csv
        
    Exit Codes:
        0: Success
        1: Error occurred during execution
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        print("\nUse --help for usage information.", file=sys.stderr)
        sys.exit(1)

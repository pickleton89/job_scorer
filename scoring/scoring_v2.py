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
from pathlib import Path
from typing import List

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
    """Return +0.5 (Critical), 0.0 (Standard), or -0.5 (Minimal)."""
    if not isinstance(text, str):
        return 0.0
        
    t = text.lower()
    if any(w in t for w in {"expert", "extensive", "demonstrated", "proven", "advanced"}):
        return +0.5
    if any(w in t for w in {"familiarity", "exposure", "limited"}):
        return -0.5
    return 0.0

def load_matrix(path: Path) -> pd.DataFrame:
    """Load and validate the skill matrix CSV file.
    
    Args:
        path: Path to the CSV file containing skill matrix data
        
    Returns:
        pd.DataFrame: Processed DataFrame with required columns for scoring
        
    Raises:
        ValueError: If required columns are missing or data is invalid
    """
    # Define required and optional columns
    required_columns = {"Classification", "Requirement", "SelfScore"}
    
    # Read the CSV file
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    # Validate required columns
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(missing_columns)}. "
            "Required columns are: Classification, Requirement, SelfScore"
        )
    
    # Add derived columns
    df["ClassWt"] = df["Classification"].map(CLASS_WT).fillna(0)
    df["EmphMod"] = df["Requirement"].apply(emphasis_modifier)
    
    # For backward compatibility with some reporting code
    df["Weight"] = df["Classification"].map(CLASS_WT).fillna(0)
    
    # Ensure SelfScore is a valid integer between 0 and 5
    df["SelfScore"] = (
        pd.to_numeric(df["SelfScore"], errors="coerce")
        .fillna(0)
        .clip(0, MAX_SELF_SCORE)
        .astype(int)
    )
    
    return df


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------


@dataclass
class CoreGapSkill:
    """Represents a skill that has a core gap (below threshold score)."""
    name: str
    classification: str
    self_score: int
    threshold: int
    
    @property
    def severity(self) -> str:
        """Return a human-readable severity level."""
        if self.classification == "Essential":
            return "High" if self.self_score <= 1 else "Medium"
        return "Medium" if self.self_score == 0 else "Low"

def compute_scores(df: pd.DataFrame) -> dict:
    """Compute core-gap flag, points and %-fit using the new scoring system.
    
    New scoring formula: ClassWt * (1 + EmphMod) * SelfScore
    - ClassWt: Weight based on classification (Essential=3.0, Important=2.0, etc.)
    - EmphMod: Emphasis modifier from -0.5 to +0.5 based on requirement text
    - SelfScore: Self-assessment score from 0-5
    
    Core gap is triggered for:
    - Essential items with SelfScore <= 2
    - Important items with SelfScore <= 1 (optional, can be configured)
    
    Returns:
        dict: Dictionary containing scoring results with the following keys:
            - core_gap: bool - Whether any core gaps exist
            - core_gap_skills: List[CoreGapSkill] - List of skills with core gaps
            - actual_points: float - Total points scored (rounded to 2 decimal places)
            - max_points: float - Maximum possible points (rounded to 2 decimal places)
            - pct_fit: float - Percentage fit (0.0 to 1.0)
    """
    # Calculate raw scores with emphasis modifiers
    df["RowScoreRaw"] = df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]
    
    # Core gap detection based on classification and score thresholds
    core_gap_mask = pd.Series(False, index=df.index)
    core_gap_skills: List[CoreGapSkill] = []
    
    # Find the requirement/skill column name
    req_col = next((col for col in df.columns if "requirement" in col.lower() or "skill" in col.lower()), "Requirement")
    
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
    
    # Calculate points and percentage
    # Apply bonus cap (25% of core weight)
    core_weight = df[df["Classification"].isin(["Essential", "Important"])]["ClassWt"].sum()
    
    # Calculate bonus points and apply cap if needed
    max_bonus_points = core_weight * BONUS_CAP_PERCENTAGE * MAX_SELF_SCORE
    bonus_mask = df["Classification"].isin(["Desirable", "Implicit"])
    actual_bonus_points = df.loc[bonus_mask, "RowScoreRaw"].sum()
    
    if actual_bonus_points > max_bonus_points and actual_bonus_points > 0:
        # Scale down bonus points to fit within the cap
        bonus_scale = max_bonus_points / actual_bonus_points
        df.loc[bonus_mask, "RowScoreRaw"] *= bonus_scale
    
    # Normalize each row by the theoretical maximum score per row
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute fit score from a skill-matrix CSV.\n\n"
        "The CSV must contain the following columns:\n"
        "- Classification: One of 'Essential', 'Important', 'Desirable', or 'Implicit'\n"
        "- Requirement: The skill or requirement description (used for emphasis detection)\n"
        "- SelfScore: Your self-assessment score from 0 to 5"
    )
    parser.add_argument(
        "csv",
        type=Path,
        help="Path to CSV with Classification, Requirement, and SelfScore columns"
    )
    args = parser.parse_args()

    try:
        df_raw = load_matrix(args.csv)
    except ValueError as e:
        print(f"Error loading skill matrix: {e}", file=sys.stderr)
        sys.exit(1)

    # Process the matrix - bonus capping is handled in compute_scores
    metrics = compute_scores(df_raw)


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
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

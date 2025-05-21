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
the last Weight-1 row in sequence. The updated `apply_bonus_cap` now slices the
Weight-1 subset deterministically, keeping only the first **N** rows that fit
within the cap and zeroing out the rest — avoiding off-by-one edge cases.

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
import math
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


# --- Constants ---
CLASS_WT = {
    "Essential": 3.0,
    "Important": 2.0,
    "Desirable": 1.0,
    "Implicit": 0.5,
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
    """Load CSV and coerce numeric columns."""
    df = pd.read_csv(path)
    
    # Handle new format with Classification and Requirement
    if "Classification" in df.columns:
        if not {"Classification", "Requirement"}.issubset(df.columns):
            raise ValueError("CSV must contain 'Classification' and 'Requirement' columns.")
            
        df["ClassWt"] = df["Classification"].map(CLASS_WT).fillna(0)
        df["EmphMod"] = df["Requirement"].apply(emphasis_modifier)
        
        # For backward compatibility, set Weight based on Classification
        df["Weight"] = df["Classification"].map(CLASS_WT).fillna(0)
    else:
        # Original format - keep existing behavior
        required_cols = {"Weight", "SelfScore"}
        if not required_cols.issubset(df.columns):
            missing = ", ".join(required_cols - set(df.columns))
            raise ValueError(f"CSV missing required columns: {missing}")
    
    # Handle numeric columns
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce").fillna(0).astype(float)
    df["SelfScore"] = pd.to_numeric(df["SelfScore"], errors="coerce").fillna(0).clip(0, 5).astype(int)
    
    return df


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------


def apply_bonus_cap(
    df_in: pd.DataFrame,
    cap_pct: float | None = 0.25,
    cap_rows: int | None = None,
) -> tuple[pd.DataFrame, int]:
    """Apply bonus cap to the dataframe.
    
    In the new scoring system, we cap the total bonus points (from Desirable/Implicit items)
    to 25% of the total core points (from Essential/Important items).
    
    Args:
        df_in: Input dataframe with skill scores
        cap_pct: Maximum bonus as a percentage of core weight (default: 0.25)
        cap_rows: Maximum number of bonus rows to consider (for backward compatibility)
        
    Returns:
        Tuple of (modified dataframe, number of bonus rows included)
    """
    """Return (**new DF**, **effective_total_weight**).

    • **Row-limit mode**   (`cap_rows` is int) – keep at most *cap_rows* Weight-1 rows.
    • **Percent mode**    (`cap_pct` float ≤ 1) – bonus weight ≤ core_weight × cap_pct.

    Weight-1 rows beyond the cap have their Weight set to **0** (they remain visible
    for the user, but they don't influence the math).
    """
    df = df_in.copy()

    core_mask = df["Weight"] >= 2
    core_weight = df.loc[core_mask, "Weight"].sum()

    # ------------------ row-limit cap ------------------
    if cap_rows is not None:
        bonus_idx = df.index[df["Weight"] == 1]
        # zero-out everything after the first `cap_rows` Weight-1 rows
        if len(bonus_idx) > cap_rows:
            drop_idx = bonus_idx[cap_rows:]
            df.loc[drop_idx, "Weight"] = 0
        effective_total_weight = core_weight + min(len(bonus_idx), cap_rows)
        return df, effective_total_weight

    # ------------------ percentage cap ----------------
    # Use math.ceil to guarantee at least one bonus row when cap_pct > 0 and core_weight > 0
    allowed_bonus_weight = int(math.ceil(core_weight * (cap_pct or 0))) if core_weight > 0 and cap_pct > 0 else 0
    bonus_idx = df.index[df["Weight"] == 1]

    # If total bonus ≤ allowed, nothing to trim
    if len(bonus_idx) <= allowed_bonus_weight:
        effective_total_weight = core_weight + len(bonus_idx)
        return df, effective_total_weight

    # otherwise trim: keep only the first N rows where N = allowed_bonus_weight
    drop_idx = bonus_idx[allowed_bonus_weight:]
    df.loc[drop_idx, "Weight"] = 0
    effective_total_weight = core_weight + allowed_bonus_weight
    return df, effective_total_weight


def compute_scores(df: pd.DataFrame, effective_total_weight: int) -> dict:
    """Compute core-gap flag, points and %-fit using the new scoring system.
    
    New scoring formula: ClassWt * (1 + EmphMod) * SelfScore
    - ClassWt: Weight based on classification (Essential=3.0, Important=2.0, etc.)
    - EmphMod: Emphasis modifier from -0.5 to +0.5 based on requirement text
    - SelfScore: Self-assessment score from 0-5
    
    Core gap is triggered for:
    - Essential items with SelfScore <= 2
    - Important items with SelfScore <= 1 (optional, can be configured)
    """
    # Configuration for core gap detection
    CORE_GAP_THRESHOLDS = {
        "Essential": 2,  # Score <= 2 is a gap
        "Important": 1,  # Score <= 1 is a gap
        "Desirable": 0,  # No gaps for Desirable
        "Implicit": 0    # No gaps for Implicit
    }
    
    # Check if we're using the new format with ClassWt and EmphMod
    new_format = "ClassWt" in df.columns and "EmphMod" in df.columns
    
    if new_format:
        # New scoring logic with emphasis modifiers
        df["RowScoreRaw"] = df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]
        
        # Core gap detection based on classification and score thresholds
        core_gap_mask = pd.Series(False, index=df.index)
        for class_type, threshold in CORE_GAP_THRESHOLDS.items():
            if threshold > 0:  # Only check if threshold is set
                class_mask = (df["Classification"] == class_type) & (df["SelfScore"] <= threshold)
                core_gap_mask = core_gap_mask | class_mask
        
        core_gap = core_gap_mask.any()
        
        # Get core gap skills if any exist
        core_gap_skills = []
        if core_gap:
            req_col = [col for col in df.columns if "requirement" in col.lower() or "skill" in col.lower()]
            req_col = req_col[0] if req_col else "Requirement"
            core_gap_skills = df.loc[core_gap_mask, [req_col, "Classification", "SelfScore"]].to_dict('records')
        
        # Calculate points and percentage
        actual_points = df["RowScoreRaw"].sum()
        
        # Apply bonus cap (25% of core weight)
        core_weight = df[df["Classification"].isin(["Essential", "Important"])]["ClassWt"].sum()
        bonus_weight = df[df["Classification"].isin(["Desirable", "Implicit"])]["ClassWt"].sum()
        
        # Cap bonus points at 25% of core weight
        max_bonus_points = core_weight * 0.25 * 5  # Max 5 points per bonus item
        actual_bonus_points = df[df["Classification"].isin(["Desirable", "Implicit"])]["RowScoreRaw"].sum()
        
        if actual_bonus_points > max_bonus_points:
            # Scale down bonus points to fit within the cap
            bonus_scale = max_bonus_points / actual_bonus_points if actual_bonus_points > 0 else 0
            df.loc[df["Classification"].isin(["Desirable", "Implicit"]), "RowScoreRaw"] *= bonus_scale
            actual_points = df["RowScoreRaw"].sum()
        
        # Maximum possible score (Essential * 1.5 * 5)
        max_possible_score = 3.0 * 1.5 * 5  # 22.5
        max_points = len(df) * max_possible_score
        pct_fit = (actual_points / max_points) if max_points > 0 else 0.0
        
    else:
        # Original scoring logic (for backward compatibility)
        df["WeightedScore"] = df["Weight"] * df["SelfScore"]
        
        # Original format - use old core gap detection for backward compatibility
        core_gap_mask = (df["Weight"] == 3) & (df["SelfScore"] <= 1)
        core_gap = core_gap_mask.any()
        
        # Get core gap skills if any exist
        core_gap_skills = []
        if core_gap:
            req_col = [col for col in df.columns if "requirement" in col.lower() or "skill" in col.lower()]
            req_col = req_col[0] if req_col else "Requirement"
            core_gap_skills = [{"skill": skill, "Weight": 3, "SelfScore": 1} 
                             for skill in df.loc[core_gap_mask, req_col].tolist()]
        
        # Calculate points with bonus cap for original format
        core_points = df[df["Weight"] >= 2]["WeightedScore"].sum()
        bonus_points = df[df["Weight"] < 2]["WeightedScore"].sum()
        max_bonus = core_points * 0.25  # Cap bonus at 25% of core points
        
        if bonus_points > max_bonus:
            bonus_scale = max_bonus / bonus_points if bonus_points > 0 else 0
            df.loc[df["Weight"] < 2, "WeightedScore"] *= bonus_scale
        
        actual_points = df["WeightedScore"].sum()
        max_points = effective_total_weight * 5  # max self-score is now 5
        pct_fit = actual_points / max_points if max_points > 0 else 0.0

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
        description="Compute fit score from a skill-matrix CSV."
    )
    parser.add_argument(
        "csv", type=Path, help="Path to CSV with Weight & SelfScore columns"
    )
    parser.add_argument(
        "--cap",
        type=float,
        default=0.25,
        help="Bonus cap: ≤1 → percent mode; >1 → row-limit mode (int)",
    )
    args = parser.parse_args()

    df_raw = load_matrix(args.csv)

    # Determine cap mode
    cap_rows = int(args.cap) if args.cap > 1 else None
    cap_pct = None if args.cap > 1 else args.cap

    df_eff, eff_weight = apply_bonus_cap(df_raw, cap_pct, cap_rows)
    metrics = compute_scores(df_eff, eff_weight)

    # ----- Report -----
    pd.set_option("display.max_rows", None)
    print("\nProcessed Matrix (after cap):")
    # Handle both old (WeightedScore) and new (RowScoreRaw) column names
    score_col = "RowScoreRaw" if "RowScoreRaw" in df_eff.columns else "WeightedScore"
    print(
        df_eff[[c for c in df_eff.columns if c != score_col] + [score_col]]
    )

    print("\n" + "="*50)
    print("SCORECARD SUMMARY")
    print("="*50)
    
    # Core gap assessment
    core_gap_status = "YES" if metrics["core_gap"] else "NO"
    print(f"\n1. Core gap present : {core_gap_status}")
    if metrics["core_gap"]:
        print("   ⚠️  At least one must-have skill (Weight 3) was self-scored 0 or 1.")
        print("   ⚠️  Treat as a red flag — address the gap before applying.")
    else:
        print("   ✓  All Weight 3 items are self-scored 2. You clear the 'minimum bar'.")
    
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
        print("\n5. Core Gap Skills (Weight=3, SelfScore≤1):")
        for skill in metrics["core_gap_skills"]:
            print(f"   • {skill}")
        print("\n   Use as a to-do list: supply stronger evidence or up-skill")
        print("   until you can honestly self-score 2 on these items.")
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
        print("1. Focus on closing the core gap skills listed above.")
        print("2. Re-evaluate after addressing these critical skills.")
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

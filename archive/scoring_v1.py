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


def load_matrix(path: Path) -> pd.DataFrame:
    """Load CSV and coerce numeric columns."""
    df = pd.read_csv(path)
    required_cols = {"Weight", "SelfScore"}
    if not required_cols.issubset(df.columns):
        missing = ", ".join(required_cols - set(df.columns))
        raise ValueError(f"CSV missing required columns: {missing}")

    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce").fillna(0).astype(int)
    df["SelfScore"] = pd.to_numeric(df["SelfScore"], errors="coerce").fillna(0).astype(int)
    return df


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------


def apply_bonus_cap(
    df_in: pd.DataFrame,
    cap_pct: float | None = 0.25,
    cap_rows: int | None = None,
) -> tuple[pd.DataFrame, int]:
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
    allowed_bonus_weight = (
        int(math.ceil(core_weight * (cap_pct or 0)))
        if core_weight is not None and cap_pct is not None and core_weight > 0 and cap_pct > 0
        else 0
    )
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
    """Compute core-gap flag, points and %-fit."""
    # Identify core gap skills (Weight == 3 and SelfScore <= 1)
    core_gap_mask = (df["Weight"] == 3) & (df["SelfScore"] <= 1)
    core_gap = core_gap_mask.any()

    # Get the list of core gap skills if any exist
    core_gap_skills = []
    if core_gap:
        # Get the requirement/skill name for each core gap
        req_col = [
            col for col in df.columns if "requirement" in col.lower() or "skill" in col.lower()
        ][0]
        core_gap_skills = df.loc[core_gap_mask, req_col].tolist()

    df["WeightedScore"] = df["Weight"] * df["SelfScore"]

    actual_points = int(df["WeightedScore"].sum())
    max_points = effective_total_weight * 2  # max self-score = 2
    pct_fit = actual_points / max_points if max_points else 0.0

    return {
        "core_gap": core_gap,
        "core_gap_skills": core_gap_skills,
        "actual_points": actual_points,
        "max_points": max_points,
        "pct_fit": pct_fit,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute fit score from a skill-matrix CSV.")
    parser.add_argument("csv", type=Path, help="Path to CSV with Weight & SelfScore columns")
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
    print(df_eff[[c for c in df_eff.columns if c != "WeightedScore"] + ["WeightedScore"]])

    print("\n" + "=" * 50)
    print("SCORECARD SUMMARY")
    print("=" * 50)

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
        if pct >= 0.80
        else "   ✓  Good fit; minor gaps → Apply; line up examples or quick up-skilling"
        if pct >= 0.65
        else "   ⚠️  Possible fit; several gaps → Decide whether to apply now or build skills first"
        if pct >= 0.50
        else "   ⚠️  Significant gaps → Up-skill before investing in an application"
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
    print("\n" + "-" * 50)
    print("RECOMMENDED NEXT STEPS")
    print("-" * 50)

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

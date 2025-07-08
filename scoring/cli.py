"""
Command Line Interface Module
===========================

This module provides the command-line interface for the job_scorer project,
handling user interaction, argument parsing, and orchestrating the scoring process.

Key Components:
- `parse_args()`: Parses command line arguments
- `main()`: Entry point for the CLI application
- `display_results()`: Formats and displays scoring results
- `display_core_gap_analysis()`: Shows detailed core gap information

Usage Examples:
    ```bash
    # Basic usage with auto-detection of CSV format
    python -m scoring data/skills.csv

    # Show version information
    python -m scoring --version

    # Get help
    python -m scoring --help
    ```

Exit Codes:
    0: Success
    1: Error occurred during execution
    2: Invalid command line arguments

Note: This module integrates with `scoring_engine.py` for core logic and
`data_loader.py` for data loading and validation.

All CLI-related logic is isolated here for maintainability and testability.
"""

from __future__ import annotations

import argparse
import sys
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

# Local imports
from .config import CORE_GAP_THRESHOLDS, UI_CONFIG
from .data_loader import load_matrix
from .scoring_engine import compute_scores, compute_scores_enhanced

if TYPE_CHECKING:
    pass


def parse_args() -> Namespace:
    """Parse command line arguments.

    Returns:
        Namespace: Parsed command line arguments

    Exits with code 1 if no arguments are provided or if there's an error.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Score your job application fit against a skill matrix.\n\n"
            "The tool analyzes your self-assessed skills against job requirements\n"
            "and provides a detailed report with recommendations.\n\n"
            "NEW: Strategic positioning enhancements for executive roles available\n"
            "with --enable-enhancements flag for advanced career positioning."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python job-skill-matrix-scoring.py skills.csv\n"
            "  python job-skill-matrix-scoring.py skills.csv --enable-enhancements\n"
            "  python job-skill-matrix-scoring.py skills.csv --enable-enhancements \\\n"
            "    --target-role-level c_suite --proven-strengths cross-functional bioinformatics\n\n"
            "For best results, ensure your CSV follows the required format:\n"
            "  - One requirement per row\n"
            "  - Use valid Classification values\n"
            "  - SelfScore should be an integer 0-5"
        ),
    )

    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to CSV file containing skill matrix data"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 3.0.0 - Strategic Positioning Enhancement Framework",
        help="Show program's version number and exit",
    )

    # Enhancement options
    enhancement_group = parser.add_argument_group("Enhancement Options")

    enhancement_group.add_argument(
        "--enable-enhancements",
        action="store_true",
        help="Enable all strategic positioning enhancements for executive roles"
    )

    enhancement_group.add_argument(
        "--target-role-type",
        choices=["executive", "ic", "hybrid"],
        default="executive",
        help="Target role type for dual-track scoring (default: executive)"
    )

    enhancement_group.add_argument(
        "--years-experience",
        type=int,
        default=20,
        help="Years of professional experience for calibration (default: 20)"
    )

    enhancement_group.add_argument(
        "--target-role-level",
        choices=["c_suite", "senior_executive", "director_vp", "senior_ic"],
        default="senior_executive",
        help="Target role level for calibration (default: senior_executive)"
    )

    enhancement_group.add_argument(
        "--proven-strengths",
        nargs="+",
        help="List of proven cross-functional strengths (e.g., 'cross-functional' 'bioinformatics')"
    )

    try:
        return parser.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


def main() -> None:
    """Main entry point for the job skill matrix scoring tool.

    This function:
    1. Parses command line arguments
    2. Loads and validates the skill matrix CSV
    3. Computes scores and identifies core gaps
    4. Generates a detailed report with recommendations

    Returns:
        None: Outputs results to stdout and exits with appropriate status code

    Raises:
        FileNotFoundError: If the specified CSV file doesn't exist
        PermissionError: If the file cannot be read due to permissions
        ValueError: If the CSV is malformed or contains invalid data
        SystemExit: With status code 1 if an error occurs during processing

    Note:
        This function never returns normally - it always exits with a status code.
    """
    # Parse command line arguments
    args = parse_args()

    # Load and validate the skill matrix
    try:
        if not args.csv_path.exists():
            raise FileNotFoundError(f"File not found: {args.csv_path}")

        df_raw = load_matrix(args.csv_path)

        # Basic validation of the loaded data
        if df_raw.empty:
            raise ValueError("The CSV file is empty or contains no valid data")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "\nPlease ensure the CSV file exists and follows the required format.", file=sys.stderr
        )
        print("Use --help for more information.", file=sys.stderr)
        sys.exit(1)

    # Process the matrix and calculate metrics
    try:
        if args.enable_enhancements:
            metrics = compute_scores_enhanced(
                df_raw,
                enable_enhancements=True,
                target_role_type=args.target_role_type,
                years_experience=args.years_experience,
                target_role_level=args.target_role_level,
                proven_strengths=args.proven_strengths
            )
        else:
            metrics = compute_scores(df_raw)
    except Exception as e:
        print(f"Error calculating scores: {e}", file=sys.stderr)
        print(
            "\nError: The skill matrix data appears to be invalid. Please check your input.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ----- Report -----
    pd.set_option("display.max_rows", None)
    # Display the processed matrix with scores
    print(df_raw[[c for c in df_raw.columns if c != "RowScoreRaw"] + ["RowScoreRaw"]])

    separator = "-" * UI_CONFIG.separator_length
    print(f"\n{separator}")
    if args.enable_enhancements:
        print("ENHANCED STRATEGIC POSITIONING RESULTS".center(UI_CONFIG.separator_length))
        print(f"Role Type: {args.target_role_type.title()} | Experience: {args.years_experience}y | Level: {args.target_role_level.replace('_', ' ').title()}".center(UI_CONFIG.separator_length))
        if args.proven_strengths:
            strengths_text = f"Proven Strengths: {', '.join(args.proven_strengths)}"
            print(strengths_text.center(UI_CONFIG.separator_length))
        print(separator)
        print("VERDICT".center(UI_CONFIG.separator_length))
    else:
        print("VERDICT".center(UI_CONFIG.separator_length))
    print(separator)

    # Core gap status
    core_gap_status = "YES" if metrics["core_gap"] else "NO"
    print(f"\n1. Core gap present : {core_gap_status}")

    if metrics["core_gap"]:
        # Report on each classification with gaps
        essential_gaps = [g for g in metrics["core_gap_skills"] if g.classification == "Essential"]
        important_gaps = [g for g in metrics["core_gap_skills"] if g.classification == "Important"]

        if essential_gaps:
            print(
                f"   {len(essential_gaps)} Essential skill(s) scored ≤ {CORE_GAP_THRESHOLDS['Essential']}."
            )
        if important_gaps:
            print(
                f"   {len(important_gaps)} Important skill(s) scored ≤ {CORE_GAP_THRESHOLDS['Important']}."
            )

        print("   Treat as a red flag — address these gaps before applying.")
    else:
        print("   All essential and important skills meet the minimum score requirements.")

    # Points calculation
    print(f"\n2. Actual points    : {metrics['actual_points']} / {metrics['max_points']}")
    print(f"   • Your weighted evidence of fit: {metrics['actual_points']} points")
    print(f"   • Maximum possible score: {metrics['max_points']} points")

    # Percentage fit
    pct = metrics["pct_fit"]
    print(f"\n3. % Fit            : {pct:.1%}")

    # Add disclaimer about % Fit when core gaps are present
    if metrics["core_gap"]:
        print("   DISCLAIMER: % Fit is misleading when core gaps are present.")
        print("   Address core gaps first before considering the % Fit value.")

    fit_guidance = (
        "   Excellent overall fit → Apply immediately, emphasize strengths"
        if pct >= 0.80
        else "   Good fit; minor gaps → Apply; line up examples or quick up-skilling"
        if pct >= 0.65
        else "   Possible fit; several gaps → Decide whether to apply now or build skills first"
        if pct >= 0.50
        else "   Significant gaps → Up-skill before investing in an application"
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
            print(
                f'   • "{gap.name}" (Classification: {gap.classification}, SelfScore: {gap.self_score})'
            )

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
    print(f"\n{separator}")
    print("RECOMMENDED NEXT STEPS".center(UI_CONFIG.separator_length))
    print(separator)

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

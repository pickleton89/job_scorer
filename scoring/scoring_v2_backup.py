#!/usr/bin/env python3
"""
Job Skill Matrix Scoring Tool - Entry Point
==========================================

A lightweight entry point for the job_scorer project that imports and utilizes
the modular components for scoring job applications against skill matrices.

This tool analyzes your self-assessed skills against job requirements and
provides a detailed report with recommendations.

Version: 2.0.0
Released: 2025-05-20

Usage:
    python scoring_v2.py skills.csv
    python scoring_v2.py --help
    python scoring_v2.py --version

For more information, see the documentation in the docs/ directory.
"""

from __future__ import annotations

import sys

# Import the main CLI function from the modular components
try:
    # Relative imports for package usage
    from .cli import main
except ImportError:
    # Fallback for direct script execution
    try:
        from cli import main
    except ImportError:
        print("Error: Could not import required modules.", file=sys.stderr)
        print("Please ensure you're running from the correct directory.", file=sys.stderr)
        sys.exit(1)


def run() -> None:
    """Entry point wrapper for the scoring tool."""
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()

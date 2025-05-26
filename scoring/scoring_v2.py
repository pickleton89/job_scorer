#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Skill Matrix Scorer - Lightweight Entry Point
=================================================

This module serves as the main entry point for the job skill matrix scoring tool.
It provides a thin wrapper around the CLI module for backward compatibility.

Note: Most of the implementation has been modularized into separate modules:
- `scoring.cli`: Command line interface and user interaction
- `scoring.scoring_engine`: Core scoring algorithms and business logic
- `scoring.data_loader`: CSV loading and validation
- `scoring.config`: Configuration and settings

Usage:
    ```bash
    # Basic usage (auto-detects v1/v2 format)
    python -m scoring.scoring_v2 skills.csv
    
    # Show version
    python -m scoring.scoring_v2 --version
    
    # Get help
    python -m scoring.scoring_v2 --help
    ```

For programmatic usage, import directly from the specific modules:
    ```python
    from scoring.data_loader import load_matrix
    from scoring.scoring_engine import compute_scores
    
    # Load and score a skill matrix
    df = load_matrix("skills.csv")
    result = compute_scores(df)
    ```

Version: 2.0.0
"""

import sys
from pathlib import Path

# Add parent directory to path to allow package imports when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try relative import first (when run as part of the package)
    from .cli import main
except ImportError:
    # Fall back to absolute import (when run directly)
    try:
        from cli import main
    except ImportError:
        print("Error: Could not import required modules.", file=sys.stderr)
        print("Please ensure you're running from the correct directory.", file=sys.stderr)
        sys.exit(1)

__version__ = "2.0.0"

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

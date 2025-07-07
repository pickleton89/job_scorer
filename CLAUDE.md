# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Job Skill Matrix Scorer** - A Python utility for evaluating job fit based on skill matrices. It helps job seekers and career advisors assess how well a candidate's skills match job requirements through a sophisticated scoring system with emphasis detection and core gap analysis.

## Development Commands

All commands should be run with `uv` as the package manager:

```bash
# Install dependencies
uv sync

# Run tests with coverage (requires 80% minimum)
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_scoring_engine.py

# Run single test
uv run pytest tests/unit/test_scoring_engine.py::test_specific_function

# Type checking
uv run mypy scoring/

# Linting
uv run ruff check .

# Run the scorer with a CSV file
uv run python -m scoring data/matrix.csv

# Run via installed command
uv run job-scorer data/matrix.csv

# Test CI locally (simulates GitHub Actions)
./scripts/test_ci_locally.sh
```

## Architecture

The project follows a modular Python package structure with strong typing throughout:

### Core Modules
- **scoring/scoring_engine.py**: Core scoring algorithms including emphasis detection, classification weighting, and bonus capping
- **scoring/scoring_v2.py**: Lightweight CLI entry point that uses the scoring engine
- **scoring/config.py**: Centralized configuration with classification weights (Essential: 3.0, Important: 2.0, Desirable: 1.0, Implicit: 0.5)
- **scoring/data_loader.py**: CSV validation and loading with support for v1 and v2 formats
- **scoring/cli.py**: Command-line interface implementation

### Key Concepts
1. **CSV Format Support**: Handles both v1 (legacy) and v2 formats with automatic detection
2. **Emphasis Detection**: Uses keywords like "expert", "extensive" for high emphasis (+0.5 modifier) and "basic", "familiarity" for low emphasis (-0.5 modifier)
3. **Core Gap Analysis**: Identifies skills where self-score is below threshold (Essential ≤ 2, Important ≤ 1)
4. **Bonus Capping**: Limits bonus points to 25% of core points to prevent over-inflation
5. **Scoring Formula**: `base_score = self_score * classification_weight * (1 + emphasis_modifier)`

### Testing
- Uses pytest with 80% minimum coverage requirement
- Tests are in `tests/unit/` with comprehensive coverage of all modules
- Integration tests verify end-to-end functionality
- Run with `uv run pytest` to execute full test suite with coverage report

### Type Safety
- Comprehensive type hints using Python 3.10+ features
- Strict mypy configuration enforcing full type coverage
- Uses `py.typed` marker for PEP 561 compliance
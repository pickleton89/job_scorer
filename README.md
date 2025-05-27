# Job Skill Matrix Scorer

A Python utility for evaluating job fit based on skill matrices. This tool helps job seekers and career advisors assess how well a candidate's skills match a job's requirements.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for data loading, scoring, and CLI
- **Advanced Scoring System**: Evaluates skills on a 0-5 scale with emphasis modifiers
- **Core-Gap Analysis**: Identifies critical skill gaps in Essential requirements
- **Optional-Skill Cap**: Weight from `Desirable`/`Implicit` rows is limited to 25% of core points
- **Row Normalisation**: Each requirement is scaled against a 22.5 max to keep scoring fair
- **Flexible Input**: Supports both legacy and new CSV formats
- **Detailed Reporting**: Provides clear feedback on job fit and improvement areas
- **Backward Compatible**: Works with both old and new scoring systems
- **Type Safe**: Comprehensive type hints with `mypy` support for better code quality and IDE support
- **Modern Python**: Utilizes Python's latest typing features including type aliases and type guards

## Quick Start

### Prerequisites
- Python 3.8+
- pandas (install via `pip install pandas`)
- mypy (for type checking, install via `pip install mypy`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/job_scorer.git
cd job_scorer

# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### Command Line Interface
```bash
# Basic usage (auto-detects v1/v2 format)
python -m scoring data/matrix.csv

# Or use the direct CLI module
python -m scoring.cli data/matrix.csv

# For v2-specific scoring
python -m scoring.scoring_v2 data/matrix.csv
```

#### Programmatic Usage

```python
from pathlib import Path
from scoring import load_matrix, compute_scores

# Load and validate a skill matrix
df = load_matrix(Path("data/matrix.csv"))

# Compute scores
result = compute_scores(df)

# Access the results
print(f"Core gap present: {result.core_gap}")
print(f"Percentage fit: {result.pct_fit:.1%}")
```

## Project Structure

```
job_scorer/
├── scoring/                  # Source code package
│   ├── __init__.py          # Package initialization and public API
│   ├── cli.py               # Command line interface
│   ├── config.py            # Configuration and constants
│   ├── data_loader.py       # CSV loading and validation
│   ├── scoring_engine.py    # Core scoring algorithms
│   └── scoring_v2.py        # Lightweight entry point
├── data/                    # Example/reference CSVs
├── tests/                   # Test scripts and test data
│   └── unit/               # Unit tests
│       ├── test_cli_error_handling.py
│       ├── test_emphasis.py
│       ├── test_scoring.py
│       └── test_validation.py
├── docs/                    # Documentation
│   ├── scoring_v2_refactor_plan.md
│   └── type_hinting_improvements.md  # Type system documentation
├── README.md
├── CHANGELOG.md
└── requirements.txt
```

## Type Checking

The project uses Python's type hints and `mypy` for static type checking. To run type checking:

```bash
# Install mypy if not already installed
pip install mypy

# Run type checking
mypy scoring/
```

For development, consider setting up a pre-commit hook to run type checking before each commit. See [Type Hinting Documentation](docs/type_hinting_improvements.md) for more details.

- Place your own skills/job matrix CSVs in the `data/` directory or specify the path as needed.
- All scoring scripts are now organized under the `scoring/` package for clarity.
- Test data and test runner scripts are in `tests/`.
- See [docs/usage.md](docs/usage.md) for extended examples (if present).

## CSV Formats

### Version 2 (Recommended)

*Column order doesn’t matter; the script matches by header.*

```csv
Requirement,Classification,SelfScore,Notes
Expert in Python,Essential,5,Used in production projects
Familiarity with SQL,Important,3,Some coursework
Documentation,Desirable,4,Contributed to team docs
```

**Required columns:**
- `Requirement`: The skill or job requirement (free text; keywords like "expert", "familiarity", "proficient" affect emphasis; *case-insensitive*)
- `Classification`: One of `Essential`, `Important`, `Desirable`, `Implicit`
- `SelfScore`: Your self-assessed proficiency (0-5)

**Optional columns:**
- `Notes`: Any evidence or comments
- `Weight`: (legacy, ignored in v2)
- `EmphasisOverride`: Manually set emphasis if you don’t want keyword detection (**must be +0.5 / 0 / -0.5**)

**Emphasis Keywords:**
The script automatically detects emphasis using keywords in the `Requirement` column (case-insensitive):
- **Critical**: "expert", "deep", "mastery"
- **Minimal**: "familiarity", "exposure", "basic"
- **Standard**: (no keyword needed; e.g., "proficient", "experience", or any other text)

The `EmphasisOverride` column can be used to manually specify +0.5, 0, or -0.5 if you want to override keyword detection.

> *Note:* In v2 the script first caps bonus rows (≤25 % of core points)  
> and then divides every row by the theoretical max (22.5).  
> That’s why the max total in this example is 67.5, not a simple sum of weights.

**Usage (v2):**
```bash
python job-skill-matrix-scoring-v2.py your_skills.csv
```
Or use the generic entry point:
```bash
python job-skill-matrix-scoring.py your_skills.csv
```

**Backward compatibility:**
- The v1 script and format are still supported for legacy data and tests.
- Legacy CSVs **ignore** emphasis and normalisation; results therefore can’t be directly compared to v2 scores.

### Version 1 (Legacy)
```csv
Requirement,Weight,SelfScore,Notes
Python programming,3,4,Core language
Data analysis,2,2,Basic experience
Project management,1,1,No formal experience
```

**Columns**:
- `Requirement`: The skill or requirement
- `Weight`: Importance (3=High, 2=Medium, 1=Low)
- `SelfScore`: Your self-assessment (0-2)
- `Notes`: Optional comments

## Scoring System

### Version 2 (New)
- **Formula**: `ClassWt * (1 + EmphMod) * SelfScore`
  - `ClassWt`: 3.0 (Essential), 2.0 (Important), 1.0 (Desirable), 0.5 (Implicit)
  - `EmphMod`: +0.5 (Critical), 0.0 (Standard), -0.5 (Minimal)
  - `SelfScore`: 0-5 rating
- **Core Gap**: Triggered when any Essential item has **SelfScore ≤ 1**

### Version 1 (Legacy)
- **Formula**: `Weight * SelfScore`
  - `Weight`: 3 (High), 2 (Medium), 1 (Low)
  - `SelfScore`: 0-2 rating
- **Core Gap**: Triggered when Weight=3 items have SelfScore ≤ 1

## Example Output

```
Processed Matrix (after cap):
          Requirement Classification  SelfScore  ... EmphMod  Weight  RowScoreRaw
0  Python programming      Essential          4  ...     0.5     3.0         18.0
1       Data analysis      Important          2  ...     0.0     2.0          4.0
2  Project management      Desirable          1  ...    -0.5     1.0          0.5

[3 rows x 8 columns]

==================================================
SCORECARD SUMMARY
==================================================

1. Core gap present : NO
   ✓  All Essential items meet minimum requirements

2. Actual points    : 22.5 / 67.5
   • Your weighted evidence of fit: 22.5 points
   • Maximum possible score: 67.5 points

3. % Fit            : 33.3%
   ⚠️  Significant gaps → Up-skill before applying

4. Verdict          : Needs development — focus on skill building
```

## Output

The tool provides:
- A core-gap analysis
- A percentage fit score
- Detailed feedback on your match

## License

Distributed under the MIT License. See `LICENSE` for details.

## Development

### Running Tests

Run the full test suite with coverage:
```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=scoring --cov-report=term-missing tests/
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Run linter
ruff check .

# Auto-format code
black .
# Sort imports
isort .
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code passes all tests and follows the project's coding standards.

## Contributing

Contributions are welcome! Please open an issue to discuss your ideas.

## API Reference

### Core Modules

#### `scoring` Package

```python
# Main entry point
from scoring import (
    # Core functions
    load_matrix,      # Load and validate skill matrix CSV
    compute_scores,   # Calculate scores from a DataFrame
    
    # Data classes
    CoreGapSkill,     # Represents a skill with a core gap
    
    # Configuration
    SCORING_CONFIG,   # Default scoring configuration
    UI_CONFIG,        # UI display settings
    
    # CLI
    main,             # Main CLI entry point
    parse_args,       # Parse command line arguments
)
```

#### `scoring.data_loader`

```python
from scoring.data_loader import load_matrix

# Load and validate a skill matrix CSV
df = load_matrix("path/to/matrix.csv")
```

#### `scoring.scoring_engine`

```python
from scoring.scoring_engine import compute_scores, CoreGapSkill, emphasis_modifier

# Compute scores from a DataFrame
result = compute_scores(df)

# Check for core gaps
if result.core_gap:
    print("Critical skill gaps found!")
```

## Version

Current version: 2.0.0 (Supports both v1 and v2 formats)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

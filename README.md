# Job Skill Matrix Scorer

A Python utility for evaluating job fit based on skill matrices. This tool helps job seekers and career advisors assess how well a candidate's skills match a job's requirements.

## Features

- **Advanced Scoring System**: Evaluates skills on a 0-5 scale with emphasis modifiers
- **Core-Gap Analysis**: Identifies critical skill gaps in Essential requirements
- **Flexible Input**: Supports both legacy and new CSV formats
- **Detailed Reporting**: Provides clear feedback on job fit and improvement areas
- **Backward Compatible**: Works with both old and new scoring systems

## Quick Start

1. **Prerequisites**
   - Python 3.8+

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/job_scorer.git
   cd job_scorer
   
   # Set up a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install pandas
   ```

3. **Basic Usage**
   ```bash
   python job-skill-matrix-scoring.py your_skills.csv
   ```

## CSV Formats

### Version 2 (Recommended)
```csv
Requirement,Classification,SelfScore,Emphasis,Notes
Python programming,Essential,4,Critical,Core language
Data analysis,Important,2,Standard,Basic experience
Project management,Desirable,1,Minimal,No formal experience
```

**Columns**:
- `Requirement`: The skill or requirement
- `Classification`: `Essential`/`Important`/`Desirable`/`Implicit`
- `SelfScore`: Your self-assessment (0-5)
- `Emphasis`: `Critical`/`Standard`/`Minimal` (affects scoring weight)
- `Notes`: Optional comments

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
- **Core Gap**: Triggered when Essential items have SelfScore ≤ 2

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

[Specify your license here]

## Contributing

Contributions are welcome! Please open an issue to discuss your ideas.

## Version

Current version: 2.0.0 (Supports both v1 and v2 formats)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

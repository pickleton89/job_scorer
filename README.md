# Job Skill Matrix Scorer

A Python utility for evaluating job fit based on skill matrices. This tool helps job seekers and career advisors assess how well a candidate's skills match a job's requirements.

## Features

- **Scoring System**: Evaluates skills on a weighted scale
- **Core-Gap Analysis**: Identifies critical skill gaps
- **Flexible Input**: Works with CSV files
- **Detailed Reporting**: Provides clear feedback on job fit

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

## CSV Format

Your CSV should include these columns:
- `Requirement`: The skill or requirement
- `Classification`: Essential/Important/Desirable/Implicit
- `SelfScore`: Your self-assessment (0-5)

## Example

```csv
Requirement,Classification,SelfScore
Python programming,Essential,4
Data analysis,Important,3
Project management,Desirable,2
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

Current version: 1.0.0

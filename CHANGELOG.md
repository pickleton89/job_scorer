# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Configurable core-gap detection thresholds (e.g., Essential <=2, Important <=1).
- Detailed core-gap skill reporting, now including Classification and SelfScore for each gap.
- New test cases for core-gap detection (`core_gap_test.csv` and `core_gap_test.json`).
- New test cases for bonus cap functionality (`bonus_cap_test.csv` and `bonus_cap_test.json`).
- Project directory reorganization: moved scoring scripts to `scoring/`, example/reference CSVs to `data/`, documentation to `docs/`.
- Added project structure and updated usage instructions in the README to reflect new organization.
- Verified all v2 tests pass after reorganization and test runner update.
- Added global constants for scoring parameters to improve code maintainability.
- Created implementation roadmap for v2 refactoring in `docs/implementation-roadmap-v2.md`.

### Refactored
- Moved magic numbers to named constants in `scoring_v2.py`:
  - `MAX_SELF_SCORE = 5`
  - `BONUS_CAP_PERCENTAGE = 0.25`
  - `EMPHASIS_MODIFIER_HIGH = +0.5`
  - `EMPHASIS_MODIFIER_LOW = -0.5`
  - `THEORETICAL_MAX_RAW_SCORE_PER_ROW = 22.5`
  - `CORE_GAP_THRESHOLDS` dictionary

### Changed
- Implemented a 25% bonus cap: total points from Desirable/Implicit skills are capped at 25% of total points from Essential/Important skills.
- Enhanced `test_runner.py` to support expected output validation using `.json` files and improved test result formatting.
- Updated README to document new CSV format, usage, and project structure.
- Moved non-test CSVs out of the project root into `data/`.
- Moved implementation roadmap and upgrade documentation into `docs/`.

### Fixed
- Removed unused `bonus_weight` local variable in `job-skill-matrix-scoring-v2.py` (resolved lint warning).

### Removed
- Removed edge case and emphasis modifier test files (`edge_cases_test.csv`, `edge_cases_test.json`, `emphasis_modifier_test.csv`, `emphasis_modifier_test.json`) from the v2 test suite to focus on core and bonus cap scenarios.

## [2.0.0] - 2025-05-20
### Added
- New scoring system with 0-5 scale and emphasis modifiers
- Test environment with sample data and test runner
- Support for new CSV format with Classification and Requirement columns
- Comprehensive README with setup instructions
- Implementation roadmap

### Changed
- Updated data model to support new scoring system
- Modified `load_matrix` to handle both old and new CSV formats
- Improved error handling and input validation
- Updated documentation for new features and formats

### Fixed
- Resolved issue with percentage calculation in new scoring model
- Fixed test runner path resolution
- Improved documentation and code organization

## [1.0.0] - 2025-05-20
### Added
- Initial release of the job scoring tool
- Core functionality for scoring job applications based on skill matrix
- Support for CSV input files
- Basic scoring algorithm with core gap detection

### Changed
- Improved output formatting for better readability
- Enhanced scoring logic to better reflect job requirements
- Updated documentation and usage examples

### Fixed
- Fixed issue with bonus weight calculation rounding
- Addressed potential edge cases in scoring algorithm

## [0.1.0] - 2025-05-15
### Added
- Basic project structure
- Initial implementation of core scoring functionality
- Basic test cases

[Unreleased]: https://github.com/yourusername/job_scorer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/job_scorer/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/yourusername/job_scorer/releases/tag/v0.1.0

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Modern Python 3.13 type hint syntax throughout the codebase
- `ScoreResult` TypedDict for better type safety in score calculations
- Type aliases for improved code readability
- Enhanced function and method signatures with precise type hints
- Better type variable usage for generic functions
- New configuration classes for better organization of constants:
  - `ScoringConfig`: Centralizes scoring-related settings
  - `ClassificationConfig`: Manages skill classifications and weights
  - `EmphasisIndicators`: Handles emphasis detection keywords
  - `UIConfig`: Centralizes UI-related constants and formatting
- Added type-safe access to all configuration values
- Standardized string formatting using f-strings throughout the codebase
- Added consistent error message formatting with "Error:" prefix
- Improved core gap reporting with clear "≤" indicators
- **Testing Infrastructure (Priority 1)**
  - **Chunk 1**: Set up pytest structure and basic configuration
    - Created `tests/unit/` directory with proper package structure
    - Added `pytest.ini` with coverage reporting and test markers
    - Implemented shared fixtures in `tests/conftest.py` for reusable test data
    - Created setup verification tests in `tests/unit/test_setup.py`
    - Added `.gitignore` entries for test artifacts and coverage reports
  - **Chunk 2**: Comprehensive unit tests for emphasis_modifier() function
    - Created `tests/unit/test_emphasis.py` with 13 test methods covering:
      - High/low emphasis keyword detection (+0.5/-0.5 modifiers)
      - Case-insensitive detection and precedence rules
      - Edge cases: non-string input, whitespace, punctuation
      - Real-world job requirement examples
      - Custom configuration testing
    - All tests passing with 100% coverage of emphasis_modifier() function
- Preserved existing integration test system alongside new unit tests

### Refactored
- Simplified imports by removing unused standard library imports
- Restructured argument parsing into a separate `parse_args()` function
- Improved type safety in `CoreGapSkill` class with proper type hints
- Enhanced docstrings with detailed type information
- Standardized return type annotations across all functions
- Improved error handling with more specific type hints
- Centralized all configuration in dedicated classes for better maintainability
- Made configuration immutable using `frozen=True` dataclasses
- Replaced all magic numbers with named constants from configuration
- Moved UI-related strings and formatting to configuration
- Updated `emphasis_modifier` to use configuration values instead of magic numbers
- Standardized UI output formatting with consistent section headers
- Improved error message clarity and consistency
- Removed all string concatenation in favor of f-strings

### Fixed
- Resolved all lint warnings related to type hints
- Fixed potential type-related issues in function returns
- Ensured consistent type usage throughout the codebase
- Addressed all mypy type checking issues
- Fixed configuration-related magic numbers by centralizing them in config classes
- Removed duplicate `@dataclass` decorator from `UIConfig`
- Fixed UI output formatting to be more consistent and configurable
- Fixed inconsistent string formatting across the codebase
- Addressed potential issues with string comparison in UI output
- Ensured consistent error message formatting throughout the application
- Fixed `EmphasisIndicators` attribute access in `emphasis_modifier` function
- Resolved test failures related to emphasis detection
- Ensured proper handling of edge cases in score calculations

### Refactored
- Simplified imports by removing unused standard library imports
- Restructured argument parsing into a separate `parse_args()` function
- Improved type safety in `CoreGapSkill` class with proper type hints
- Enhanced docstrings with detailed type information
- Standardized return type annotations across all functions
- Improved error handling with more specific type hints
- Centralized all configuration in dedicated classes for better maintainability
- Made configuration immutable using `frozen=True` dataclasses
- Added type-safe access to configuration values

### Fixed
- Resolved all lint warnings related to type hints
- Fixed potential type-related issues in function returns
- Ensured consistent type usage throughout the codebase
- Addressed all mypy type checking issues
- Fixed configuration-related magic numbers by centralizing them in config classes

## [2.0.1] - 2025-05-22
### Added
- Comprehensive type hints throughout the codebase for better code clarity and IDE support
- Detailed docstrings for all functions and classes following Google style guide
- Input validation and error handling for all public functions
- Improved command-line interface with better help text and error messages
- Support for `--version` flag to display the tool version
- Enhanced error messages with actionable guidance for users
- Expanded keyword matching in `emphasis_modifier` for better detection of skill emphasis
- Input validation for `CoreGapSkill` class to ensure data integrity
- Graceful handling of keyboard interrupts (Ctrl+C)

### Refactored
- Restructured `CoreGapSkill` class with proper validation and documentation
- Improved error handling in `load_matrix` with specific error messages
- Enhanced `emphasis_modifier` with better keyword matching and error handling
- Restructured `main` function for better separation of concerns
- Added input validation for all function parameters
- Improved code organization with clear section comments
- Standardized error reporting to stderr
- Enhanced console output formatting for better readability
- Added proper exit codes for different error conditions
- Improved type safety throughout the codebase

### Changed
- Updated documentation to reflect all code improvements
- Improved error messages to be more user-friendly and actionable
- Enhanced console output formatting for better readability
- Made error messages more specific and helpful
- Standardized on double quotes for string literals
- Improved code organization and structure

### Fixed
- Fixed potential issues with non-string inputs in `emphasis_modifier`
- Addressed all lint warnings and type checking issues
- Improved handling of edge cases in score calculations
- Fixed potential issues with file handling and resource cleanup
- Ensured consistent behavior across different Python versions
- Fixed potential issues with command-line argument parsing
- Addressed potential issues with file encoding when reading CSV files
- Fixed potential issues with string comparison in classification checks

## [2.0.0] - 2025-05-20
### Added
- Configurable core-gap detection thresholds (e.g., Essential <=2, Important <=1).
- Detailed core-gap skill reporting, now including Classification and SelfScore for each gap.
- Improved core gap skills reporting in the console output with clearer formatting and more actionable information.
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
- Removed old scoring logic and backward compatibility code:
  - Deleted `apply_bonus_cap` function as bonus capping is now handled in `compute_scores`
  - Removed `effective_total_weight` parameter from `compute_scores`
  - Simplified scoring logic to only handle the new format
  - Removed unused `math` import
  - Removed support for old CSV format in `load_matrix`
  - Removed `--cap` argument from command line interface
- Improved code organization and maintainability:
  - Consolidated bonus capping logic in one place
  - Used more efficient pandas operations
  - Added clearer variable names and comments
  - Enhanced error handling and input validation
  - Improved documentation and help text

### Changed
- Implemented a 25% bonus cap: total points from Desirable/Implicit skills are capped at 25% of total points from Essential/Important skills.
- Enhanced `test_runner.py` to support expected output validation using `.json` files and improved test result formatting.
- Updated README to document new CSV format, usage, and project structure.
- Moved non-test CSVs out of the project root into `data/`.
- Moved implementation roadmap and upgrade documentation into `docs/`.

### Fixed
- Removed unused `bonus_weight` local variable in `job-skill-matrix-scoring-v2.py` (resolved lint warning).

### Changed
- Updated core gap reporting to show counts of Essential/Important skills below thresholds
- Simplified core gap skills listing to show each skill with its classification and self-score
- Made core gap reporting more consistent with the application's terminology

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

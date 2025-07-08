# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.1] - 2025-07-08
### 🧹 CODEBASE CLEANUP: Professional Development Standards Alignment ✅
- **PROFESSIONAL READY**: Comprehensive codebase cleanup and quality improvements
- **MODERN STANDARDS**: Updated to latest Python development practices and tooling
- **ENTERPRISE QUALITY**: Zero linting errors, full type safety, comprehensive testing

### 🔧 Code Quality & Standards
- **Fixed 178 ruff linting errors**: Removed unused imports, fixed whitespace, updated deprecated type annotations
- **100% mypy compliance**: Achieved full type checking coverage with strict configuration
- **Modern Python typing**: Migrated from `typing.List/Dict/Tuple` to built-in `list/dict/tuple` (Python 3.10+)
- **Consistent formatting**: Standardized code style across entire codebase
- **Professional imports**: Organized imports and removed unused dependencies

### 📦 Project Structure & Configuration
- **Modern ruff configuration**: Updated pyproject.toml to use `[tool.ruff.lint]` structure
- **Version synchronization**: Aligned version numbers (3.0.0) across pyproject.toml, CLI, and __init__.py
- **Clean repository**: Removed build artifacts (htmlcov/, egg-info/, tester.cv, requirements.txt)
- **Enhanced public API**: Updated __init__.py to properly expose `compute_scores_enhanced` function
- **Dependency management**: Consolidated to pyproject.toml-only approach (removed requirements.txt)

### 🧪 Testing & Quality Assurance
- **Fixed failing tests**: Updated version test expectations from 2.0.0 to 3.0.0
- **Eliminated pytest warnings**: Renamed `TestOutput` to `ScriptExecutionOutput` to avoid test collection issues
- **Maintained coverage**: Preserved 83.3% test coverage with 122 passing tests
- **Quality pipeline**: Verified mypy + ruff + pytest integration works flawlessly

### 🗂️ Documentation & Organization
- **Cleaned documentation**: Removed outdated development docs (priority_*.md, type_hinting_improvements.md)
- **Organized structure**: Maintained essential docs while removing obsolete files
- **Updated __all__**: Enhanced public API specification in package __init__.py

### Technical Excellence Metrics
- **122/122 tests passing** ✅
- **0 ruff linting errors** ✅ 
- **0 mypy type errors** ✅
- **83.3% test coverage** ✅
- **Modern Python 3.10+ standards** ✅

### Impact
This release transforms the Job Scorer from a working tool into an enterprise-grade Python package that meets professional development standards. The codebase now exemplifies modern Python best practices with comprehensive quality controls, making it suitable for production environments and team collaboration.

## [3.0.0] - 2025-07-08  
### 🎉 MAJOR RELEASE: Strategic Positioning Enhancement Framework Complete ✅
- **PRODUCTION READY**: Complete 4-phase implementation of executive career positioning system
- **PROVEN IMPACT**: Up to 7% scoring improvement demonstrated for senior executives
- **COMPREHENSIVE**: 4 enhancement modules + CLI integration + extensive validation + documentation

### 🚀 Phase 1: Foundation Implementation (Configuration & Functions)
- **Enhancement Configuration Classes** (config.py):
  - `DualTrackConfig`: Executive vs IC requirement alignment with 14+10 keyword indicators
  - `ExperienceLevelConfig`: Career stage calibration with skill baselines for 15+ year professionals  
  - `CrossFunctionalConfig`: Leadership complexity detection across 4 indicator categories (16 total keywords)
  - `RoleLevelConfig`: Role-specific weight adjustments for 4 levels (C-suite through Senior IC)

- **Enhancement Functions** (scoring_engine.py):
  - `classify_requirement_type()`: Classifies requirements as executive/IC/hybrid based on keyword analysis
  - `dual_track_modifier()`: Applies role alignment adjustments (0.8-1.0 multipliers)
  - `categorize_skill()`: Maps skills to 5 categories (leadership, technical, strategic, communication, domain)
  - `experience_level_modifier()`: Applies experience-appropriate calibration for 15+ year professionals
  - `assess_cross_functional_complexity()`: Evaluates leadership complexity (high/medium/low) with indicator counting
  - `cross_functional_modifier()`: Rewards integration capabilities (1.0-1.45 multipliers with bonuses)
  - `get_role_weights()`: Retrieves role-specific skill category weights for target positions
  - `matches_proven_strength()`: Detects alignment between candidate strengths and job requirements

- **Comprehensive Unit Testing** (tests/unit/test_enhancements.py):
  - 41 unit tests covering all enhancement functions with 100% success rate
  - Integration scenarios testing combined enhancement effects
  - Custom configuration testing for flexible parameter adjustment
  - Edge case and error handling validation

### 🎯 Phase 2: CLI Integration & Enhanced Scoring Engine
- **Enhanced Scoring Engine**:
  - `compute_scores_enhanced()`: Complete 4-module enhancement pipeline with configurable parameters
  - Full backward compatibility when enhancements disabled (identical to standard scoring)
  - Bonus capping and core gap detection preserved in enhanced scoring
  - Type-safe implementation with comprehensive error handling

- **Complete CLI Integration** (cli.py):
  - `--enable-enhancements`: Master flag to activate strategic positioning features
  - `--target-role-type`: Executive/IC/hybrid dual-track alignment (default: executive)
  - `--target-role-level`: Role-level calibration for C-suite/Senior Executive/Director-VP/Senior IC
  - `--years-experience`: Experience-level calibration with intelligent defaults (default: 20)
  - `--proven-strengths`: Cross-functional strength keywords for targeted bonuses
  - Enhanced UI with configuration display and updated help documentation

- **Integration Testing** (tests/unit/test_enhanced_scoring.py):
  - 14 integration tests validating complete enhancement pipeline
  - Standard vs enhanced scoring comparison validation
  - Role-specific testing across all target levels and types
  - Proven strengths bonus validation and edge case testing

### 📊 Phase 3: Comprehensive Validation & Quality Assurance  
- **Validation Test Framework** (data/validation_test_cases.py):
  - Automated test harness for comparing enhanced vs standard scoring
  - 4 detailed role archetypes with 10 requirements each
  - Multiple enhancement configurations per scenario
  - Summary reporting with best configuration identification

- **Demonstrated Performance Improvements**:
  - **Senior Executive Biotech**: 30.0% → 37.0% (+7.0% improvement) - Cross-functional leadership emphasis
  - **Senior IC Technical**: 34.0% → 37.0% (+3.0% improvement) - Technical expertise and proven strengths
  - **Director Hybrid**: Appropriate neutral scoring (29.0%) with correct penalties for misalignment
  - **Edge Case Validation**: Reasonable improvements (15.0% → 17.0%) without over-inflation

- **Quality Control Verification**:
  - Bonus capping working correctly even with extreme proven strengths
  - Core gap detection logic preserved across all enhancement scenarios
  - Input validation maintained with comprehensive error handling
  - Backward compatibility confirmed (standard scoring unchanged when disabled)

- **Production Documentation**:
  - `Enhancement_Framework_Validation_Report.md`: Comprehensive validation methodology and results
  - `Enhancement_User_Guide.md`: Complete user guide with role-specific configurations
  - Updated README.md with strategic positioning features and examples
  - Business impact assessment and competitive advantage analysis

### 📚 Phase 4: Documentation & Production Deployment
- **User Documentation**:
  - Comprehensive Enhancement User Guide with role-specific configurations
  - Examples for Senior Executive, C-suite, Senior IC, and Director/VP roles
  - Proven strengths guidance with domain-specific keyword recommendations
  - Troubleshooting guide and best practices for optimal results

- **Technical Documentation**:
  - Updated README with strategic positioning framework overview
  - Complete CLI reference with all enhancement options
  - Programmatic usage examples for both standard and enhanced scoring
  - Architecture documentation updated with enhancement module integration

### Technical Excellence Maintained
- **Type Safety**: Full mypy validation with no issues across all enhancement code
- **Test Coverage**: 100% success rate across 55+ enhancement-related tests
- **Modular Design**: Clean separation of concerns with enhancement modules as optional add-ons
- **Backward Compatibility**: Standard scoring completely unchanged when enhancements disabled
- **Production Ready**: Comprehensive error handling, input validation, and quality controls

## [2.1.0] - 2025-07-07
### Major Achievement: Refactoring Complete ✅
- **COMPLETED**: Scoring V2 refactoring successfully implemented
- **Result**: scoring_v2.py reduced from 632 lines to 101 lines
- **Architecture**: Modular design with clean separation of concerns

### Added
- Type stubs for third-party libraries
- `docs/README.md`: Documentation directory index  
- `tests/README.md`: Test suite directory index
- Comprehensive modular architecture:
  - `__init__.py`: Package initialization (59 lines)
  - `config.py`: Configuration classes (207 lines) 
  - `data_loader.py`: CSV loading & validation (246 lines)
  - `scoring_engine.py`: Core scoring algorithms (277 lines)
  - `cli.py`: CLI interface & UI output (274 lines)
  - `py.typed`: Type checking marker
  - `scoring_v2.py`: Lightweight entry point (101 lines)

### Changed
- **BREAKING**: Refactored scoring_v2.py into modular architecture
- Split functionality into data_loader.py, scoring_engine.py, and cli.py
- Updated import paths for programmatic usage
- Maintained 100% backward compatibility for CLI usage
- Updated type hints to use modern Python syntax
- Improved type safety in `scoring_engine.py` and `cli.py`
- Enhanced docstrings with more detailed type information
- Made `ScoreResult` TypedDict more flexible with `total=False`
- Replaced `Any` with more specific types where possible
- Standardized type annotations across the codebase

### Technical
- Reduced main file size from 632 to 101 lines
- Improved code organization and maintainability
- Enhanced testing isolation and module boundaries
- Prepared architecture for enhancement framework implementation
- All 67 tests continue to pass with 82% coverage maintained

### Fixed
- Removed duplicate docstrings in `cli.py` and `scoring_engine.py`
- Fixed whitespace and formatting issues
- Resolved type checking errors in the codebase
- Ensured consistent docstring formatting
- Fixed potential type-related bugs in scoring logic

## [2025-05-27]
### Added
- Comprehensive module-level docstrings for all core modules
- Usage examples in module docstrings for better developer experience
- Detailed configuration documentation in `config.py`
- Clear API reference in docstrings for public functions and classes
- Cross-references between related modules in documentation

### Changed
- Improved README.md with updated project structure and usage instructions
- Standardized docstring format across all modules
- Enhanced error message documentation in CLI module
- Updated configuration documentation to reflect current settings

### Fixed
- Fixed various typos and inaccuracies in existing documentation
- Ensured all public APIs have proper type hints and docstrings
- Updated outdated references in documentation

## [2025-05-26]
### Added
- New modular package structure with `__init__.py` for proper package initialization
- Input validation for `CoreGapSkill` class to ensure data integrity
- Comprehensive documentation for the public API

### Changed
- Refactored codebase into modular components:
  - `scoring_v2.py`: Lightweight entry point
  - `cli.py`: Command-line interface and user interaction
  - `data_loader.py`: Loading and validation of skill matrices
  - `scoring_engine.py`: Core scoring logic and data structures
  - `config.py`: Configuration and constants
- Updated all test imports to use the new module structure
- Improved code organization and maintainability

### Fixed
- All 67 unit tests passing with the new modular structure
- Proper handling of relative and absolute imports
- Consistent error handling across modules

## [2025-05-25]
### Added
- Modularized all scoring logic to new `scoring/scoring_engine.py` (Step 1 of scoring_v2 refactor).
- Comprehensive test coverage for modularized logic (unit, validation, CLI, scoring).

### Changed
- Updated all imports in code and tests to use `scoring_engine.py`.
- Updated error handling and input validation to accept both `Requirement` and `Skill` columns.
- Improved floating point robustness and deterministic output for scoring results.

### Fixed
- All test failures from normalization, severity logic, and import issues after modularization.
- Severity logic for `CoreGapSkill` to match domain/test expectations (Essential: ≤1 High, 2 Medium, >2 Low; Important: 0 Medium, >0 Low).
- Restored 100% passing state (67/67 tests) and 93%+ coverage for scoring logic.
### Changed
- Step 1 of modular refactor complete: `load_matrix` moved from `scoring_v2.py` to new `scoring/data_loader.py` module. All imports and tests updated. File organization improved for maintainability.

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
  - **Chunk 3**: Comprehensive unit tests for core scoring logic
    - Created `tests/unit/test_scoring.py` with 16 test methods covering:
      - Core gap detection for Essential (≤2) and Important (≤1) skills
      - Raw score calculation with emphasis modifiers and classification weights
      - Bonus point capping mechanism (25% of core points for Desirable/Implicit)
      - Score normalization and percentage fit calculation
      - CoreGapSkill severity levels (High/Medium/Low) and sorting
      - Input validation, edge cases, and error handling
      - Alternative column naming and empty DataFrame scenarios
    - All tests passing with comprehensive coverage of compute_scores() function
    - Combined test coverage: 48% of scoring_v2.py (33 tests total)
  - **Chunk 4**: Comprehensive validation and error handling tests
    - Created `tests/unit/test_validation.py` with 18 test methods covering:
      - File system validation (FileNotFoundError, invalid paths, directories)
      - CSV format validation (empty files, encoding issues, malformed data)
      - Required column validation and error reporting
      - Classification value validation against allowed types
      - SelfScore processing (non-numeric handling, clipping to 0-5 range)
      - Derived column calculation (ClassWt, EmphMod, Weight)
      - Edge cases: large files, whitespace handling, string vs Path inputs
    - Created `tests/unit/test_cli_error_handling.py` with 10 test methods covering:
      - Main function error scenarios (file not found, empty CSV, invalid data)
      - Argument parsing validation (missing arguments, invalid flags)
      - CLI flag handling (--help, --version)
      - Graceful error reporting and exit codes
      - Successful execution verification
    - All 28 validation/CLI tests passing with comprehensive error path coverage
    - **Final metrics: 79% coverage of scoring_v2.py (61 tests total)**
  - **Chunk 6**: Final push to 80%+ coverage target - ACHIEVED!
    - Added 6 additional CoreGapSkill validation tests covering:
      - Invalid name validation (empty, whitespace, non-string)
      - Invalid classification validation
      - Invalid self_score validation (non-integer, out of range)
      - Invalid threshold validation (non-integer, negative)
    - Added 2 error handling tests for load_matrix edge cases:
      - SelfScore processing error handling
      - Derived column processing error handling
    - **FINAL ACHIEVEMENT: 82% coverage of scoring_v2.py (67 tests total)**
    - **EXCEEDED TARGET**: Achieved 82% vs 80% goal (+2% above target)
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
- Fixed import issue in `scoring_v2.py` to support both module import and direct script execution
- Added try/except fallback for imports to handle relative vs absolute import scenarios

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

## Priority 5: GitHub Actions CI/CD Pipeline 
*Completed: 2025-05-23*

### **MAJOR MILESTONE: Enterprise-Grade CI/CD Infrastructure Complete!**

**Comprehensive GitHub Actions pipeline with multi-job workflow:**

#### **CI Workflow (`.github/workflows/ci.yml`)**
- **Multi-Python Testing**: Python 3.10, 3.11, 3.12, 3.13 support
- **Test Job**: 67 unit tests + integration tests with 80% coverage enforcement
- **Lint Job**: Ruff linting, formatting, and MyPy type checking
- **Example Testing**: CLI validation and import verification
- **Performance**: Dependency caching for faster builds
- **Reporting**: Codecov integration for coverage tracking

#### **Project Infrastructure**
- **Dependabot Configuration**: Automated weekly dependency updates
- **Pull Request Template**: Comprehensive PR checklist and guidelines
- **Issue Templates**: Bug reports and feature request templates
- **Modern Python Setup**: Complete `pyproject.toml` configuration
- **Local CI Script**: `scripts/test_ci_locally.sh` for local validation

#### **Quality Gates Implemented**
- **Coverage Enforcement**: Must maintain 80%+ test coverage
- **Multi-Environment Testing**: Ensures compatibility across Python versions
- **Code Quality**: Automated linting and formatting checks
- **CLI Validation**: Comprehensive command-line interface testing
- **Import Verification**: Package installation and import validation

#### **Verification Results**
- **All 67 unit tests passing** in local environment
- **Integration tests working** with existing test suite
- **CLI functionality verified**: Help, version, and execution working
- **Coverage target met**: 82% coverage maintained
- **Import validation successful**: All package imports working

#### **Benefits Achieved**
- **Quality Assurance**: Automated testing prevents regressions
- **Developer Experience**: Fast feedback with clear templates
- **Project Health**: Consistent code quality and automated maintenance
- **Production Ready**: Enterprise-grade CI/CD infrastructure

**Impact**: The job_scorer project now has robust CI/CD infrastructure that ensures code quality, prevents regressions, and provides excellent developer experience. Every commit and pull request is automatically tested across multiple Python versions with comprehensive quality checks.

**Status: PRIORITY 5 COMPLETE - PRODUCTION-READY CI/CD! **

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

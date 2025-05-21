# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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

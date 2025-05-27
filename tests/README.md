# Test Suite Index

This directory contains all tests for the **Job Scorer** project.

## Structure

- `unit/` — Unit tests for individual modules and functions
    - `test_cli_error_handling.py`: Tests for CLI error handling and edge cases
    - `test_emphasis.py`: Tests for emphasis modifier logic
    - `test_scoring.py`: Tests for core scoring algorithms and data structures
    - `test_validation.py`: Tests for input validation and error reporting
- (Add `integration/` or `e2e/` directories here as the suite grows)

## Running Tests

- **All tests:**
  ```bash
  uv run pytest
  ```
- **Specific module:**
  ```bash
  uv run pytest tests/unit/test_scoring.py
  ```

## Guidelines
- Add new tests to the appropriate subdirectory.
- Use descriptive names for test files and functions.
- Prefer small, focused tests for maintainability.
- Shared fixtures should go in `conftest.py`.

## Coverage
- Target: **80%+** coverage (see CI for current status)
- Use `pytest-cov` for local coverage reports:
  ```bash
  uv run pytest --cov=scoring
  ```

---

If you add new test types or directories, please update this index!

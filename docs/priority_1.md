# Priority 1: Testing Infrastructure - Implementation Plan

*Generated: 2025-05-23*

## Overview

This document outlines the step-by-step implementation plan for Priority 1: Testing Infrastructure. The goal is to establish a comprehensive pytest-based testing framework with 80%+ code coverage.

## Step-by-Step Plan

### **Chunk 1: Set up pytest structure and basic configuration** ⭐ *[Start Here]*
**Estimated Time**: 30-45 minutes

**What we'll do**:
- Create the `tests/unit/` directory structure
- Set up `pytest.ini` configuration file
- Create `conftest.py` with shared fixtures
- Verify pytest can discover and run (even with empty tests)

**Deliverable**: Working pytest setup that can be executed

**Files to create**:
```
tests/
├── unit/
│   └── __init__.py
├── conftest.py
└── pytest.ini
```

---

### **Chunk 2: Write tests for emphasis_modifier() function**
**Estimated Time**: 45-60 minutes

**What we'll do**:
- Test expert keywords (+0.5, +0.3)
- Test basic keywords (-0.5, -0.3)
- Test neutral cases (0.0)
- Test edge cases (multiple keywords, case sensitivity)

**Why this function first**: It's self-contained, well-defined, and critical to scoring accuracy

**File to create**: `tests/unit/test_emphasis.py`

**Test cases to implement**:
- `test_expert_keywords()` - Expert level emphasis detection
- `test_basic_keywords()` - Basic level emphasis detection
- `test_no_emphasis()` - Neutral requirements
- `test_multiple_keywords()` - Precedence when multiple keywords present
- `test_case_insensitive()` - Case insensitive detection
- `test_empty_string()` - Edge case handling

---

### **Chunk 3: Test core scoring logic**
**Estimated Time**: 1-1.5 hours

**What we'll do**:
- Test core gap detection logic
- Test bonus cap enforcement (25% rule)
- Test score boundary validation (0-5 range)

**Why next**: Core business logic that affects all scoring results

**File to create**: `tests/unit/test_scoring.py`

**Test classes to implement**:
- `TestScoreComputation`
  - `test_core_gap_detection()` - Core gap identification logic
  - `test_bonus_cap_enforcement()` - 25% bonus point cap
  - `test_score_boundaries()` - Score validation (0-5 range)
  - `test_classification_weights()` - Essential vs Important vs Desirable scoring
- `TestSkillMetrics`
  - `test_metrics_calculation()` - Overall metrics computation
  - `test_percentage_calculation()` - Percentage fit calculation

---

### **Chunk 4: Add validation and error handling tests**
**Estimated Time**: 45 minutes

**What we'll do**:
- Test missing required columns
- Test invalid score values
- Test empty/malformed CSV handling

**File to create**: `tests/unit/test_validation.py`

**Test classes to implement**:
- `TestCSVValidation`
  - `test_missing_required_columns()` - Missing Classification/Requirement columns
  - `test_invalid_score_values()` - Scores outside 0-5 range
  - `test_empty_csv()` - Empty file handling
  - `test_malformed_csv()` - Corrupted CSV files
- `TestInputValidation`
  - `test_file_not_found()` - Non-existent file handling
  - `test_permission_denied()` - File permission issues

---

### **Chunk 5: Set up GitHub Actions CI**
**Estimated Time**: 30 minutes

**What we'll do**:
- Create `.github/workflows/test.yml`
- Run tests on push/PR
- Add coverage reporting

**File to create**: `.github/workflows/test.yml`

**CI Pipeline features**:
- Run on Python 3.9, 3.10, 3.11
- Install dependencies from requirements.txt
- Run pytest with coverage
- Upload coverage to codecov (optional)
- Fail on coverage below threshold

---

### **Chunk 6: Achieve 80%+ test coverage**
**Estimated Time**: Variable (based on gaps found)

**What we'll do**:
- Run coverage analysis
- Identify untested code paths
- Add tests for remaining critical functions

**Files to potentially create**:
- `tests/unit/test_config.py` - Configuration classes
- `tests/unit/test_cli.py` - Command line interface
- Additional test methods in existing files

**Coverage targets**:
- `scoring_v2.py`: 85%+ coverage
- Core functions: 90%+ coverage
- Overall project: 80%+ coverage

---

## Current Status

### Existing Test Infrastructure
- ✅ Integration test runner (`tests/test_runner.py`)
- ✅ Test data in `tests/data/v1/` and `tests/data/v2/`
- ✅ Expected output validation
- ✅ pytest installed in requirements.txt

### What We're Adding
- 🔄 Unit test structure with pytest
- 🔄 Comprehensive test coverage
- 🔄 CI/CD pipeline
- 🔄 Coverage reporting

## Questions for Implementation

### Chunk 1 Questions:
1. Should I preserve your existing `test_runner.py` integration tests? (Recommended: yes)
2. Any specific pytest plugins you'd like me to configure?
3. Would you like me to set up coverage reporting from the start?

### General Questions:
- Preferred coverage threshold (80%, 85%, 90%)?
- Should we add performance/benchmark tests?
- Any specific test naming conventions you prefer?

## Implementation Notes

### Preserving Existing Tests
- Keep `test_runner.py` for integration testing
- Maintain `tests/data/` structure for test files
- Ensure new unit tests complement existing integration tests

### Test Organization
- Unit tests in `tests/unit/` for isolated function testing
- Integration tests remain in `tests/` root for full workflow testing
- Shared fixtures in `conftest.py` for reusability

### Coverage Strategy
- Focus on critical business logic first
- Ensure edge cases are covered
- Maintain backward compatibility testing

---

## Success Criteria

### Chunk 1 Success:
- [ ] `pytest` command runs without errors
- [ ] Test discovery works correctly
- [ ] Basic configuration is functional

### Overall Priority 1 Success:
- [ ] 80%+ code coverage achieved
- [ ] All critical functions have unit tests
- [ ] CI pipeline runs tests automatically
- [ ] No regression in existing functionality
- [ ] Documentation updated with testing approach

---

## Next Steps

1. **Start with Chunk 1**: Set up pytest infrastructure
2. **Validate setup**: Ensure pytest runs and discovers tests
3. **Proceed chunk by chunk**: Complete each section before moving to next
4. **Regular check-ins**: Review progress and adjust approach as needed

---

*This document will be updated as we progress through each chunk, documenting decisions made and lessons learned.*

# Implementation Roadmap

# Implementation Roadmap

## 1. Setup & Preparation
- [x] Create a backup of the current working script
- [x] Set up a test environment with sample data
  - [x] Create test directory structure
  - [x] Add sample CSV files for v1 and v2 formats
  - [x] Implement test runner script
  - [x] Verify test environment works with both versions

## 2. Core Changes
- [x] Update the data model to include new fields (Classification, Emphasis)
  - [x] Add CLASS_WT constant for classification weights
  - [x] Implement emphasis_modifier function
  - [x] Modify load_matrix to handle both old and new formats
- [x] Modify the scoring algorithm to use the new 0-5 scale
  - [x] Update compute_scores function
  - [x] Adjust percentage calculation
  - [x] Update core-gap detection for 0-5 scale
- [x] Implement the emphasis modifier logic
  - [x] Integrate emphasis modifier into scoring
  - [x] Test with various emphasis keywords

## 3. Enhancements
- [x] Update the core-gap detection
  - [x] Adjust threshold for 0-5 scale
  - [x] Update warning messages (Implicitly done by improving core gap skill reporting)
- [x] Implement the new bonus cap calculation
  - [x] Apply 25% cap on bonus points
  - [ ] Update documentation (for bonus cap specifics)
- [ ] Add input validation for the new fields
  - [ ] Validate classification values
  - [ ] Check score ranges
  - [ ] Add meaningful error messages

## 4. Testing
- [x] Test with existing CSV files
  - [x] Verify v1 format works
  - [x] Test v2 format
- [x] Create test cases for the new functionality
  - [x] Test different classification combinations (Covered by `core_gap_test.csv`)
  - [ ] Test emphasis modifiers
  - [x] Test edge cases (Covered `bonus_cap_test.csv` and basic pass-throughs)
- [x] Verify backward compatibility
  - [x] Ensure old CSVs still work (Covered by `v1/basic_test.csv`)
  - [ ] Test migration path
- [x] All v2 tests pass after project reorganization and test runner update (project stable)

## 5. Documentation
- [x] Update the CHANGELOG.md
- [ ] Update the script's help text and documentation
  - [ ] Document new CSV format
  - [ ] Update usage examples
  - [ ] Add examples of emphasis keywords

## Progress Tracking

| Section | Completed | In Progress | Not Started |
|---------|-----------|-------------|-------------|
| Setup & Preparation | 2/2 | 0/2 | 0/2 |
| Core Changes | 3/3 | 0/3 | 0/3 |
| Enhancements | 2/3 | 0/3 | 1/3 | 
| Testing | 2/3 | 0/3 | 1/3 |
| Documentation | 1/2 | 0/2 | 1/2 |
| **Total** | **10/13** | **0/13** | **3/13** |

## Next Steps
1. Update scoring algorithm in `compute_scores`
2. Test with various input scenarios
3. Update documentation and help text
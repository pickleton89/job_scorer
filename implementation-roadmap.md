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
- [ ] Modify the scoring algorithm to use the new 0-5 scale
  - [ ] Update compute_scores function
  - [ ] Adjust percentage calculation
  - [ ] Update core-gap detection for 0-5 scale
- [ ] Implement the emphasis modifier logic
  - [ ] Integrate emphasis modifier into scoring
  - [ ] Test with various emphasis keywords

## 3. Enhancements
- [ ] Update the core-gap detection
  - [ ] Adjust threshold for 0-5 scale
  - [ ] Update warning messages
- [ ] Implement the new bonus cap calculation
  - [ ] Apply 25% cap on bonus points
  - [ ] Update documentation
- [ ] Add input validation for the new fields
  - [ ] Validate classification values
  - [ ] Check score ranges
  - [ ] Add meaningful error messages

## 4. Testing
- [x] Test with existing CSV files
  - [x] Verify v1 format works
  - [x] Test v2 format
- [ ] Create test cases for the new functionality
  - [ ] Test different classification combinations
  - [ ] Test emphasis modifiers
  - [ ] Test edge cases
- [ ] Verify backward compatibility
  - [ ] Ensure old CSVs still work
  - [ ] Test migration path

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
| Core Changes | 1/3 | 1/3 | 1/3 |
| Enhancements | 0/3 | 0/3 | 3/3 |
| Testing | 1/3 | 0/3 | 2/3 |
| Documentation | 1/2 | 0/2 | 1/2 |
| **Total** | **5/13** | **1/13** | **7/13** |

## Next Steps
1. Update scoring algorithm in `compute_scores`
2. Test with various input scenarios
3. Update documentation and help text
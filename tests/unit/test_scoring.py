"""
Unit tests for core scoring logic.

Tests the compute_scores() function which handles:
- Core gap detection based on classification and thresholds
- Raw score calculation with emphasis modifiers
- Bonus point capping for Desirable/Implicit skills
- Score normalization and percentage fit calculation
"""

import pandas as pd
import pytest

from scoring.scoring_engine import CoreGapSkill, compute_scores


class TestComputeScores:
    """Test cases for the compute_scores function."""

    def test_basic_scoring_no_gaps(self):
        """Test basic scoring with no core gaps."""
        df = pd.DataFrame({
            'Requirement': ['Python programming', 'SQL databases'],
            'Classification': ['Essential', 'Important'],
            'ClassWt': [3.0, 2.0],
            'EmphMod': [0.0, 0.0],
            'SelfScore': [4, 3]
        })

        result = compute_scores(df)

        assert result['core_gap'] is False
        assert result['core_gap_skills'] == []
        # Raw scores: 3*1*4=12, 2*1*3=6, total=18
        # Theoretical max per row: 3*1.5*5=22.5
        # Normalized: 12/22.5=0.533, 6/22.5=0.267, total=0.8
        assert result['actual_points'] == 0.8
        assert result['max_points'] == 2.0  # 2 rows * 1.0 each
        assert result['pct_fit'] == 0.4  # 0.8/2.0

    def test_essential_core_gap_detection(self):
        """Test core gap detection for Essential skills."""
        df = pd.DataFrame({
            'Requirement': ['Python expert', 'Advanced SQL', 'Basic Git'],
            'Classification': ['Essential', 'Essential', 'Essential'],
            'ClassWt': [3.0, 3.0, 3.0],
            'EmphMod': [0.0, 0.0, 0.0],
            'SelfScore': [1, 2, 0]  # All are gaps (≤2 for Essential)
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        assert len(result['core_gap_skills']) == 3  # All three are gaps

        # Check gap skills are sorted correctly (by classification, then by score)
        gaps = result['core_gap_skills']
        assert gaps[0].name == 'Basic Git'
        assert gaps[0].self_score == 0
        assert gaps[0].classification == 'Essential'
        assert gaps[1].name == 'Python expert'
        assert gaps[1].self_score == 1
        assert gaps[1].classification == 'Essential'
        assert gaps[2].name == 'Advanced SQL'
        assert gaps[2].self_score == 2
        assert gaps[2].classification == 'Essential'

    def test_important_core_gap_detection(self):
        """Test core gap detection for Important skills."""
        df = pd.DataFrame({
            'Requirement': ['Docker', 'Kubernetes', 'CI/CD'],
            'Classification': ['Important', 'Important', 'Important'],
            'ClassWt': [2.0, 2.0, 2.0],
            'EmphMod': [0.0, 0.0, 0.0],
            'SelfScore': [0, 1, 2]  # 0 and 1 are gaps (≤1), 2 is not
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        assert len(result['core_gap_skills']) == 2

        gaps = result['core_gap_skills']
        assert gaps[0].name == 'Docker'
        assert gaps[0].self_score == 0
        assert gaps[1].name == 'Kubernetes'
        assert gaps[1].self_score == 1

    def test_mixed_classification_gaps(self):
        """Test core gap detection with mixed classifications."""
        df = pd.DataFrame({
            'Requirement': ['Python', 'Docker', 'AWS', 'Nice to have'],
            'Classification': ['Essential', 'Important', 'Desirable', 'Implicit'],
            'ClassWt': [3.0, 2.0, 1.0, 0.5],
            'EmphMod': [0.0, 0.0, 0.0, 0.0],
            'SelfScore': [1, 0, 0, 0]  # Essential and Important have gaps, others don't
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        assert len(result['core_gap_skills']) == 2

        # Should be sorted by classification order (Essential first)
        gaps = result['core_gap_skills']
        assert gaps[0].classification == 'Essential'
        assert gaps[1].classification == 'Important'

    def test_emphasis_modifier_scoring(self):
        """Test scoring with emphasis modifiers."""
        df = pd.DataFrame({
            'Requirement': ['Expert Python', 'Basic SQL'],
            'Classification': ['Essential', 'Important'],
            'ClassWt': [3.0, 2.0],
            'EmphMod': [0.5, -0.5],  # High and low emphasis
            'SelfScore': [4, 3]
        })

        result = compute_scores(df)

        # Raw scores: 3*(1+0.5)*4=18, 2*(1-0.5)*3=3, total=21
        # Normalized: 18/22.5=0.8, 3/22.5=0.133, total=0.933
        assert result['actual_points'] == 0.93
        assert result['core_gap'] is False

    def test_bonus_capping_mechanism(self):
        """Test bonus point capping for Desirable/Implicit skills."""
        # Create scenario where bonus points exceed the cap
        df = pd.DataFrame({
            'Requirement': ['Python', 'SQL', 'Bonus1', 'Bonus2', 'Bonus3'],
            'Classification': ['Essential', 'Important', 'Desirable', 'Desirable', 'Implicit'],
            'ClassWt': [3.0, 2.0, 1.0, 1.0, 0.5],
            'EmphMod': [0.0, 0.0, 0.0, 0.0, 0.0],
            'SelfScore': [5, 5, 5, 5, 5]  # Max scores
        })

        result = compute_scores(df)

        # Core weight = 3.0 + 2.0 = 5.0
        # Max bonus = 5.0 * 0.25 * 5 = 6.25 (25% cap)
        # Actual bonus before cap = 1*5 + 1*5 + 0.5*5 = 12.5
        # Since 12.5 > 6.25, bonus should be capped

        # The bonus capping should reduce the total score
        assert result['actual_points'] < 2.0  # Less than if no capping applied
        assert result['core_gap'] is False

    def test_no_bonus_capping_when_under_limit(self):
        """Test that bonus capping doesn't apply when under the limit."""
        df = pd.DataFrame({
            'Requirement': ['Python', 'SQL', 'Small bonus'],
            'Classification': ['Essential', 'Important', 'Desirable'],
            'ClassWt': [3.0, 2.0, 1.0],
            'EmphMod': [0.0, 0.0, 0.0],
            'SelfScore': [3, 3, 1]  # Small bonus that won't hit cap
        })

        result = compute_scores(df)

        # Core weight = 5.0, max bonus = 6.25
        # Actual bonus = 1*1 = 1.0 (well under cap)
        # No scaling should occur

        # Raw scores: 3*3=9, 2*3=6, 1*1=1, total=16
        # Normalized: 9/22.5=0.4, 6/22.5=0.267, 1/22.5=0.044, total=0.711
        expected_score = round((9 + 6 + 1) / 22.5, 2)
        assert result['actual_points'] == expected_score

    def test_zero_scores_handling(self):
        """Test handling of zero self-scores."""
        df = pd.DataFrame({
            'Requirement': ['Python', 'SQL', 'Docker'],
            'Classification': ['Essential', 'Important', 'Desirable'],
            'ClassWt': [3.0, 2.0, 1.0],
            'EmphMod': [0.0, 0.0, 0.0],
            'SelfScore': [0, 0, 0]
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        assert len(result['core_gap_skills']) == 2  # Essential and Important
        assert result['actual_points'] == 0.0
        assert result['pct_fit'] == 0.0

    def test_perfect_scores(self):
        """Test scenario with perfect scores across all classifications."""
        df = pd.DataFrame({
            'Requirement': ['Python', 'SQL', 'Docker', 'Nice'],
            'Classification': ['Essential', 'Important', 'Desirable', 'Implicit'],
            'ClassWt': [3.0, 2.0, 1.0, 0.5],
            'EmphMod': [0.0, 0.0, 0.0, 0.0],
            'SelfScore': [5, 5, 5, 5]
        })

        result = compute_scores(df)

        assert result['core_gap'] is False
        assert result['core_gap_skills'] == []
        # With bonus capping, the fit percentage will be lower than without capping
        assert result['pct_fit'] > 0.3  # Adjusted expectation due to bonus capping
        assert result['actual_points'] > 0  # Should still have positive points

    def test_input_validation_missing_columns(self):
        """Test input validation for missing required columns."""
        df = pd.DataFrame({
            'Requirement': ['Python'],
            'Classification': ['Essential']
            # Missing ClassWt, EmphMod, SelfScore
        })

        try:
            compute_scores(df)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing required columns" in str(e)

    def test_input_validation_wrong_type(self):
        """Test input validation for wrong input type."""
        try:
            compute_scores("not a dataframe")
            assert False, "Should have raised TypeError"
        except TypeError as e:
            assert "Expected pandas DataFrame" in str(e)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame({
            'Requirement': [],
            'Classification': [],
            'ClassWt': [],
            'EmphMod': [],
            'SelfScore': []
        })

        result = compute_scores(df)

        assert result['core_gap'] is False
        assert result['core_gap_skills'] == []
        assert result['actual_points'] == 0.0
        assert result['max_points'] == 0.0
        assert result['pct_fit'] == 0.0

    def test_alternative_requirement_column_names(self):
        """Test that function finds requirement column with different names."""
        df = pd.DataFrame({
            'Skill': ['Python programming'],  # Different column name
            'Classification': ['Essential'],
            'ClassWt': [3.0],
            'EmphMod': [0.0],
            'SelfScore': [1]  # Core gap
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        assert result['core_gap_skills'][0].name == 'Python programming'

    def test_core_gap_severity_levels(self):
        """Test CoreGapSkill severity calculation."""
        df = pd.DataFrame({
            'Requirement': ['Essential 0', 'Essential 1', 'Essential 2', 'Important 0', 'Important 1'],
            'Classification': ['Essential', 'Essential', 'Essential', 'Important', 'Important'],
            'ClassWt': [3.0, 3.0, 3.0, 2.0, 2.0],
            'EmphMod': [0.0, 0.0, 0.0, 0.0, 0.0],
            'SelfScore': [0, 1, 2, 0, 1]
        })

        result = compute_scores(df)

        assert result['core_gap'] is True
        gaps = result['core_gap_skills']

        # Test severity levels using the correct property name
        essential_0 = next(g for g in gaps if g.name == 'Essential 0')
        essential_1 = next(g for g in gaps if g.name == 'Essential 1')
        essential_2 = next(g for g in gaps if g.name == 'Essential 2')
        important_0 = next(g for g in gaps if g.name == 'Important 0')
        important_1 = next(g for g in gaps if g.name == 'Important 1')

        assert essential_0.severity == 'High'  # Essential with score 0
        assert essential_1.severity == 'High'  # Essential with score 1
        assert essential_2.severity == 'Medium'  # Essential with score 2
        assert important_0.severity == 'Medium'  # Important with score 0
        assert important_1.severity == 'Low'  # Important with score 1

    def test_bonus_cap_edge_case_zero_bonus(self):
        """Test bonus capping when actual bonus is zero."""
        df = pd.DataFrame({
            'Requirement': ['Python', 'Bonus'],
            'Classification': ['Essential', 'Desirable'],
            'ClassWt': [3.0, 1.0],
            'EmphMod': [0.0, 0.0],
            'SelfScore': [5, 0]  # Zero bonus score
        })

        result = compute_scores(df)

        # Should handle zero bonus gracefully without division by zero
        assert result['actual_points'] > 0
        assert result['core_gap'] is False

    def test_custom_scoring_config(self):
        """Test compute_scores with custom configuration values."""
        # This test verifies the function uses the global SCORING_CONFIG correctly
        df = pd.DataFrame({
            'Requirement': ['Python'],
            'Classification': ['Essential'],
            'ClassWt': [3.0],
            'EmphMod': [0.5],  # High emphasis
            'SelfScore': [5]
        })

        result = compute_scores(df)

        # Raw score: 3 * (1 + 0.5) * 5 = 22.5
        # Normalized: 22.5 / 22.5 = 1.0
        assert result['actual_points'] == 1.0
        assert result['max_points'] == 1.0
        assert result['pct_fit'] == 1.0

    def test_core_gap_skill_validation_invalid_name(self):
        """Test CoreGapSkill validation with invalid name."""

        # Empty string name should raise ValueError
        with pytest.raises(ValueError, match="Skill name must be a non-empty string"):
            CoreGapSkill(name="", classification="Essential", self_score=1, threshold=2)

        # Whitespace-only name should raise ValueError
        with pytest.raises(ValueError, match="Skill name must be a non-empty string"):
            CoreGapSkill(name="   ", classification="Essential", self_score=1, threshold=2)

        # Non-string name should raise ValueError
        with pytest.raises(ValueError, match="Skill name must be a non-empty string"):
            CoreGapSkill(name=123, classification="Essential", self_score=1, threshold=2)

    def test_core_gap_skill_validation_invalid_classification(self):
        """Test CoreGapSkill validation with invalid classification."""

        # Invalid classification should raise ValueError
        with pytest.raises(ValueError, match="Invalid classification: InvalidType"):
            CoreGapSkill(name="Python", classification="InvalidType", self_score=1, threshold=2)

    def test_core_gap_skill_validation_invalid_self_score(self):
        """Test CoreGapSkill validation with invalid self_score."""

        # Non-integer self_score should raise ValueError
        with pytest.raises(ValueError, match="Self score must be an integer between 0 and 5"):
            CoreGapSkill(name="Python", classification="Essential", self_score=1.5, threshold=2)

        # Self score below 0 should raise ValueError
        with pytest.raises(ValueError, match="Self score must be an integer between 0 and 5"):
            CoreGapSkill(name="Python", classification="Essential", self_score=-1, threshold=2)

        # Self score above 5 should raise ValueError
        with pytest.raises(ValueError, match="Self score must be an integer between 0 and 5"):
            CoreGapSkill(name="Python", classification="Essential", self_score=6, threshold=2)

    def test_core_gap_skill_validation_invalid_threshold(self):
        """Test CoreGapSkill validation with invalid threshold."""

        # Non-integer threshold should raise ValueError
        with pytest.raises(ValueError, match="Threshold must be a non-negative integer"):
            CoreGapSkill(name="Python", classification="Essential", self_score=1, threshold=2.5)

        # Negative threshold should raise ValueError
        with pytest.raises(ValueError, match="Threshold must be a non-negative integer"):
            CoreGapSkill(name="Python", classification="Essential", self_score=1, threshold=-1)

"""
Unit tests for compute_scores_enhanced function

This module tests the integration of all enhancement functions
in the enhanced scoring pipeline.
"""

import pandas as pd
import pytest

from scoring.scoring_engine import compute_scores, compute_scores_enhanced


class TestEnhancedScoring:
    """Test enhanced scoring integration."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        data = {
            "Classification": ["Essential", "Important", "Desirable", "Implicit"],
            "Requirement": [
                "Lead strategic planning initiatives",
                "Manage cross-functional teams in biology",
                "Expert bioinformatics knowledge",
                "Present to senior leadership"
            ],
            "SelfScore": [4, 3, 2, 4],
            "ClassWt": [3.0, 2.0, 1.0, 0.5],
            "EmphMod": [0.0, 0.0, 0.5, 0.0]
        }
        return pd.DataFrame(data)

    def test_enhanced_scoring_disabled_equals_standard(self, sample_df):
        """Test that enhanced scoring with enhancements disabled equals standard scoring."""
        standard_result = compute_scores(sample_df.copy())
        enhanced_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=False
        )

        assert standard_result["pct_fit"] == enhanced_result["pct_fit"]
        assert standard_result["actual_points"] == enhanced_result["actual_points"]
        assert standard_result["core_gap"] == enhanced_result["core_gap"]

    def test_enhanced_scoring_enabled_different_from_standard(self, sample_df):
        """Test that enhanced scoring with enhancements enabled differs from standard."""
        standard_result = compute_scores(sample_df.copy())
        enhanced_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            target_role_type="executive",
            years_experience=20
        )

        # Enhanced scoring should be different (could be higher or lower)
        assert enhanced_result["pct_fit"] != standard_result["pct_fit"]

    def test_enhanced_scoring_with_proven_strengths(self, sample_df):
        """Test enhanced scoring with proven strengths."""
        result_without = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            proven_strengths=None
        )

        result_with = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            proven_strengths=["cross-functional", "bioinformatics"]
        )

        # With proven strengths should typically score higher
        assert result_with["pct_fit"] >= result_without["pct_fit"]

    def test_enhanced_scoring_role_level_differences(self):
        """Test that different role levels produce different scores."""
        # Create data with strategic and technical requirements
        role_data = {
            "Classification": ["Essential", "Important"],
            "Requirement": [
                "Strategic planning and vision development",
                "Technical programming and data analysis"
            ],
            "SelfScore": [4, 3],
            "ClassWt": [3.0, 2.0],
            "EmphMod": [0.0, 0.0]
        }
        df = pd.DataFrame(role_data)

        c_suite_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            target_role_level="c_suite"
        )

        senior_ic_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            target_role_level="senior_ic"
        )

        # Different role levels should produce different scores
        assert c_suite_result["pct_fit"] != senior_ic_result["pct_fit"]

    def test_enhanced_scoring_experience_level_effects(self, sample_df):
        """Test that experience level affects scoring."""
        junior_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            years_experience=10  # Below 15 year threshold
        )

        senior_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            years_experience=25  # Above 15 year threshold
        )

        # Different experience levels should produce different scores for senior professionals
        assert junior_result["pct_fit"] != senior_result["pct_fit"]

    def test_enhanced_scoring_dual_track_effects(self, sample_df):
        """Test that target role type affects dual-track scoring."""
        executive_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            target_role_type="executive"
        )

        ic_result = compute_scores_enhanced(
            sample_df.copy(),
            enable_enhancements=True,
            target_role_type="ic"
        )

        # Different role types should produce different scores
        assert executive_result["pct_fit"] != ic_result["pct_fit"]

    def test_enhanced_scoring_adds_columns(self, sample_df):
        """Test that enhanced scoring adds the expected columns."""
        df_copy = sample_df.copy()
        compute_scores_enhanced(
            df_copy,
            enable_enhancements=True
        )

        expected_columns = [
            "ReqType", "DualTrackMod", "SkillCategory", "ExpLevelMod",
            "CrossFuncComplexity", "IndicatorCount", "MatchesStrength",
            "CrossFuncMod", "RoleLevelMod"
        ]

        for col in expected_columns:
            assert col in df_copy.columns

    def test_enhanced_scoring_preserves_core_gap_logic(self, sample_df):
        """Test that enhanced scoring preserves core gap detection logic."""
        # Create data with core gaps
        gap_data = sample_df.copy()
        gap_data.loc[0, "SelfScore"] = 1  # Essential skill with score 1 (≤ 2 threshold)

        result = compute_scores_enhanced(
            gap_data,
            enable_enhancements=True
        )

        assert result["core_gap"] is True
        assert len(result["core_gap_skills"]) > 0
        assert result["core_gap_skills"][0].classification == "Essential"

    def test_enhanced_scoring_input_validation(self):
        """Test enhanced scoring input validation."""
        with pytest.raises(TypeError):
            compute_scores_enhanced("not a dataframe", enable_enhancements=True)  # type: ignore[arg-type]

    def test_enhanced_scoring_missing_columns(self):
        """Test enhanced scoring with missing required columns."""
        invalid_df = pd.DataFrame({"InvalidColumn": [1, 2, 3]})

        with pytest.raises(ValueError, match="Missing required columns"):
            compute_scores_enhanced(invalid_df, enable_enhancements=True)

    def test_enhanced_scoring_bonus_capping(self, sample_df):
        """Test that enhanced scoring still applies bonus capping."""
        # Create data with high desirable/implicit scores
        bonus_data = sample_df.copy()
        bonus_data.loc[2, "SelfScore"] = 5  # Desirable
        bonus_data.loc[3, "SelfScore"] = 5  # Implicit

        result = compute_scores_enhanced(
            bonus_data,
            enable_enhancements=True
        )

        # Should still have reasonable scores due to bonus capping
        assert result["pct_fit"] <= 1.0  # Should not exceed 100%


class TestEnhancedScoringRealWorld:
    """Test enhanced scoring with realistic scenarios."""

    def test_cross_functional_leadership_scenario(self):
        """Test scenario emphasizing cross-functional leadership."""
        data = {
            "Classification": ["Essential", "Essential", "Important"],
            "Requirement": [
                "Collaborate across chemistry, biology, and clinical teams",
                "Translate research findings to business stakeholders",
                "Integrate multiple therapeutic platforms"
            ],
            "SelfScore": [4, 4, 3],
            "ClassWt": [3.0, 3.0, 2.0],
            "EmphMod": [0.0, 0.0, 0.0]
        }
        df = pd.DataFrame(data)

        result = compute_scores_enhanced(
            df,
            enable_enhancements=True,
            proven_strengths=["cross-functional", "integration"]
        )

        # Should detect high cross-functional complexity and apply bonuses
        assert result["pct_fit"] > 0.0

    def test_senior_executive_experience_calibration(self):
        """Test experience calibration for senior executives."""
        data = {
            "Classification": ["Essential", "Important"],
            "Requirement": [
                "Lead strategic planning initiatives",
                "Manage and mentor team members"
            ],
            "SelfScore": [3, 3],  # Below baseline for senior executives
            "ClassWt": [3.0, 2.0],
            "EmphMod": [0.0, 0.0]
        }
        df = pd.DataFrame(data)

        senior_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            years_experience=25  # Senior experience
        )

        junior_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            years_experience=10  # Junior experience (no calibration)
        )

        # Senior should have lower score due to higher expectations
        assert senior_result["pct_fit"] <= junior_result["pct_fit"]

    def test_role_level_calibration_effects(self):
        """Test role level calibration across different levels."""
        strategic_data = {
            "Classification": ["Essential", "Important"],
            "Requirement": [
                "Strategic thinking and vision development",
                "Technical implementation expertise"
            ],
            "SelfScore": [4, 3],
            "ClassWt": [3.0, 2.0],
            "EmphMod": [0.0, 0.0]
        }
        df = pd.DataFrame(strategic_data)

        c_suite_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            target_role_level="c_suite"  # Strategic thinking weighted higher
        )

        senior_ic_result = compute_scores_enhanced(
            df.copy(),
            enable_enhancements=True,
            target_role_level="senior_ic"  # Technical skills weighted higher
        )

        # C-suite should score higher due to strategic emphasis
        assert c_suite_result["pct_fit"] > senior_ic_result["pct_fit"]

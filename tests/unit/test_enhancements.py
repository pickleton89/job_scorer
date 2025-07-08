"""
Unit tests for enhancement functions in scoring_engine.py

This module tests all four enhancement framework functions:
1. Dual-track scoring (executive vs IC alignment)
2. Experience-level calibration
3. Cross-functional leadership detection
4. Role-level weight adjustments
"""

from scoring.config import (
    DualTrackConfig,
    ExperienceLevelConfig,
    RoleLevelConfig,
)
from scoring.scoring_engine import (
    assess_cross_functional_complexity,
    categorize_skill,
    classify_requirement_type,
    cross_functional_modifier,
    dual_track_modifier,
    experience_level_modifier,
    get_role_weights,
    matches_proven_strength,
)


class TestDualTrackScoring:
    """Test dual-track scoring functionality."""

    def test_classify_requirement_type_executive(self):
        """Test classification of executive-focused requirements."""
        text = "Lead strategic planning and manage cross-functional teams"
        result = classify_requirement_type(text)
        assert result == "executive"

    def test_classify_requirement_type_ic(self):
        """Test classification of IC-focused requirements."""
        text = "Develop advanced algorithms and implement novel solutions"
        result = classify_requirement_type(text)
        assert result == "ic"

    def test_classify_requirement_type_hybrid(self):
        """Test classification of hybrid requirements."""
        text = "Technical role with balanced responsibilities"
        result = classify_requirement_type(text)
        assert result == "hybrid"

    def test_classify_requirement_type_empty(self):
        """Test classification with empty text."""
        result = classify_requirement_type("")
        assert result == "hybrid"  # No indicators found

    def test_dual_track_modifier_aligned(self):
        """Test modifier when requirement and role are aligned."""
        modifier = dual_track_modifier("executive", "executive")
        assert modifier == 1.0

    def test_dual_track_modifier_ic_for_executive(self):
        """Test modifier when IC requirement for executive role."""
        modifier = dual_track_modifier("ic", "executive")
        assert modifier == 0.9

    def test_dual_track_modifier_executive_for_ic(self):
        """Test modifier when executive requirement for IC role."""
        modifier = dual_track_modifier("executive", "ic")
        assert modifier == 0.8

    def test_dual_track_modifier_hybrid(self):
        """Test modifier for hybrid requirements."""
        modifier = dual_track_modifier("hybrid", "executive")
        assert modifier == 1.0

    def test_dual_track_custom_config(self):
        """Test dual-track with custom configuration."""
        custom_config = DualTrackConfig(
            ic_for_executive_multiplier=0.85,
            executive_for_ic_multiplier=0.75
        )
        modifier = dual_track_modifier("ic", "executive", custom_config)
        assert modifier == 0.85


class TestExperienceLevelScoring:
    """Test experience-level calibration functionality."""

    def test_categorize_skill_leadership(self):
        """Test skill categorization for leadership skills."""
        text = "Lead cross-functional teams and manage stakeholder relationships"
        result = categorize_skill(text)
        assert result == "leadership"

    def test_categorize_skill_technical(self):
        """Test skill categorization for technical skills."""
        text = "Data analysis and statistical modeling"
        result = categorize_skill(text)
        assert result == "basic_technical"

    def test_categorize_skill_strategic(self):
        """Test skill categorization for strategic thinking."""
        text = "Strategic planning and vision development"
        result = categorize_skill(text)
        assert result == "strategic_thinking"

    def test_categorize_skill_no_match(self):
        """Test skill categorization with no matches."""
        text = "Some random skill description"
        result = categorize_skill(text)
        assert result is None

    def test_experience_level_modifier_junior(self):
        """Test modifier for junior experience level."""
        modifier = experience_level_modifier("leadership", 3, 10)
        assert modifier == 1.0  # No adjustment for < 15 years

    def test_experience_level_modifier_below_baseline(self):
        """Test modifier for below-baseline senior executive."""
        modifier = experience_level_modifier("leadership", 3, 20)
        assert modifier == 0.7  # Below baseline penalty

    def test_experience_level_modifier_above_baseline(self):
        """Test modifier for above-baseline senior executive."""
        modifier = experience_level_modifier("leadership", 5, 20)
        assert modifier == 1.1  # Above baseline bonus

    def test_experience_level_modifier_at_baseline(self):
        """Test modifier at baseline for senior executive."""
        modifier = experience_level_modifier("leadership", 4, 20)
        assert modifier == 1.0  # At baseline, no adjustment

    def test_experience_level_modifier_no_category(self):
        """Test modifier for uncategorized skill."""
        modifier = experience_level_modifier(None, 3, 20)
        assert modifier == 1.0

    def test_experience_level_custom_config(self):
        """Test experience level with custom configuration."""
        custom_baseline = ExperienceLevelConfig.SkillBaseline(leadership=5)
        custom_config = ExperienceLevelConfig(
            senior_executive_baselines=custom_baseline,
            below_baseline_penalty=0.6
        )
        modifier = experience_level_modifier("leadership", 3, 20, custom_config)
        assert modifier == 0.6


class TestCrossFunctionalScoring:
    """Test cross-functional leadership functionality."""

    def test_assess_cross_functional_complexity_high(self):
        """Test high complexity cross-functional requirement."""
        text = "Collaborate with chemistry, biology, clinical teams to translate research findings"
        complexity, count = assess_cross_functional_complexity(text)
        assert complexity == "high"
        assert count >= 3

    def test_assess_cross_functional_complexity_medium(self):
        """Test medium complexity cross-functional requirement."""
        text = "Coordinate cross-functional projects"
        complexity, count = assess_cross_functional_complexity(text)
        assert complexity == "medium"
        assert count >= 1

    def test_assess_cross_functional_complexity_low(self):
        """Test low complexity requirement."""
        text = "Individual contributor role with minimal interaction"
        complexity, count = assess_cross_functional_complexity(text)
        assert complexity == "low"
        assert count == 0

    def test_cross_functional_modifier_high_complexity(self):
        """Test modifier for high complexity with bonuses."""
        modifier = cross_functional_modifier("high", True, True)
        expected = 1.3 + 0.1 + 0.05  # high + proven + executive
        assert modifier == expected

    def test_cross_functional_modifier_medium_complexity(self):
        """Test modifier for medium complexity."""
        modifier = cross_functional_modifier("medium", False, False)
        assert modifier == 1.15

    def test_cross_functional_modifier_low_complexity(self):
        """Test modifier for low complexity."""
        modifier = cross_functional_modifier("low", False, False)
        assert modifier == 1.0

    def test_cross_functional_modifier_with_proven_strength(self):
        """Test modifier with proven strength bonus."""
        modifier = cross_functional_modifier("low", True, False)
        assert modifier == 1.1  # 1.0 + 0.1 proven strength bonus

    def test_cross_functional_modifier_executive_bonus(self):
        """Test modifier with executive role bonus."""
        modifier = cross_functional_modifier("low", False, True)
        assert modifier == 1.05  # 1.0 + 0.05 executive bonus

    def test_matches_proven_strength_match(self):
        """Test proven strength matching."""
        text = "Cross-functional leadership experience"
        strengths = ["cross-functional", "leadership"]
        result = matches_proven_strength(text, strengths)
        assert result is True

    def test_matches_proven_strength_no_match(self):
        """Test proven strength with no matches."""
        text = "Individual technical work"
        strengths = ["cross-functional", "leadership"]
        result = matches_proven_strength(text, strengths)
        assert result is False

    def test_matches_proven_strength_none(self):
        """Test proven strength with None input."""
        text = "Any requirement text"
        result = matches_proven_strength(text, None)
        assert result is False

    def test_matches_proven_strength_empty_list(self):
        """Test proven strength with empty list."""
        text = "Any requirement text"
        result = matches_proven_strength(text, [])
        assert result is False


class TestRoleLevelCalibration:
    """Test role-level calibration functionality."""

    def test_get_role_weights_c_suite(self):
        """Test role weights for C-suite level."""
        weights = get_role_weights("c_suite")
        assert weights.strategic_thinking == 1.4
        assert weights.business_acumen == 1.3
        assert weights.hands_on_skills == 0.6

    def test_get_role_weights_senior_executive(self):
        """Test role weights for senior executive level."""
        weights = get_role_weights("senior_executive")
        assert weights.strategic_thinking == 1.3
        assert weights.cross_functional == 1.3
        assert weights.hands_on_skills == 0.8

    def test_get_role_weights_director_vp(self):
        """Test role weights for director/VP level."""
        weights = get_role_weights("director_vp")
        assert weights.strategic_thinking == 1.0
        assert weights.cross_functional == 1.1
        assert weights.technical_literacy == 1.2

    def test_get_role_weights_senior_ic(self):
        """Test role weights for senior IC level."""
        weights = get_role_weights("senior_ic")
        assert weights.strategic_thinking == 0.8
        assert weights.business_acumen == 0.7
        assert weights.domain_expertise == 1.4

    def test_get_role_weights_invalid(self):
        """Test role weights for invalid level defaults to senior_executive."""
        weights = get_role_weights("invalid_level")
        # Should default to senior_executive
        assert weights.strategic_thinking == 1.3
        assert weights.cross_functional == 1.3

    def test_get_role_weights_custom_config(self):
        """Test role weights with custom configuration."""
        custom_weights = RoleLevelConfig.RoleWeights(strategic_thinking=2.0)
        custom_config = RoleLevelConfig(c_suite_weights=custom_weights)
        weights = get_role_weights("c_suite", custom_config)
        assert weights.strategic_thinking == 2.0


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple enhancements."""

    def test_executive_role_complex_requirement(self):
        """Test executive role with complex cross-functional requirement."""
        # Complex requirement
        req_text = "Lead strategy development across chemistry and clinical teams"

        # Classification
        req_type = classify_requirement_type(req_text)
        assert req_type == "executive"

        # Dual-track modifier
        dual_mod = dual_track_modifier(req_type, "executive")
        assert dual_mod == 1.0  # Aligned

        # Cross-functional complexity
        complexity, _ = assess_cross_functional_complexity(req_text)
        assert complexity in ["medium", "high"]

        # Cross-functional modifier
        cf_mod = cross_functional_modifier(complexity, True, True)
        assert cf_mod > 1.0  # Should have bonuses

    def test_ic_role_technical_requirement(self):
        """Test IC role with technical requirement."""
        # Technical requirement
        req_text = "Develop novel algorithms for data analysis"

        # Classification
        req_type = classify_requirement_type(req_text)
        assert req_type == "ic"

        # Skill categorization
        skill_cat = categorize_skill(req_text)
        assert skill_cat == "basic_technical"

        # Role weights for senior IC
        weights = get_role_weights("senior_ic")
        # Technical skills should be weighted higher for IC roles
        assert weights.technical_literacy > 1.0

    def test_experience_mismatch_scenario(self):
        """Test scenario with experience level mismatch."""
        # Leadership requirement for senior person with low self-score
        skill_cat = categorize_skill("Lead and manage teams")
        exp_mod = experience_level_modifier(skill_cat, 2, 25)  # 25 years experience, score 2
        assert exp_mod == 0.7  # Penalty for below baseline

    def test_proven_strength_bonus_scenario(self):
        """Test scenario with proven strength bonus."""
        # Cross-functional requirement matching proven strength
        req_text = "Cross-functional collaboration and integration"
        strengths = ["cross-functional", "integration"]

        complexity, _ = assess_cross_functional_complexity(req_text)
        matches = matches_proven_strength(req_text, strengths)

        assert matches is True

        cf_mod = cross_functional_modifier(complexity, matches, True)
        # Should have proven strength bonus (0.1) and executive bonus (0.05)
        base_mod = 1.15 if complexity == "medium" else (1.3 if complexity == "high" else 1.0)
        expected = base_mod + 0.1 + 0.05
        assert cf_mod == expected

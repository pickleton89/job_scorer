"""
Unit tests for emphasis_modifier() function.

Tests the emphasis detection logic that determines scoring modifiers
based on keywords in requirement text.
"""

from scoring.config import EmphasisIndicators, ScoringConfig
from scoring.scoring_engine import emphasis_modifier


class TestEmphasisModifier:
    """Test cases for the emphasis_modifier function."""

    def test_high_emphasis_keywords(self):
        """Test detection of high emphasis keywords."""
        # Test individual high emphasis keywords
        assert emphasis_modifier("Expert Python developer") == 0.5
        assert emphasis_modifier("Extensive experience with SQL") == 0.5
        assert emphasis_modifier("Strong background in data analysis") == 0.5
        assert emphasis_modifier("Proven track record") == 0.5
        assert emphasis_modifier("Deep understanding of algorithms") == 0.5
        assert emphasis_modifier("Comprehensive knowledge of AWS") == 0.5
        assert emphasis_modifier("Advanced machine learning skills") == 0.5
        assert emphasis_modifier("Thorough understanding of databases") == 0.5
        assert emphasis_modifier("Significant experience") == 0.5
        assert emphasis_modifier("Considerable expertise") == 0.5
        assert emphasis_modifier("Demonstrated proficiency") == 0.5
        assert emphasis_modifier("Extensively used Docker") == 0.5
        assert emphasis_modifier("Expertise in cloud computing") == 0.5
        assert emphasis_modifier("Mastery of JavaScript") == 0.5
        assert emphasis_modifier("Proficiency in React") == 0.5
        assert emphasis_modifier("Fluent in multiple languages") == 0.5

    def test_low_emphasis_keywords(self):
        """Test detection of low emphasis keywords."""
        # Test individual low emphasis keywords
        assert emphasis_modifier("Basic understanding of Python") == -0.5
        assert emphasis_modifier("Familiarity with SQL databases") == -0.5
        assert emphasis_modifier("Familiar with Git") == -0.5
        assert emphasis_modifier("Awareness of cloud platforms") == -0.5
        assert emphasis_modifier("Aware of security practices") == -0.5
        assert emphasis_modifier("Some experience with testing") == -0.5
        assert emphasis_modifier("Knowledge of REST APIs") == -0.5
        assert emphasis_modifier("Understanding of microservices") == -0.5
        assert emphasis_modifier("Exposure to machine learning") == -0.5
        assert emphasis_modifier("Introduction to DevOps") == -0.5
        assert emphasis_modifier("Fundamental programming concepts") == -0.5
        assert emphasis_modifier("Beginner level JavaScript") == -0.5
        assert emphasis_modifier("Novice understanding") == -0.5
        assert emphasis_modifier("Entry-level position") == -0.5
        assert emphasis_modifier("Basic understanding of algorithms") == -0.5

    def test_neutral_requirements(self):
        """Test requirements with no emphasis keywords."""
        assert emphasis_modifier("Python programming") == 0.0
        assert emphasis_modifier("SQL database management") == 0.0
        assert emphasis_modifier("Web development") == 0.0
        assert emphasis_modifier("Data analysis") == 0.0
        assert emphasis_modifier("Project management") == 0.0
        assert emphasis_modifier("Team collaboration") == 0.0
        assert emphasis_modifier("Problem solving") == 0.0
        assert emphasis_modifier("Communication skills") == 0.0

    def test_case_insensitive_detection(self):
        """Test that keyword detection is case insensitive."""
        # High emphasis - different cases
        assert emphasis_modifier("EXPERT level programming") == 0.5
        assert emphasis_modifier("Expert Level Programming") == 0.5
        assert emphasis_modifier("expert level programming") == 0.5
        assert emphasis_modifier("ExPeRt LeVeL pRoGrAmMiNg") == 0.5

        # Low emphasis - different cases
        assert emphasis_modifier("BASIC understanding") == -0.5
        assert emphasis_modifier("Basic Understanding") == -0.5
        assert emphasis_modifier("basic understanding") == -0.5
        assert emphasis_modifier("BaSiC uNdErStAnDiNg") == -0.5

    def test_high_emphasis_precedence(self):
        """Test that high emphasis takes precedence over low emphasis."""
        # When both high and low emphasis keywords are present
        assert emphasis_modifier("Expert level with basic tools") == 0.5
        assert emphasis_modifier("Advanced knowledge and basic understanding") == 0.5
        assert emphasis_modifier("Comprehensive expertise, some familiarity") == 0.5
        assert emphasis_modifier("Basic understanding but proven experience") == 0.5
        assert emphasis_modifier("Fundamental concepts with deep expertise") == 0.5

    def test_multiple_same_emphasis_keywords(self):
        """Test requirements with multiple keywords of the same emphasis level."""
        # Multiple high emphasis keywords
        assert emphasis_modifier("Expert and advanced proficiency") == 0.5
        assert emphasis_modifier("Extensive and comprehensive knowledge") == 0.5
        assert emphasis_modifier("Strong, proven, and demonstrated skills") == 0.5

        # Multiple low emphasis keywords
        assert emphasis_modifier("Basic familiarity and awareness") == -0.5
        assert emphasis_modifier("Some understanding and exposure") == -0.5
        assert emphasis_modifier("Fundamental, beginner, entry-level") == -0.5

    def test_keyword_as_substring(self):
        """Test that keywords are detected even as substrings."""
        # High emphasis keywords within larger words
        assert emphasis_modifier("Expertly handle complex problems") == 0.5
        assert emphasis_modifier("Extensively documented code") == 0.5

        # Low emphasis keywords within larger words
        assert emphasis_modifier("Basically functional requirements") == -0.5
        # Note: "familiarity" contains "familiar" so should be detected
        assert emphasis_modifier("Show familiarity with tools") == -0.5

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        assert emphasis_modifier("  Expert Python developer  ") == 0.5
        assert emphasis_modifier("\t\nBasic understanding\t\n") == -0.5
        assert emphasis_modifier("   Python programming   ") == 0.0
        assert emphasis_modifier("") == 0.0
        assert emphasis_modifier("   ") == 0.0

    def test_non_string_input(self):
        """Test handling of non-string input."""
        assert emphasis_modifier(None) == 0.0
        assert emphasis_modifier(123) == 0.0
        assert emphasis_modifier([]) == 0.0
        assert emphasis_modifier({}) == 0.0
        assert emphasis_modifier(True) == 0.0

    def test_empty_and_special_strings(self):
        """Test handling of empty and special string inputs."""
        assert emphasis_modifier("") == 0.0
        assert emphasis_modifier(" ") == 0.0
        assert emphasis_modifier("\n") == 0.0
        assert emphasis_modifier("\t") == 0.0
        assert emphasis_modifier("!@#$%^&*()") == 0.0
        assert emphasis_modifier("123456") == 0.0

    def test_custom_config(self):
        """Test emphasis_modifier with custom configuration."""
        # Create custom config with different modifiers
        custom_config = ScoringConfig(
            emphasis_modifier_high=0.3,
            emphasis_modifier_low=-0.3,
            emphasis_indicators=EmphasisIndicators(
                high_emphasis=("custom_high",),
                low_emphasis=("custom_low",)
            )
        )

        assert emphasis_modifier("custom_high requirement", custom_config) == 0.3
        assert emphasis_modifier("custom_low requirement", custom_config) == -0.3
        assert emphasis_modifier("expert requirement", custom_config) == 0.0  # Default keywords don't apply
        assert emphasis_modifier("basic requirement", custom_config) == 0.0   # Default keywords don't apply

    def test_real_world_examples(self):
        """Test with realistic job requirement examples."""
        # High emphasis examples
        assert emphasis_modifier("5+ years of expert-level Python development") == 0.5
        assert emphasis_modifier("Proven track record in machine learning projects") == 0.5
        assert emphasis_modifier("Deep understanding of distributed systems architecture") == 0.5
        assert emphasis_modifier("Extensive experience with cloud platforms (AWS/Azure)") == 0.5

        # Low emphasis examples
        assert emphasis_modifier("Basic familiarity with containerization technologies") == -0.5
        assert emphasis_modifier("Some exposure to microservices architecture") == -0.5
        assert emphasis_modifier("Fundamental understanding of database concepts") == -0.5
        assert emphasis_modifier("Entry-level knowledge of web development frameworks") == -0.5

        # Neutral examples
        assert emphasis_modifier("Bachelor's degree in Computer Science") == 0.0
        assert emphasis_modifier("Experience with version control systems") == 0.0
        assert emphasis_modifier("Ability to work in team environments") == 0.0
        assert emphasis_modifier("Strong problem-solving skills") == 0.5  # "strong" is high emphasis

    def test_edge_cases_with_punctuation(self):
        """Test emphasis detection with various punctuation."""
        assert emphasis_modifier("Expert-level programming skills") == 0.5
        assert emphasis_modifier("Basic, fundamental understanding") == -0.5
        assert emphasis_modifier("Advanced (5+ years) experience") == 0.5
        assert emphasis_modifier("Some/basic knowledge required") == -0.5
        assert emphasis_modifier("Expert: Python, SQL, JavaScript") == 0.5

"""
Unit tests for data validation and error handling functions.

This module tests the load_matrix function and related validation logic,
ensuring proper error handling for various input scenarios including
file system errors, CSV format issues, and data validation problems.

Author: Job Scorer Testing Suite
Created: 2025-05-23
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from scoring.data_loader import load_matrix


class TestLoadMatrix:
    """Test suite for the load_matrix function."""

    def test_valid_csv_loading(self):
        """Test successful loading of a valid CSV file."""
        # Create a temporary valid CSV file
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
Important,SQL databases,3
Desirable,Docker containers,2
Implicit,Team collaboration,5"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            # Verify basic structure
            assert len(df) == 4
            assert 'Classification' in df.columns
            assert 'Requirement' in df.columns
            assert 'SelfScore' in df.columns
            assert 'ClassWt' in df.columns
            assert 'EmphMod' in df.columns
            assert 'Weight' in df.columns

            # Verify data types
            assert df['SelfScore'].dtype == 'int64'
            assert df['ClassWt'].dtype == 'float64'
            assert df['EmphMod'].dtype == 'float64'

            # Verify specific values
            assert df.iloc[0]['Classification'] == 'Essential'
            assert df.iloc[0]['SelfScore'] == 4
            assert df.iloc[0]['ClassWt'] == 3.0  # Essential weight

        finally:
            os.unlink(temp_path)

    def test_file_not_found_error(self):
        """Test FileNotFoundError for non-existent file."""
        non_existent_path = Path("/non/existent/file.csv")

        with pytest.raises(FileNotFoundError, match="File not found"):
            load_matrix(non_existent_path)

    def test_invalid_path_type_error(self):
        """Test TypeError for invalid path type."""
        with pytest.raises(TypeError, match="Expected str or Path"):
            load_matrix(123)  # Invalid type

        with pytest.raises(TypeError, match="Expected str or Path"):
            load_matrix(['not', 'a', 'path'])  # Invalid type

    def test_directory_path_error(self):
        """Test ValueError when path points to a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Path is not a file"):
                load_matrix(Path(temp_dir))

    def test_empty_csv_file_error(self):
        """Test EmptyDataError for empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write nothing to create empty file
            temp_path = f.name

        try:
            with pytest.raises(pd.errors.EmptyDataError, match="The CSV file is empty"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_invalid_csv_format_error(self):
        """Test ValueError for invalid CSV format."""
        # Create a file with invalid CSV content that pandas can read but has missing columns
        invalid_content = "This is not a CSV file\nJust some random text"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name

        try:
            # This will fail on missing required columns, not CSV format
            with pytest.raises(ValueError, match="CSV is missing required columns"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_missing_required_columns_error(self):
        """Test ValueError for missing required columns."""
        # CSV missing Classification column
        csv_content = """Requirement,SelfScore
Python programming,4
SQL databases,3"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="CSV is missing required columns: Classification"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_missing_multiple_required_columns_error(self):
        """Test ValueError for multiple missing required columns."""
        # CSV missing both Classification and Requirement columns
        csv_content = """SelfScore
4
3"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="CSV is missing required columns"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_invalid_classification_values_error(self):
        """Test ValueError for invalid classification values."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
InvalidClass,SQL databases,3
Important,Docker containers,2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid Classification values found: InvalidClass"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_multiple_invalid_classification_values_error(self):
        """Test ValueError for multiple invalid classification values."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
BadClass1,SQL databases,3
BadClass2,Docker containers,2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid Classification values found"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_non_numeric_self_score_handling(self):
        """Test handling of non-numeric SelfScore values."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
Important,SQL databases,invalid
Desirable,Docker containers,2.5"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            # Non-numeric values should be converted to 0
            assert df.iloc[1]['SelfScore'] == 0  # 'invalid' -> 0
            # Numeric values should be preserved (and converted to int)
            assert df.iloc[0]['SelfScore'] == 4
            assert df.iloc[2]['SelfScore'] == 2  # 2.5 -> 2 (truncated)

        finally:
            os.unlink(temp_path)

    def test_self_score_clipping(self):
        """Test SelfScore values are clipped to valid range (0-5)."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,10
Important,SQL databases,-5
Desirable,Docker containers,3"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            # Values should be clipped to 0-5 range
            assert df.iloc[0]['SelfScore'] == 5  # 10 -> 5 (clipped)
            assert df.iloc[1]['SelfScore'] == 0  # -5 -> 0 (clipped)
            assert df.iloc[2]['SelfScore'] == 3  # 3 -> 3 (unchanged)

        finally:
            os.unlink(temp_path)

    def test_derived_columns_calculation(self):
        """Test calculation of derived columns (ClassWt, EmphMod, Weight)."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Expert Python programming,4
Important,Basic SQL knowledge,3
Desirable,Strong Docker skills,2
Implicit,Team collaboration,5"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            # Check ClassWt values
            assert df.iloc[0]['ClassWt'] == 3.0  # Essential
            assert df.iloc[1]['ClassWt'] == 2.0  # Important
            assert df.iloc[2]['ClassWt'] == 1.0  # Desirable
            assert df.iloc[3]['ClassWt'] == 0.5  # Implicit

            # Check EmphMod values (emphasis modifiers)
            assert df.iloc[0]['EmphMod'] == 0.5   # "Expert" -> high emphasis
            assert df.iloc[1]['EmphMod'] == -0.5  # "Basic" -> low emphasis
            assert df.iloc[2]['EmphMod'] == 0.5   # "Strong" -> high emphasis
            assert df.iloc[3]['EmphMod'] == 0.0   # neutral

            # Check Weight column (should match ClassWt)
            assert df.iloc[0]['Weight'] == df.iloc[0]['ClassWt']
            assert df.iloc[1]['Weight'] == df.iloc[1]['ClassWt']

        finally:
            os.unlink(temp_path)

    def test_string_path_input(self):
        """Test that string paths are accepted and converted properly."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Test with string path instead of Path object
            df = load_matrix(temp_path)  # Pass string, not Path

            assert len(df) == 1
            assert df.iloc[0]['Classification'] == 'Essential'

        finally:
            os.unlink(temp_path)

    def test_whitespace_in_data(self):
        """Test handling of whitespace in CSV data."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
Important,SQL databases,3"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            # pandas should handle whitespace automatically
            assert len(df) == 2
            assert df.iloc[0]['SelfScore'] == 4

        finally:
            os.unlink(temp_path)

    def test_load_matrix_derived_column_error_handling(self):
        """Test load_matrix error handling during derived column processing."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Mock emphasis_modifier to raise an exception
            with patch('scoring.data_loader.emphasis_modifier') as mock_emphasis:
                mock_emphasis.side_effect = Exception("Emphasis processing error")

                with pytest.raises(ValueError, match="Error processing derived columns:"):
                    load_matrix(Path(temp_path))

        finally:
            os.unlink(temp_path)

    def test_load_matrix_selfscore_processing_error(self):
        """Test load_matrix error handling during SelfScore processing."""
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Mock pandas to_numeric to raise an exception
            with patch('pandas.to_numeric') as mock_to_numeric:
                mock_to_numeric.side_effect = Exception("Numeric conversion error")

                with pytest.raises(ValueError, match="Error processing SelfScore values: Numeric conversion error"):
                    load_matrix(Path(temp_path))

        finally:
            os.unlink(temp_path)

    def test_unicode_decode_error_simulation(self):
        """Test handling of files with encoding issues."""
        # Create a file with binary content that can't be decoded as UTF-8
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            # Write some binary data that's not valid UTF-8
            f.write(b'\xff\xfe\x00\x00Invalid UTF-8 content')
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unable to decode CSV file"):
                load_matrix(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_large_csv_file_handling(self):
        """Test handling of larger CSV files."""
        # Create a CSV with many rows to test performance and memory handling
        csv_lines = ["Classification,Requirement,SelfScore"]
        classifications = ["Essential", "Important", "Desirable", "Implicit"]

        for i in range(100):
            classification = classifications[i % 4]
            csv_lines.append(f"{classification},Skill {i},3")

        csv_content = "\n".join(csv_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_matrix(Path(temp_path))

            assert len(df) == 100
            assert all(col in df.columns for col in ['Classification', 'Requirement', 'SelfScore', 'ClassWt', 'EmphMod', 'Weight'])

        finally:
            os.unlink(temp_path)


class TestCoreGapSkillValidation:
    """Test suite for CoreGapSkill validation logic."""

    def test_core_gap_skill_validation_in_context(self):
        """Test CoreGapSkill validation through load_matrix and compute_scores integration."""
        # This tests the validation indirectly through the normal workflow
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,1
Important,SQL databases,0"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            from scoring.scoring_engine import compute_scores

            df = load_matrix(Path(temp_path))
            result = compute_scores(df)

            # Should have core gaps
            assert result['core_gap'] is True
            assert len(result['core_gap_skills']) == 2

            # Verify CoreGapSkill objects are created properly
            gap_skills = result['core_gap_skills']
            for skill in gap_skills:
                assert hasattr(skill, 'name')
                assert hasattr(skill, 'classification')
                assert hasattr(skill, 'self_score')
                assert hasattr(skill, 'threshold')
                assert hasattr(skill, 'severity')

        finally:
            os.unlink(temp_path)

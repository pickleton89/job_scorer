"""
Shared pytest fixtures for job_scorer tests.

This module provides common fixtures used across unit and integration tests.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def sample_csv_v1():
    """Provide path to sample v1 CSV data for testing."""
    return Path(__file__).parent / "data" / "v1" / "basic_test.csv"


@pytest.fixture
def sample_csv_v2():
    """Provide path to sample v2 CSV data for testing."""
    return Path(__file__).parent / "data" / "v2" / "basic_test.csv"


@pytest.fixture
def sample_dataframe_v2():
    """Provide sample DataFrame with v2 format for testing."""
    return pd.DataFrame(
        {
            "Requirement": [
                "Python programming",
                "Expert SQL",
                "Basic data visualization",
                "Machine learning",
            ],
            "Classification": ["Essential", "Important", "Desirable", "Implicit"],
            "SelfScore": [4, 3, 2, 1],
        }
    )


@pytest.fixture
def malformed_csv(tmp_path):
    """Create a malformed CSV file for error testing."""
    csv_file = tmp_path / "malformed.csv"
    csv_file.write_text("Invalid,CSV,Content\nMissing,Headers")
    return csv_file


@pytest.fixture
def empty_csv(tmp_path):
    """Create an empty CSV file for error testing."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    return csv_file


@pytest.fixture
def missing_columns_csv(tmp_path):
    """Create CSV with missing required columns."""
    csv_file = tmp_path / "missing_columns.csv"
    csv_file.write_text("WrongColumn,AnotherWrong\nValue1,Value2")
    return csv_file

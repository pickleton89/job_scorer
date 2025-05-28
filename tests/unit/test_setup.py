"""
Basic setup verification tests.

These tests verify that our pytest configuration is working correctly
and that we can import the scoring module.
"""

import pytest

from scoring import scoring_v2


def test_pytest_setup() -> None:
    """Verify pytest is working correctly."""
    assert True, "Basic pytest functionality is working"

def test_python_path() -> None:
    """Verify we can access the project modules."""
    # Check that we can import from the scoring package
    try:
        assert hasattr(scoring_v2, 'main'), "scoring_v2 module should have main function"
    except ImportError as e:
        pytest.fail(f"Could not import scoring.scoring_v2: {e}")

def test_fixtures_available(sample_dataframe_v2):  # type: ignore[no-untyped-def]
    """Verify our fixtures are working."""
    import pandas as pd

    assert sample_dataframe_v2 is not None
    assert isinstance(sample_dataframe_v2, pd.DataFrame)
    assert len(sample_dataframe_v2) > 0
    assert 'Requirement' in sample_dataframe_v2.columns
    assert 'Classification' in sample_dataframe_v2.columns

def test_test_data_exists(sample_csv_v2):  # type: ignore[no-untyped-def]
    """Verify test data files exist."""
    import pathlib

    assert isinstance(sample_csv_v2, pathlib.Path)
    assert sample_csv_v2.exists(), f"Test data file should exist: {sample_csv_v2}"

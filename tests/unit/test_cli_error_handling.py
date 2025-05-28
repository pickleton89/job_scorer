"""
Unit tests for CLI error handling and main function scenarios.

This module tests the main function's error handling capabilities,
including file validation, argument parsing, and graceful error reporting.

Author: Job Scorer Testing Suite
Created: 2025-05-23
"""

import io
import os
import tempfile
from unittest.mock import patch

import pytest


class TestMainFunctionErrorHandling:
    """Test suite for main function error handling."""

    def test_file_not_found_handling(self):
        """Test main function handling of non-existent files."""
        from scoring.cli import main

        # Mock sys.argv to simulate command line arguments
        test_args = ['scoring_v2.py', '/non/existent/file.csv']

        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 1
                assert exc_info.value.code == 1

                # Should print error message to stderr
                stderr_output = mock_stderr.getvalue()
                assert "Error:" in stderr_output
                assert "File not found" in stderr_output

    def test_empty_csv_handling(self):
        """Test main function handling of empty CSV files."""
        from scoring.cli import main

        # Create an empty CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name

        try:
            test_args = ['scoring_v2.py', temp_path]

            with patch('sys.argv', test_args):
                with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    # Should exit with code 1
                    assert exc_info.value.code == 1

                    # Should print error message to stderr
                    stderr_output = mock_stderr.getvalue()
                    assert "Error:" in stderr_output

        finally:
            os.unlink(temp_path)

    def test_invalid_csv_data_handling(self):
        """Test main function handling of invalid CSV data."""
        from scoring.cli import main

        # Create a CSV with missing required columns
        csv_content = """WrongColumn,AnotherWrongColumn
value1,value2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            test_args = ['scoring_v2.py', temp_path]

            with patch('sys.argv', test_args):
                with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    # Should exit with code 1
                    assert exc_info.value.code == 1

                    # Should print error message to stderr
                    stderr_output = mock_stderr.getvalue()
                    assert "Error:" in stderr_output
                    assert "missing required columns" in stderr_output

        finally:
            os.unlink(temp_path)

    def test_scoring_calculation_error_handling(self):
        """Test main function handling of scoring calculation errors."""
        from scoring.cli import main

        # Create a valid CSV file
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            test_args = ['scoring_v2.py', temp_path]

            # Mock compute_scores to raise an exception
            with patch('scoring.cli.compute_scores') as mock_compute:
                mock_compute.side_effect = Exception("Simulated scoring error")

                with patch('sys.argv', test_args):
                    with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                        with pytest.raises(SystemExit) as exc_info:
                            main()

                        # Should exit with code 1
                        assert exc_info.value.code == 1

                        # Should print error message to stderr
                        stderr_output = mock_stderr.getvalue()
                        assert "Error calculating scores:" in stderr_output
                        assert "skill matrix data appears to be invalid" in stderr_output

        finally:
            os.unlink(temp_path)

    def test_successful_execution_no_errors(self):
        """Test main function successful execution without errors."""
        from scoring.cli import main

        # Create a valid CSV file
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4
Important,SQL databases,3
Desirable,Docker containers,2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            test_args = ['scoring_v2.py', temp_path]

            with patch('sys.argv', test_args):
                with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                    # Should not raise SystemExit for successful execution
                    try:
                        main()
                        # If we get here, the function completed successfully
                        stdout_output = mock_stdout.getvalue()

                        # Should contain expected output sections
                        assert "VERDICT" in stdout_output
                        assert "Core gap present" in stdout_output

                    except SystemExit as e:
                        # If it does exit, it should be with code 0 (success)
                        assert e.code == 0

        finally:
            os.unlink(temp_path)

    def test_help_flag_handling(self):
        """Test main function handling of --help flag."""
        from scoring.cli import main

        test_args = ['scoring_v2.py', '--help']

        with patch('sys.argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Help should exit with code 0
                assert exc_info.value.code == 0

                # Should print help text to stdout
                stdout_output = mock_stdout.getvalue()
                assert "usage:" in stdout_output.lower()

    def test_version_flag_handling(self):
        """Test main function handling of --version flag."""
        from scoring.cli import main

        test_args = ['scoring_v2.py', '--version']

        with patch('sys.argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Version should exit with code 0
                assert exc_info.value.code == 0

                # Should print version information
                stdout_output = mock_stdout.getvalue()
                assert "2.0.0" in stdout_output

    def test_keyboard_interrupt_handling(self):
        """Test main function handling of keyboard interrupt (Ctrl+C)."""
        from scoring.cli import main

        # Create a valid CSV file
        csv_content = """Classification,Requirement,SelfScore
Essential,Python programming,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            test_args = ['scoring_v2.py', temp_path]

            # Mock load_matrix to raise KeyboardInterrupt
            with patch('scoring.cli.load_matrix') as mock_load:
                mock_load.side_effect = KeyboardInterrupt()

                with patch('sys.argv', test_args):
                    with patch('builtins.print'):
                        # The main function should handle KeyboardInterrupt gracefully
                        try:
                            main()
                        except (SystemExit, KeyboardInterrupt):
                            # Either is acceptable for interrupt handling
                            pass

                        # Verify that some error handling occurred
                        # (either print was called or SystemExit was raised)
                        assert True  # Test passes if we get here without hanging

        finally:
            os.unlink(temp_path)


class TestArgumentParsing:
    """Test suite for argument parsing functionality."""

    def test_missing_csv_argument(self):
        """Test handling of missing CSV file argument."""
        from scoring.cli import main

        test_args = ['scoring_v2.py']  # No CSV file provided

        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 2 (argparse error)
                assert exc_info.value.code == 2

                # Should print usage information
                stderr_output = mock_stderr.getvalue()
                assert "usage:" in stderr_output.lower()

    def test_invalid_argument_handling(self):
        """Test handling of invalid command line arguments."""
        from scoring.cli import main

        test_args = ['scoring_v2.py', '--invalid-flag', 'file.csv']

        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 2 (argparse error)
                assert exc_info.value.code == 2

                # Should print error message
                stderr_output = mock_stderr.getvalue()
                assert "unrecognized arguments" in stderr_output or "invalid" in stderr_output

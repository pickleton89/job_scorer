#!/usr/bin/env python3
"""
Test runner for the job skill matrix scoring system.

This script helps verify both the current (v1) and new (v2) implementations.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Literal, TypedDict

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent))

class ScriptExecutionOutput(TypedDict):
    """Type definition for test output dictionary.

    Attributes:
        exit_code: The exit code of the test process
        stdout: Standard output from the test
        stderr: Standard error from the test
        success: Whether the test was successful
    """
    exit_code: int
    stdout: str
    stderr: str
    success: bool

def run_test(script_path: str, test_file: str, version: Literal["v1", "v2"] = "v1") -> ScriptExecutionOutput:
    """Run a single test case and return the output as a dictionary."""
    try:
        # Run the script and capture output
        result = subprocess.run(
            ["python", script_path, test_file],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the output (this is a simple example - adjust based on actual output)
        output = ScriptExecutionOutput(
            exit_code=0,
            stdout=result.stdout,
            stderr=result.stderr,
            success=True
        )

    except subprocess.CalledProcessError as e:
        output = ScriptExecutionOutput(
            exit_code=e.returncode,
            stdout=e.stdout,
            stderr=e.stderr,
            success=False
        )

    return output

def main() -> None:
    parser = argparse.ArgumentParser(description="Test runner for job skill matrix scoring")
    parser.add_argument("--version", choices=["v1", "v2"], default="v1",
                      help="Which version to test (v1 or v2)")
    args = parser.parse_args()

    # Determine which script to test
    script_name = "scoring/cli.py"
    if args.version == "v2":
        script_name = "scoring/scoring_v2.py"

    # Get the absolute path to the script
    script_path = str(Path(__file__).parent.parent / script_name)

    # Find all test files for this version
    test_dir = Path(__file__).parent / "data" / args.version
    test_files = list(test_dir.glob("*.csv"))

    if not test_files:
        print(f"No test files found in {test_dir}")
        return

    print(f"Running {len(test_files)} test(s) for {args.version}...\n")

    # Run tests
    for test_file in test_files:
        print(f"Testing: {test_file.name}")
        print("-" * 50)

        result = run_test(script_path, str(test_file), args.version)

        # Print test results
        if result["success"]:
            print("✅ Test passed")
            print("Output:")
            print(result["stdout"])
        else:
            print("❌ Test failed")
            print("Error:")
            print(result["stderr"])

        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()

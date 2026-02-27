"""Test runner script for Oplaadpalen integration."""
import subprocess
import sys


def run_tests():
    """Run tests with coverage."""
    args = [
        "pytest",
        "tests/",
        "-v",
        "--cov=custom_components/oplaadpalen",
        "--cov-report=html",
        "--cov-report=term-missing",
    ]
    
    return subprocess.run(args).returncode


if __name__ == "__main__":
    sys.exit(run_tests())

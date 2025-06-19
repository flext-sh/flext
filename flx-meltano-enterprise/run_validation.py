#!/usr/bin/env python3
"""
Run complete validation for FLX-Meltano Enterprise project.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and report results."""
    print(f"\n{'=' * 60}")
    print(f"🔍 {description}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("🚀 FLX-MELTANO ENTERPRISE VALIDATION")
    print("=" * 60)

    # Change to project directory
    Path(__file__).parent

    checks = [
        # Code quality checks
        ("poetry run ruff check src/", "Ruff Linting"),
        ("poetry run black --check src/", "Black Formatting"),
        (
            "poetry run mypy src/flx --ignore-missing-imports",
            "MyPy Type Checking - Core",
        ),
        (
            "poetry run mypy src/flx_api --ignore-missing-imports",
            "MyPy Type Checking - API",
        ),
        (
            "poetry run mypy src/flx_cli --ignore-missing-imports",
            "MyPy Type Checking - CLI",
        ),
        # Security checks
        ("poetry run bandit -r src/ -ll", "Bandit Security Check"),
        # Import checks
        (
            "python -c 'import sys; sys.path.insert(0, \"src\"); import flx'",
            "Import FLX Core",
        ),
        (
            "python -c 'import sys; sys.path.insert(0, \"src\"); import flx_api'",
            "Import FLX API",
        ),
        (
            "python -c 'import sys; sys.path.insert(0, \"src\"); import flx_cli'",
            "Import FLX CLI",
        ),
        (
            "python -c 'import sys; sys.path.insert(0, \"src\"); import flx_web'",
            "Import FLX Web",
        ),
        # Test execution
        ("poetry run pytest tests/test_core_daemon.py -v", "Core Daemon Tests"),
        ("poetry run pytest tests/test_grpc_server.py -v", "gRPC Server Tests"),
        ("poetry run pytest tests/test_api_endpoints.py -v", "API Endpoint Tests"),
        ("poetry run pytest tests/test_cli.py -v", "CLI Tests"),
    ]

    results = []
    for cmd, description in checks:
        results.append(run_command(cmd, description))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0

    print(f"\nTotal checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {percentage:.1f}%")

    if percentage == 100:
        print("\n🎉 ALL CHECKS PASSED! Project is ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

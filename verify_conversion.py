#!/usr/bin/env python3
"""
Verify that Python 3.12+ syntax has been successfully converted.
"""

import subprocess
from pathlib import Path


def verify_conversion():
    """Verify the conversion was successful."""

    # Check for remaining class[T]: patterns
    result_class = subprocess.run(
        [
            "find",
            "/home/marlonsc/flext/legacy",
            "-name",
            "*.py",
            "-exec",
            "grep",
            "-l",
            "class.*\\[.*\\]:",
            "{}",
            ";",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # Check for remaining def func[T]( patterns
    result_func = subprocess.run(
        [
            "find",
            "/home/marlonsc/flext/legacy",
            "-name",
            "*.py",
            "-exec",
            "grep",
            "-l",
            "def.*\\[.*\\](",
            "{}",
            ";",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # Test compilation of some key converted files
    test_files = [
        "/home/marlonsc/flext/legacy/flx/src/flx/core/types/common.py",
        "/home/marlonsc/flext/legacy/flx-adapter-example/src/flx_adapter_example/pagination.py",
        "/home/marlonsc/flext/legacy/flx-meltano-enterprise/src/flx_core/commands/decorators.py",
        "/home/marlonsc/flext/legacy/flx-meltano-enterprise/src/flx_core/grpc/types.py",
        "/home/marlonsc/flext/legacy/flx-meltano-enterprise/src/flx_core/domain/advanced_types.py",
    ]

    class_files = (
        result_class.stdout.strip().split("\n") if result_class.stdout.strip() else []
    )
    func_files = (
        result_func.stdout.strip().split("\n") if result_func.stdout.strip() else []
    )

    # Remove false positives and test files that might contain patterns intentionally
    class_files = [
        f
        for f in class_files
        if f and not any(x in f for x in ["test_", "example_", "/tests/", "/examples/"])
    ]
    func_files = [
        f
        for f in func_files
        if f and not any(x in f for x in ["test_", "example_", "/tests/", "/examples/"])
    ]

    if class_files:
        for _f in class_files[:5]:  # Show first 5
            pass
        if len(class_files) > 5:
            pass

    if func_files:
        for _f in func_files[:5]:  # Show first 5
            pass
        if len(func_files) > 5:
            pass

    all_passed = True

    for test_file in test_files:
        if Path(test_file).exists():
            result = subprocess.run(
                ["python", "-m", "py_compile", test_file],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                pass
            else:
                all_passed = False
        else:
            pass

    if all_passed:
        pass
    else:
        pass

    # Show improvements made

    remaining_issues = len(class_files) + len(func_files)
    if remaining_issues == 0:
        pass
    else:
        pass


if __name__ == "__main__":
    verify_conversion()

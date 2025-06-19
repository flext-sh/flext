#!/usr/bin/env python3
"""MonkeyType utility for DCApiX.

This script provides simple commands to run MonkeyType
for collecting and applying types in the DCApiX project.
"""

import argparse
import subprocess
import sys


def run_monkeytype_tests(test_path: str | None = None) -> int:
    """Run tests with MonkeyType to collect runtime types."""
    cmd = ["monkeytype", "run", "-m", "pytest"]

    if test_path:
        cmd.append(test_path)

    print(f"Running tests with MonkeyType: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\nType collection completed successfully.")
        print("To list modules with type information:")
        print("  python dc_api_x_monkeytype.py list")
        print("To apply types to a module:")
        print("  python dc_api_x_monkeytype.py apply --module dc_api_x.some_module")

    return result.returncode


def list_modules() -> int:
    """List modules with collected type information."""
    cmd = ["monkeytype", "list-modules"]

    print("Listing modules with type information:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\nTo apply types to a module:")
        print("  python dc_api_x_monkeytype.py apply --module dc_api_x.some_module")

    return result.returncode


def apply_types(module: str) -> int:
    """Apply collected types to a specific module."""
    cmd = ["monkeytype", "apply", module]

    print(f"Applying types to module {module}:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print(f"\nTypes applied successfully to module {module}")
        print("Check the changes and run mypy to validate the types.")

    return result.returncode


def generate_stub(module) -> Any:
    """Generate a stub with collected types for a module."""
    cmd = ["monkeytype", "stub", module]

    print(f"Generating stub for module {module}:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print(f"\nStub generated successfully for module {module}")
        print("Review the stub and apply manually if necessary.")

    return result.returncode


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MonkeyType utility for DCApiX")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # Run command
    run_parser = subparsers.add_parser("run", help="Run tests with MonkeyType")
    run_parser.add_argument("--test-path", help="Specific test path")

    # List command
    subparsers.add_parser("list", help="List modules with type information")

    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply types to a module")
    apply_parser.add_argument("--module", required=True, help="Module path")

    # Stub command
    stub_parser = subparsers.add_parser("stub", help="Generate stub for a module")
    stub_parser.add_argument("--module", required=True, help="Module path")

    args = parser.parse_args()

    if args.command == "run":
        return run_monkeytype_tests(args.test_path)
    if args.command == "list":
        return list_modules()
    if args.command == "apply":
        return apply_types(args.module)
    if args.command == "stub":
        return generate_stub(args.module)
    print(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

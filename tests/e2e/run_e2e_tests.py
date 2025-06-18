#!/usr/bin/env python3
"""
Script to run end-to-end tests for LDAP components.

This script manages the Docker environment and runs the E2E test suite.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Set up the test environment."""
    e2e_dir = Path(__file__).parent

    # Ensure we're in the right directory
    os.chdir(e2e_dir)

    # Check Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    # Check required Python packages
    required_packages = ["pytest", "docker", "psycopg2-binary", "ldap3", "faker"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    return not missing_packages


def build_containers():
    """Build Docker containers if needed."""
    subprocess.run(["docker-compose", "build"], check=True)


def start_containers():
    """Start Docker containers."""
    subprocess.run(["docker-compose", "up", "-d"], check=True)


def stop_containers(keep=False):
    """Stop Docker containers."""
    if not keep:
        subprocess.run(
            ["docker-compose", "down", "-v"], capture_output=True, check=False
        )


def run_tests(args):
    """Run the test suite."""
    pytest_args = [
        "pytest",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-p",
        "no:warnings",  # Disable warnings for cleaner output
    ]

    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(
            [
                "--cov=tap_ldap",
                "--cov=target_ldap",
                "--cov=flx_ldap",
                "--cov-report=html",
                "--cov-report=term",
            ]
        )

    # Add markers if specified
    if args.markers:
        pytest_args.extend(["-m", args.markers])

    # Add specific tests if provided
    if args.tests:
        pytest_args.extend(args.tests)
    else:
        # Run all E2E tests
        pytest_args.extend(["scenarios/"])

    # Add any extra pytest args
    if args.pytest_args:
        pytest_args.extend(args.pytest_args.split())

    # Set environment variable if keeping containers
    if args.keep_containers:
        os.environ["E2E_KEEP_CONTAINERS"] = "true"

    # Run tests
    return subprocess.run(pytest_args, check=False).returncode


def show_logs(service=None):
    """Show Docker container logs."""
    cmd = ["docker-compose", "logs", "--tail=100"]
    if service:
        cmd.append(service)

    subprocess.run(cmd, check=False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run end-to-end tests for LDAP components"
    )

    parser.add_argument(
        "--skip-setup", action="store_true", help="Skip environment setup checks"
    )

    parser.add_argument(
        "--skip-build", action="store_true", help="Skip building Docker containers"
    )

    parser.add_argument(
        "--keep-containers",
        action="store_true",
        help="Keep Docker containers running after tests",
    )

    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )

    parser.add_argument(
        "--markers", "-m", help="Run tests matching given mark expression"
    )

    parser.add_argument(
        "--logs",
        nargs="?",
        const="all",
        help="Show Docker logs (optionally specify service)",
    )

    parser.add_argument("--pytest-args", help="Additional arguments to pass to pytest")

    parser.add_argument(
        "tests", nargs="*", help="Specific test files or directories to run"
    )

    args = parser.parse_args()

    # Show logs if requested
    if args.logs:
        service = None if args.logs == "all" else args.logs
        show_logs(service)
        return 0

    # Setup environment
    if not args.skip_setup and not setup_environment():
        return 1

    # Build containers if needed
    if not args.skip_build:
        try:
            build_containers()
        except subprocess.CalledProcessError:
            return 1

    # Run tests
    try:
        return run_tests(args)
    except KeyboardInterrupt:
        return 1
    finally:
        if not args.keep_containers:
            stop_containers()


if __name__ == "__main__":
    sys.exit(main())

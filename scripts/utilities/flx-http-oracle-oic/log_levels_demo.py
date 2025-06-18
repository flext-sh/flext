#!/usr/bin/env python3
"""Demonstration of all log levels in the OIC CLI.

This script shows how different log levels affect the output.
"""

import os
import subprocess
from pathlib import Path


def run_command_with_log_level(log_level: str, command: list[str]) -> None:
    """Run a CLI command with a specific log level."""
    # Full command with log level
    full_cmd = ["poetry", "run", "flx-oic", "--log-level", log_level, *command]

    # Run the command
    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
        check=False,
    )

    if result.stdout:
        pass

    if result.stderr:
        # Limit stderr output for higher log levels
        lines = result.stderr.strip().split("\n")
        if log_level in {"ERROR", "CRITICAL"} and len(lines) > 10:
            pass


def main() -> None:
    """Run demonstration of all log levels."""
    # Test command - version is simple and always works
    test_command = ["version"]

    # Test all log levels
    log_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in log_levels:
        run_command_with_log_level(level, test_command)

    # Show environment variable usage

    # Set environment variable
    env = os.environ.copy()
    env["LOG_LEVEL"] = "WARNING"

    result = subprocess.run(
        ["poetry", "run", "flx-oic", "version"],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).parent.parent,
        check=False,
    )

    if result.stdout:
        pass

    if result.stderr:
        pass

    # Show shortcuts

    subprocess.run(
        ["poetry", "run", "flx-oic", "--debug", "version"],
        cwd=Path(__file__).parent.parent,
        check=False,
    )

    subprocess.run(
        ["poetry", "run", "flx-oic", "--trace", "version"],
        cwd=Path(__file__).parent.parent,
        check=False,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Test script for PEP8 compliant CLI with TRACE logging."""

import os
import subprocess
from pathlib import Path


def run_command(cmd: str, env_file: str = ".env.test") -> None:
    """Run a CLI command with specific environment."""
    print(f"\n{'=' * 79}")
    print(f"Command: {cmd}")
    print('=' * 79)

    # Set up environment
    env = os.environ.copy()
    env["DOTENV_PATH"] = env_file

    # Change to project directory
    project_dir = Path(__file__).parent / "gruponos_oic_wms"

    try:
        # Run command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=env, check=False
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\nReturn code: {result.returncode}")

    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    """Run CLI tests with PEP8 compliance."""
    print("Testing GN-WMS CLI with PEP8 compliance")
    print("=" * 79)
    print("Environment: OUTPUT=TABLE, LOG_LEVEL=TRACE")

    # Copy test env file
    env_test = Path("gruponos_oic_wms/.env.test")
    env_file = Path("gruponos_oic_wms/.env")

    if env_test.exists() and not env_file.exists():
        import shutil
        shutil.copy(env_test, env_file)
        print("Created .env from .env.test")

    # Test commands
    commands = [
        # Help command
        "poetry run gn-wms --help",

        # Version with default format (TABLE from .env)
        "poetry run gn-wms version",

        # Config show with default format
        "poetry run gn-wms config show",

        # Override format to JSON
        "poetry run gn-wms version --format json",

        # List entities
        "poetry run gn-wms list-entities --limit 5",

        # Health check
        "poetry run gn-wms health",

        # Show logs with TRACE level
        "poetry run gn-wms show-logs --hours 1 --level TRACE",
    ]

    for cmd in commands:
        run_command(cmd)

    # Test Python script compliance
    print("\n" + "=" * 79)
    print("Testing PEP8 compliance with flake8")
    print("=" * 79)

    # Run flake8 on the CLI module
    flake8_cmd = (
        "cd gruponos-poc-oic-wms && "
        "poetry run flake8 src/gn_oic_wms_db/cli.py --max-line-length=79"
    )
    run_command(flake8_cmd)

    # Check line lengths with simple Python
    print("\n" + "=" * 79)
    print("Checking line lengths (PEP8: max 79 chars)")
    print("=" * 79)

    cli_file = Path("gruponos_oic_wms/src/gn_oic_wms_db/cli.py")
    if cli_file.exists():
        with open(cli_file, encoding="utf-8") as f:
            lines = f.readlines()

        long_lines = [
            (i + 1, len(line.rstrip()))
            for i, line in enumerate(lines)
            if len(line.rstrip()) > 79
        ]

        if long_lines:
            print(f"Found {len(long_lines)} lines exceeding 79 characters:")
            for line_no, length in long_lines[:10]:  # Show first 10
                print(f"  Line {line_no}: {length} chars")
        else:
            print("✓ All lines are within 79 characters (PEP8 compliant)")


if __name__ == "__main__":
    main()

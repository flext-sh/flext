#!/usr/bin/env python3
"""Test script for the standardized GN OIC-WMS CLI."""

import subprocess


def run_command(command) -> None:
    """Run a CLI command and display output."""
    print(f"\n{'=' * 60}")
    print(f"Running: {command}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Return code: {result.returncode}")
    except Exception as e:
        print(f"Error running command: {e}")


def main() -> None:
    """Test various CLI commands."""
    base_cmd = "gn-wms"

    # Test commands with different output formats
    commands = [
        # Help
        f"{base_cmd} --help",
        # Version (table format - default)
        f"{base_cmd} version",
        # Version (JSON format)
        f"{base_cmd} version --format json",
        # Config show (table format)
        f"{base_cmd} config show",
        # Config show (JSON format)
        f"{base_cmd} config show --format json",
        # List entities (table format)
        f"{base_cmd} list-entities --entity-type=all --limit=5",
        # List entities (CSV format)
        f"{base_cmd} list-entities --entity-type=orders --format csv",
        # Health check (table format)
        f"{base_cmd} health",
        # Show logs (table format)
        f"{base_cmd} show-logs --hours=1 --level=INFO",
        # Show logs (JSON format)
        f"{base_cmd} show-logs --hours=1 --format json",
    ]

    for cmd in commands:
        run_command(cmd)


if __name__ == "__main__":
    main()

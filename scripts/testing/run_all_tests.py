#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-testing/SKILL.md
"""Run all FLEXT tests across workspace projects.

Thin wrapper around run_pytest_all_projects.py for CI compatibility.
Referenced by: .github/workflows/flx_comprehensive_tests.yml
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all FLEXT tests across workspace projects.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would run without executing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.dry_run:
        print("Would delegate to: scripts/testing/run_pytest_all_projects.py")
        return 0

    # Delegate to the canonical test runner
    runner_path = Path(__file__).parent / "run_pytest_all_projects.py"
    if not runner_path.exists():
        print(f"ERROR: canonical runner not found: {runner_path}", file=sys.stderr)
        return 1

    spec = importlib.util.spec_from_file_location("runner", runner_path)
    if spec is None or spec.loader is None:
        print(f"ERROR: cannot load {runner_path}", file=sys.stderr)
        return 1

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())

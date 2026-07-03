#!/usr/bin/env python3
# Owner-Skill: .agents/skills/scripts-infra/SKILL.md
"""Validate gate contract conformance module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flext_infra import c, t
from flext_infra.validate.gate_contract import FlextInfraGateContractValidator
from flext_infra.validate.gate_contract_models import FlextInfraGateContractModels


def eprint(message: str) -> None:
    """Print one message to stderr."""
    print(message, file=sys.stderr)


def parse_args(argv: t.StrSequence) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Validate gate contract conformance for validator/fixer scripts.",
    )
    _ = parser.add_argument(
        "--root",
        required=True,
        help="Repository root path (scripts are scanned under <root>/scripts)",
    )
    _ = parser.add_argument(
        "--mode",
        choices=["baseline", "strict"],
        default="baseline",
    )
    _ = parser.add_argument(
        "--all",
        action="store_true",
        help="Check all scripts, not just validators/fixers",
    )
    return parser.parse_args(argv)


def usage_exit_code(code: int) -> int:
    """Normalize argparse exit codes to the script contract."""
    if code in c.Infra.SCRIPT_EXIT_CODE_VALUES:
        return code
    return int(c.Infra.ScriptExitCode.USAGE)


def run_main(argv: t.StrSequence) -> tuple[int, int]:
    """Run the validator and return exit code plus violation count."""
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        code = (
            exc.code
            if isinstance(exc.code, int)
            else int(
                c.Infra.ScriptExitCode.USAGE,
            )
        )
        return (usage_exit_code(code), 0)

    validator = FlextInfraGateContractValidator.model_validate(
        {
            "check_all": bool(args.all),
            "mode": c.Infra.OperationMode(str(args.mode)),
            "workspace_root": Path(str(args.root)).resolve(),
        },
    )
    outcome = validator.run()
    return (outcome.exit_code, outcome.violation_count)


def main() -> int:
    """Main function."""
    try:
        code, violation_count = run_main(sys.argv[1:])
    except FlextInfraGateContractModels.UsageError as exc:
        eprint(f"ERROR: {exc}")
        code = int(c.Infra.ScriptExitCode.USAGE)
        violation_count = 0
    except FlextInfraGateContractModels.InfraError as exc:
        eprint(f"ERROR: {exc}")
        code = int(c.Infra.ScriptExitCode.INFRA)
        violation_count = 0
    except Exception as exc:
        eprint(f"ERROR: unexpected failure: {exc}")
        code = int(c.Infra.ScriptExitCode.INFRA)
        violation_count = 0

    print(json.dumps({"violation_count": violation_count}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

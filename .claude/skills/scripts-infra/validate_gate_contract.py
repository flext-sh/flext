#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Validate gate contract conformance module."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_INFRA = 3

OWNER_MARKER_RE = re.compile(
    r"^# Owner-Skill:\s+(.claude/skills/[a-z0-9][-a-z0-9]*/SKILL\.md)\s*$"
)
ARTIFACT_NAME_RE = re.compile(r"[a-z][-a-z0-9]*--[a-z]+--[a-z][-a-z0-9]*\.[a-z]+")
REPORTS_PATH_RE = re.compile(r"\.reports/([^\s\"']+)")
BASH_EXIT_RE = re.compile(r"^\s*exit\s+(\d+)")
INTERACTIVE_PY_RE = re.compile(r"\binput\s*\(")
INTERACTIVE_SH_RE = re.compile(
    r"\bread\s+-p\b|\bselect\s+\w+\s+in\b|\bdialog\b|\bwhiptail\b"
)
INTERACTIVE_GATE_RE = re.compile(r"--interactive")

MAX_HEADER_LINES = 10
MIN_CODE_LINES = 20

VALIDATOR_NAMES = re.compile(
    r"^(enforce|check|validate|test|verify|audit|lint|scan)[-_]"
)
FIXER_NAMES = re.compile(
    r"^(fix|autofix|repair|correct|reorder|refactor|standardize)[-_]"
)


class UsageError(Exception):
    """UsageError class."""

    pass


class InfraError(Exception):
    """InfraError class."""

    pass


class Ansi:
    """Ansi class."""

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


@dataclass(frozen=True)
class Violation:
    """Violation class."""

    script: str
    check: str
    message: str
    severity: str = "error"


@dataclass
class ScriptInfo:
    """ScriptInfo class."""

    path: str
    extension: str
    role: str
    violations: list[Violation] = field(default_factory=list)


def eprint(message: str) -> None:
    """Eprint function."""
    print(message, file=sys.stderr)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """parse_args function."""
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


def tracked_scripts(root: Path) -> list[Path]:
    """tracked_scripts function."""
    scripts_root = root / "scripts"
    if not scripts_root.exists() or not scripts_root.is_dir():
        return []

    result = subprocess.run(
        [
            "/usr/bin/env",
            "git",
            "ls-files",
            "scripts/*.sh",
            "scripts/*.py",
            "scripts/**/*.sh",
            "scripts/**/*.py",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise InfraError(stderr or "git ls-files failed")

    scripts: list[Path] = []
    for line in sorted(set(result.stdout.splitlines())):
        rel = line.strip()
        if not rel:
            continue
        path = Path(rel)
        if path.name == "__init__.py":
            continue
        scripts.append(path)
    return scripts


def classify_role(script_path: Path) -> str:
    """classify_role function."""
    name = script_path.stem

    if (
        script_path.as_posix().startswith(("scripts/lib/", "scripts/core/"))
        and not VALIDATOR_NAMES.match(name)
        and not FIXER_NAMES.match(name)
    ):
        return "other"

    if VALIDATOR_NAMES.match(name):
        return "validator"
    if FIXER_NAMES.match(name):
        return "fixer"
    return "other"


def read_content(root: Path, script_path: Path) -> str:
    """read_content function."""
    full_path = root / script_path
    try:
        return full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def read_header(content: str) -> list[str]:
    """read_header function."""
    return content.splitlines()[:MAX_HEADER_LINES]


def count_code_lines(content: str, extension: str) -> int:
    """count_code_lines function."""
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if extension == ".py" and stripped.startswith("#"):
            continue
        if extension == ".sh" and stripped.startswith("#"):
            continue
        count += 1
    return count


def check_shebang(header: list[str], extension: str) -> Violation | None:
    """check_shebang function."""
    if not header:
        return Violation(
            script="",
            check="shebang",
            message="empty file - no shebang found",
        )

    first = header[0]
    if extension == ".py" and not first.startswith("#!/usr/bin/env python"):
        return Violation(
            script="",
            check="shebang",
            message=f"expected '#!/usr/bin/env python3', got: {first!r}",
        )
    if (
        extension == ".sh"
        and not first.startswith("#!/usr/bin/env bash")
        and not first.startswith("#!/bin/bash")
    ):
        return Violation(
            script="",
            check="shebang",
            message=f"expected '#!/usr/bin/env bash', got: {first!r}",
        )
    return None


def check_owner_marker(header: list[str]) -> Violation | None:
    """check_owner_marker function."""
    for line in header:
        if OWNER_MARKER_RE.match(line):
            return None
    return Violation(
        script="",
        check="owner_marker",
        message="missing Owner-Skill marker in first 10 lines",
    )


def check_exit_codes(content: str, extension: str) -> list[Violation]:
    """check_exit_codes function."""
    if extension != ".sh":
        return []

    violations: list[Violation] = []
    for i, line in enumerate(content.splitlines(), 1):
        match = BASH_EXIT_RE.match(line)
        if not match:
            continue
        code = int(match.group(1))
        if code not in {0, 1, 2, 3}:
            violations.append(
                Violation(
                    script="",
                    check="exit_code",
                    message=f"line {i}: exit {code} - only 0/1/2/3 allowed",
                )
            )
    return violations


def check_interactive(
    content: str, extension: str, script_path: str
) -> list[Violation]:
    """check_interactive function."""
    _ = script_path
    if INTERACTIVE_GATE_RE.search(content):
        return []

    violations: list[Violation] = []
    pattern = INTERACTIVE_PY_RE if extension == ".py" else INTERACTIVE_SH_RE

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if extension == ".py" and stripped.startswith(('"""', "'''", '"', "'")):
            continue
        if pattern.search(line):
            violations.append(
                Violation(
                    script="",
                    check="interactive",
                    message=f"line {i}: interactive prompt without --interactive gate",
                    severity="warning",
                )
            )
    return violations


def check_artifact_naming(content: str) -> list[Violation]:
    """check_artifact_naming function."""
    violations: list[Violation] = []
    for i, line in enumerate(content.splitlines(), 1):
        for match in REPORTS_PATH_RE.finditer(line):
            filename = Path(match.group(1)).name
            if "$" in filename or "*" in filename or "{" in filename:
                continue
            if filename == ".gitkeep":
                continue
            if not ARTIFACT_NAME_RE.fullmatch(filename):
                violations.append(
                    Violation(
                        script="",
                        check="artifact_naming",
                        message=(
                            f"line {i}: artifact '{filename}' does not match "
                            "<skill>--<kind>--<slug>.<ext>"
                        ),
                        severity="warning",
                    )
                )
    return violations


def check_min_code_lines(content: str, extension: str, role: str) -> Violation | None:
    """check_min_code_lines function."""
    if role == "other":
        return None
    code_lines = count_code_lines(content, extension)
    if code_lines < MIN_CODE_LINES:
        return Violation(
            script="",
            check="min_code_lines",
            message=(
                f"{role} has only {code_lines} code lines "
                f"(minimum {MIN_CODE_LINES}) - may be a stub"
            ),
            severity="warning",
        )
    return None


def validate_script(root: Path, script_path: Path, *, check_all: bool) -> ScriptInfo:
    """validate_script function."""
    extension = script_path.suffix
    role = classify_role(script_path)
    info = ScriptInfo(path=script_path.as_posix(), extension=extension, role=role)

    if role == "other" and not check_all:
        return info

    content = read_content(root, script_path)
    if not content:
        info.violations.append(
            Violation(
                script=info.path,
                check="readable",
                message="could not read file",
            )
        )
        return info

    header = read_header(content)

    shebang_violation = check_shebang(header, extension)
    if shebang_violation:
        info.violations.append(
            Violation(
                script=info.path,
                check=shebang_violation.check,
                message=shebang_violation.message,
            )
        )

    owner_violation = check_owner_marker(header)
    if owner_violation:
        info.violations.append(
            Violation(
                script=info.path,
                check=owner_violation.check,
                message=owner_violation.message,
            )
        )

    for violation in check_exit_codes(content, extension):
        info.violations.append(
            Violation(
                script=info.path,
                check=violation.check,
                message=violation.message,
            )
        )

    for violation in check_interactive(content, extension, info.path):
        info.violations.append(
            Violation(
                script=info.path,
                check=violation.check,
                message=violation.message,
                severity=violation.severity,
            )
        )

    for violation in check_artifact_naming(content):
        info.violations.append(
            Violation(
                script=info.path,
                check=violation.check,
                message=violation.message,
                severity=violation.severity,
            )
        )

    min_lines_violation = check_min_code_lines(content, extension, role)
    if min_lines_violation:
        info.violations.append(
            Violation(
                script=info.path,
                check=min_lines_violation.check,
                message=min_lines_violation.message,
                severity=min_lines_violation.severity,
            )
        )

    return info


def print_results(scripts: list[ScriptInfo]) -> None:
    """print_results function."""
    eprint(f"{Ansi.CYAN}Gate Contract Validation{Ansi.RESET}")
    eprint(f"{Ansi.CYAN}{'SCRIPT':<60} {'ROLE':<10} {'STATUS':<10} DETAILS{Ansi.RESET}")

    for script in scripts:
        if script.role == "other" and not script.violations:
            continue

        errors = [v for v in script.violations if v.severity == "error"]
        warnings = [v for v in script.violations if v.severity == "warning"]

        if errors:
            status = f"{Ansi.RED}FAIL{Ansi.RESET}"
        elif warnings:
            status = f"{Ansi.YELLOW}WARN{Ansi.RESET}"
        else:
            status = f"{Ansi.GREEN}OK{Ansi.RESET}"

        detail_parts: list[str] = []
        if errors:
            detail_parts.append(f"{len(errors)} error(s)")
        if warnings:
            detail_parts.append(f"{len(warnings)} warning(s)")
        detail = ", ".join(detail_parts) if detail_parts else "contract compliant"

        eprint(f"{script.path:<60} {script.role:<10} {status:<22} {detail}")

        for violation in script.violations:
            color = Ansi.RED if violation.severity == "error" else Ansi.YELLOW
            eprint(f"  {color}[{violation.check}]{Ansi.RESET} {violation.message}")


def report_path_for(root: Path) -> Path:
    """report_path_for function."""
    return root / ".claude" / "skills" / "scripts-infra" / "report.json"


def write_report(root: Path, scripts: list[ScriptInfo], mode: str) -> Path:
    """write_report function."""
    report_path = report_path_for(root)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    all_violations: list[dict[str, str]] = []
    for script in scripts:
        all_violations.extend(
            {
                "check": violation.check,
                "message": violation.message,
                "script": violation.script,
                "severity": violation.severity,
            }
            for violation in script.violations
        )

    checked_count = sum(1 for s in scripts if s.role != "other" or s.violations)
    error_count = sum(1 for s in scripts for v in s.violations if v.severity == "error")
    warning_count = sum(
        1 for s in scripts for v in s.violations if v.severity == "warning"
    )

    payload: dict[str, object] = {
        "checked": checked_count,
        "errors": error_count,
        "mode": mode,
        "violations": sorted(
            all_violations,
            key=lambda x: (str(x.get("script", "")), str(x.get("check", ""))),
        ),
        "warnings": warning_count,
    }

    _ = report_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report_path


def run_main(argv: list[str]) -> tuple[int, int]:
    """run_main function."""
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
        return (EXIT_USAGE if code not in {0, 1, 2, 3} else code, 0)

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        msg = f"root directory not found: {root}"
        raise UsageError(msg)

    try:
        scripts_list = tracked_scripts(root)
    except (UsageError, InfraError):
        raise
    except Exception as exc:
        raise InfraError(str(exc)) from exc

    results = [
        validate_script(root, script, check_all=bool(args.all))
        for script in scripts_list
    ]

    print_results(results)
    try:
        report_path = write_report(root, results, str(args.mode))
    except OSError as exc:
        msg = f"failed to write report: {exc}"
        raise InfraError(msg) from exc

    error_count = sum(1 for s in results for v in s.violations if v.severity == "error")
    warning_count = sum(
        1 for s in results for v in s.violations if v.severity == "warning"
    )

    gate_scripts = [s for s in results if s.role in {"validator", "fixer"}]
    ok_count = sum(
        1 for s in gate_scripts if not any(v.severity == "error" for v in s.violations)
    )

    summary_line = (
        f"\n{Ansi.CYAN}Summary:{Ansi.RESET} "
        f"gate_scripts={len(gate_scripts)} "
        f"{Ansi.GREEN}ok={ok_count}{Ansi.RESET} "
        f"{Ansi.RED}errors={error_count}{Ansi.RESET} "
        f"{Ansi.YELLOW}warnings={warning_count}{Ansi.RESET}"
    )
    eprint(summary_line)
    eprint(f"Report: {report_path}")

    return (EXIT_FAIL if error_count > 0 else EXIT_PASS, error_count)


def main() -> int:
    """Main function."""
    try:
        code, violation_count = run_main(sys.argv[1:])
    except UsageError as exc:
        eprint(f"ERROR: {exc}")
        code = EXIT_USAGE
        violation_count = 0
    except InfraError as exc:
        eprint(f"ERROR: {exc}")
        code = EXIT_INFRA
        violation_count = 0
    except Exception as exc:
        eprint(f"ERROR: unexpected failure: {exc}")
        code = EXIT_INFRA
        violation_count = 0

    print(json.dumps({"violation_count": int(violation_count)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

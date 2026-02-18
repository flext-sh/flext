#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Validate Owner-Skill ownership markers for tracked scripts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


OWNER_MARKER_RE = re.compile(
    r"^# Owner-Skill:\s+(.claude/skills/([a-z0-9][-a-z0-9]*)/SKILL\.md)\s*$"
)
MAX_HEADER_LINES = 10

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_INFRA = 3


class Ansi:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


class SkillUsageError(Exception):
    pass


class SkillInfraError(Exception):
    pass


@dataclass(frozen=True)
class ScriptCheckResult:
    script: str
    status: str
    details: str
    owner_skill: str | None


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that each tracked script under scripts/ has exactly one "
            "Owner-Skill marker and a matching SKILL.md scripts entry."
        ),
    )
    _ = parser.add_argument(
        "--root",
        required=True,
        help="Repository root path used to resolve files and run git ls-files",
    )
    _ = parser.add_argument(
        "--mode",
        choices=["baseline", "strict"],
        default="baseline",
        help="Validation mode (accepted for skill_validate contract compatibility)",
    )
    return parser.parse_args(argv)


def tracked_scripts(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "scripts/*.sh",
            "scripts/*.py",
            "scripts/**/*.sh",
            "scripts/**/*.py",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SkillInfraError(result.stderr.strip() or "git ls-files failed")

    scripts: list[Path] = []
    for line in sorted(set(result.stdout.splitlines())):
        if not line.strip():
            continue
        path = Path(line)
        if path.name == "__init__.py":
            continue
        if not (repo_root / path).exists():
            continue
        scripts.append(path)
    return scripts


def read_header(repo_root: Path, script_path: Path) -> list[str]:
    full_path = repo_root / script_path
    try:
        with full_path.open("r", encoding="utf-8") as handle:
            lines = []
            for _ in range(MAX_HEADER_LINES):
                line = handle.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except OSError as exc:
        raise SkillInfraError(f"cannot read script header: {script_path}") from exc
    return lines


def scripts_section(skill_file: Path) -> str:
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise SkillInfraError(f"cannot read skill file: {skill_file}") from exc

    lines = content.splitlines()
    in_section = False
    section_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if line.strip() == "## Scripts":
                in_section = True
                continue
            if in_section:
                break

        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines)


def script_listed_in_skill(skill_file: Path, script_path: Path) -> bool:
    section = scripts_section(skill_file)
    if not section.strip():
        return False

    escaped = re.escape(script_path.as_posix())
    pattern = rf"`{escaped}`|{escaped}"
    return re.search(pattern, section) is not None


def candidate_skill(script_path: Path) -> str:
    path = script_path.as_posix()
    if path.startswith("scripts/validation/"):
        return "scripts-validation"
    if path.startswith("scripts/security/"):
        return "scripts-security"
    if path.startswith("scripts/architecture/"):
        return "scripts-architecture"
    if path.startswith("scripts/testing/"):
        return "scripts-testing"
    if path.startswith("scripts/dependencies/"):
        return "scripts-dependencies"
    if path.startswith("scripts/maintenance/"):
        return "scripts-maintenance"
    if path.startswith("scripts/git/"):
        return "scripts-maintenance"
    if path.startswith("scripts/lib/"):
        return "scripts-infra"
    if path.startswith("scripts/core/"):
        return "scripts-infra"
    if path.startswith("scripts/config/"):
        return "scripts-infra"
    if path.startswith("scripts/makefiles/"):
        return "scripts-infra"
    if path.startswith("scripts/analysis/"):
        return "scripts-architecture"
    return "scripts-infra"


def validate_script(
    repo_root: Path,
    script_path: Path,
) -> tuple[ScriptCheckResult, dict[str, str] | None]:
    header = read_header(repo_root, script_path)
    markers = [match for line in header if (match := OWNER_MARKER_RE.match(line))]

    if not markers:
        candidate = candidate_skill(script_path)
        return (
            ScriptCheckResult(
                script=script_path.as_posix(),
                status="UNOWNED",
                details=f"missing Owner-Skill marker (candidate: {candidate})",
                owner_skill=None,
            ),
            {
                "script": script_path.as_posix(),
                "candidate_skill": candidate,
                "candidate_skill_file": f".claude/skills/{candidate}/SKILL.md",
                "reason": "missing_owner_marker",
            },
        )

    if len(markers) > 1:
        return (
            ScriptCheckResult(
                script=script_path.as_posix(),
                status="VIOLATION",
                details="multiple Owner-Skill markers in first 10 lines",
                owner_skill=None,
            ),
            None,
        )

    marker = markers[0]
    owner_rel = marker.group(1)
    owner_skill = marker.group(2)
    owner_file = repo_root / owner_rel

    if not owner_file.exists():
        return (
            ScriptCheckResult(
                script=script_path.as_posix(),
                status="VIOLATION",
                details=f"owner skill file does not exist: {owner_rel}",
                owner_skill=owner_skill,
            ),
            None,
        )

    if not script_listed_in_skill(owner_file, script_path):
        return (
            ScriptCheckResult(
                script=script_path.as_posix(),
                status="VIOLATION",
                details="script not listed under target SKILL.md ## Scripts section",
                owner_skill=owner_skill,
            ),
            None,
        )

    return (
        ScriptCheckResult(
            script=script_path.as_posix(),
            status="OK",
            details="owner marker and SKILL.md scripts section validated",
            owner_skill=owner_skill,
        ),
        None,
    )


def status_color(status: str) -> str:
    if status == "OK":
        return Ansi.GREEN
    if status == "UNOWNED":
        return Ansi.YELLOW
    return Ansi.RED


def print_table(results: list[ScriptCheckResult]) -> None:
    eprint(f"{Ansi.CYAN}Script Ownership Validation{Ansi.RESET}")
    eprint(f"{Ansi.CYAN}{'SCRIPT':<55} {'STATUS':<10} DETAILS{Ansi.RESET}")
    for result in results:
        color = status_color(result.status)
        eprint(
            f"{result.script:<55} {color}{result.status:<10}{Ansi.RESET} {result.details}",
        )


def write_candidates(
    repo_root: Path,
    candidates: list[dict[str, str]],
) -> Path:
    report_path = repo_root / ".claude" / "skills" / "scripts-infra" / "report.json"
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "total_candidates": len(candidates),
            "candidates": sorted(candidates, key=lambda item: item["script"]),
        }
        _ = report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise SkillInfraError(f"cannot write candidate report: {report_path}") from exc
    return report_path


def run_main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
        return (
            code
            if code in (EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_INFRA)
            else EXIT_USAGE
        )

    repo_root = Path(args.root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        eprint(f"{Ansi.RED}error:{Ansi.RESET} --root is not a directory: {repo_root}")
        return EXIT_USAGE

    try:
        scripts = tracked_scripts(repo_root)

        results: list[ScriptCheckResult] = []
        candidates: list[dict[str, str]] = []
        for script in scripts:
            result, candidate = validate_script(repo_root, script)
            results.append(result)
            if candidate is not None:
                candidates.append(candidate)

        print_table(results)
        report_path = write_candidates(repo_root, candidates)

        ok_count = sum(1 for item in results if item.status == "OK")
        unowned_count = sum(1 for item in results if item.status == "UNOWNED")
        violation_only_count = sum(1 for item in results if item.status == "VIOLATION")
        total_violations = unowned_count + violation_only_count

        summary = (
            f"\n{Ansi.CYAN}Summary:{Ansi.RESET} total={len(results)} "
            + f"{Ansi.GREEN}ok={ok_count}{Ansi.RESET} "
            + f"{Ansi.YELLOW}unowned={unowned_count}{Ansi.RESET} "
            + f"{Ansi.RED}violations={violation_only_count}{Ansi.RESET} "
            + f"{Ansi.RED}total_noncompliant={total_violations}{Ansi.RESET}"
        )
        eprint(summary)
        eprint(f"Candidates report: {report_path.relative_to(repo_root)}")

        print(json.dumps({"violation_count": total_violations}, separators=(",", ":")))
        return EXIT_PASS if total_violations == 0 else EXIT_FAIL
    except SkillUsageError as exc:
        eprint(f"{Ansi.RED}error:{Ansi.RESET} {exc}")
        return EXIT_USAGE
    except SkillInfraError as exc:
        eprint(f"{Ansi.RED}error:{Ansi.RESET} {exc}")
        return EXIT_INFRA
    except Exception as exc:
        eprint(f"{Ansi.RED}error:{Ansi.RESET} unexpected failure: {exc}")
        return EXIT_INFRA


def main() -> None:
    code = run_main(sys.argv[1:])
    if code not in (EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_INFRA):
        code = EXIT_INFRA
    raise SystemExit(code)


if __name__ == "__main__":
    main()

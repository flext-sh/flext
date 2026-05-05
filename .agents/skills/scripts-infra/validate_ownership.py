#!/usr/bin/env python3
# Owner-Skill: .agents/skills/scripts-infra/SKILL.md
"""Validate Owner-Skill ownership markers for tracked scripts."""

from __future__ import annotations

import argparse
import json
import operator
import re
import sys
from pathlib import Path
from typing import Annotated, ClassVar

from flext_infra import c, m, t, u


class Ansi:
    """Ansi class."""

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


class SkillUsageError(Exception):
    """SkillUsageError class."""


class SkillInfraError(Exception):
    """SkillInfraError class."""


class ScriptCheckResult(m.BaseModel):
    """ScriptCheckResult class."""

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True)

    script: str = u.Field(description="Script file path")
    status: str = u.Field(description="Validation status (OK, UNOWNED, VIOLATION)")
    details: str = u.Field(description="Detailed status message")
    owner_skill: Annotated[
        str | None,
        u.Field(
            description="Owner skill identifier if applicable",
        ),
    ] = None


def eprint(message: str) -> None:
    """Eprint function."""
    print(message, file=sys.stderr)


def parse_args(argv: t.StrSequence) -> argparse.Namespace:
    """parse_args function."""
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


def tracked_scripts(repo_root: Path) -> t.SequenceOf[Path]:
    """tracked_scripts function."""
    result = u.Cli.run_raw(
        [
            "/usr/bin/env",
            "git",
            "ls-files",
            "scripts/*.sh",
            "scripts/*.py",
            "scripts/**/*.sh",
            "scripts/**/*.py",
        ],
        cwd=repo_root,
    )
    if result.failure:
        raise SkillInfraError(result.error or "git ls-files failed")
    output = result.value
    if output.exit_code != 0:
        raise SkillInfraError(output.stderr.strip() or "git ls-files failed")

    scripts: list[Path] = []
    for line in sorted(set(output.stdout.splitlines())):
        if not line.strip():
            continue
        path = Path(line)
        if path.name == "__init__.py":
            continue
        if not (repo_root / path).exists():
            continue
        scripts.append(path)
    return scripts


def read_header(repo_root: Path, script_path: Path) -> t.StrSequence:
    """read_header function."""
    full_path = repo_root / script_path
    try:
        with full_path.open("r", encoding="utf-8") as handle:
            lines: list[str] = []
            for _ in range(c.Infra.SCRIPT_HEADER_MAX_LINES):
                line = handle.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except OSError as exc:
        msg = f"cannot read script header: {script_path}"
        raise SkillInfraError(msg) from exc
    return lines


def scripts_section(skill_file: Path) -> str:
    """scripts_section function."""
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"cannot read skill file: {skill_file}"
        raise SkillInfraError(msg) from exc

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
    """script_listed_in_skill function."""
    section = scripts_section(skill_file)
    if not section.strip():
        return False

    escaped = re.escape(script_path.as_posix())
    pattern = rf"`{escaped}`|{escaped}"
    return re.search(pattern, section) is not None


def candidate_skill(script_path: Path) -> str:
    """candidate_skill function."""
    path = script_path.as_posix()
    skill = "scripts-infra"
    match path:
        case value if value.startswith("scripts/validation/"):
            skill = "scripts-validation"
        case value if value.startswith("scripts/security/"):
            skill = "scripts-security"
        case value if value.startswith("scripts/architecture/"):
            skill = "scripts-architecture"
        case value if value.startswith("scripts/testing/"):
            skill = "scripts-testing"
        case value if value.startswith("scripts/dependencies/"):
            skill = "scripts-dependencies"
        case value if value.startswith("scripts/maintenance/"):
            skill = "scripts-maintenance"
        case value if value.startswith("scripts/git/"):
            skill = "scripts-maintenance"
        case value if value.startswith("scripts/lib/"):
            skill = "scripts-infra"
        case value if value.startswith("scripts/core/"):
            skill = "scripts-infra"
        case value if value.startswith("scripts/settings/"):
            skill = "scripts-infra"
        case value if value.startswith("scripts/makefiles/"):
            skill = "scripts-infra"
        case value if value.startswith("scripts/analysis/"):
            skill = "scripts-architecture"
    return skill


def validate_script(
    repo_root: Path,
    script_path: Path,
) -> tuple[ScriptCheckResult, t.StrMapping | None]:
    """validate_script function."""
    script = script_path.as_posix()
    header = read_header(repo_root, script_path)
    markers = [
        match for line in header if (match := c.Infra.SKILL_OWNER_MARKER_RE.match(line))
    ]
    candidate_report: t.StrMapping | None = None
    result: ScriptCheckResult

    if not markers:
        candidate = candidate_skill(script_path)
        result = ScriptCheckResult(
            script=script,
            status="UNOWNED",
            details=f"missing Owner-Skill marker (candidate: {candidate})",
            owner_skill=None,
        )
        candidate_report = {
            "script": script,
            "candidate_skill": candidate,
            "candidate_skill_file": f".agents/skills/{candidate}/SKILL.md",
            "reason": "missing_owner_marker",
        }
    elif len(markers) > 1:
        result = ScriptCheckResult(
            script=script,
            status="VIOLATION",
            details="multiple Owner-Skill markers in first 10 lines",
            owner_skill=None,
        )
    else:
        marker = markers[0]
        owner_rel = marker.group(1)
        owner_skill = marker.group(2)
        owner_file = repo_root / owner_rel

        if not owner_file.exists():
            result = ScriptCheckResult(
                script=script,
                status="VIOLATION",
                details=f"owner skill file does not exist: {owner_rel}",
                owner_skill=owner_skill,
            )
        elif not script_listed_in_skill(owner_file, script_path):
            result = ScriptCheckResult(
                script=script,
                status="VIOLATION",
                details="script not listed under target SKILL.md ## Scripts section",
                owner_skill=owner_skill,
            )
        else:
            result = ScriptCheckResult(
                script=script,
                status="OK",
                details="owner marker and SKILL.md scripts section validated",
                owner_skill=owner_skill,
            )

    return result, candidate_report


def status_color(status: str) -> str:
    """status_color function."""
    match status:
        case "OK":
            color = Ansi.GREEN
        case "UNOWNED":
            color = Ansi.YELLOW
        case _:
            color = Ansi.RED
    return color


def print_table(results: t.SequenceOf[ScriptCheckResult]) -> None:
    """print_table function."""
    eprint(f"{Ansi.CYAN}Script Ownership Validation{Ansi.RESET}")
    eprint(f"{Ansi.CYAN}{'SCRIPT':<55} {'STATUS':<10} DETAILS{Ansi.RESET}")
    for result in results:
        color = status_color(result.status)
        eprint(
            f"{result.script:<55} {color}{result.status:<10}{Ansi.RESET} {result.details}",
        )


def write_candidates(
    repo_root: Path,
    candidates: t.SequenceOf[t.StrMapping],
) -> Path:
    """write_candidates function."""
    report_path = repo_root / ".agents" / "skills" / "scripts-infra" / "report.json"
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "total_candidates": len(candidates),
            "candidates": sorted(candidates, key=operator.itemgetter("script")),
        }
        _ = report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        msg = f"cannot write candidate report: {report_path}"
        raise SkillInfraError(msg) from exc
    return report_path


def run_main(argv: t.StrSequence) -> int:
    """run_main function."""
    exit_code = c.Infra.ScriptExitCode.INFRA
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        match exc.code:
            case int() as raw_code if raw_code in c.Infra.SCRIPT_EXIT_CODE_VALUES:
                exit_code = c.Infra.ScriptExitCode(raw_code)
            case _:
                exit_code = c.Infra.ScriptExitCode.USAGE
    else:
        try:
            repo_root = Path(args.root).resolve()
            if not repo_root.exists() or not repo_root.is_dir():
                eprint(
                    f"{Ansi.RED}error:{Ansi.RESET} --root is not a directory: {repo_root}"
                )
                exit_code = c.Infra.ScriptExitCode.USAGE
            else:
                validations = [
                    validate_script(repo_root, script)
                    for script in tracked_scripts(repo_root)
                ]
                results = [result for result, _ in validations]
                candidates = [
                    candidate for _, candidate in validations if candidate is not None
                ]

                print_table(results)
                report_path = write_candidates(repo_root, candidates)

                ok_count = sum(1 for item in results if item.status == "OK")
                unowned_count = sum(1 for item in results if item.status == "UNOWNED")
                violation_only_count = len(results) - ok_count - unowned_count
                total_violations = len(results) - ok_count

                summary = (
                    f"\n{Ansi.CYAN}Summary:{Ansi.RESET} total={len(results)} "
                    f"{Ansi.GREEN}ok={ok_count}{Ansi.RESET} "
                    f"{Ansi.YELLOW}unowned={unowned_count}{Ansi.RESET} "
                    f"{Ansi.RED}violations={violation_only_count}{Ansi.RESET} "
                    f"{Ansi.RED}total_noncompliant={total_violations}{Ansi.RESET}"
                )
                eprint(summary)
                eprint(f"Candidates report: {report_path.relative_to(repo_root)}")

                print(
                    json.dumps(
                        {"violation_count": total_violations},
                        separators=(",", ":"),
                    )
                )
                exit_code = (
                    c.Infra.ScriptExitCode.PASS
                    if total_violations == 0
                    else c.Infra.ScriptExitCode.FAIL
                )
        except SkillUsageError as exc:
            eprint(f"{Ansi.RED}error:{Ansi.RESET} {exc}")
            exit_code = c.Infra.ScriptExitCode.USAGE
        except SkillInfraError as exc:
            eprint(f"{Ansi.RED}error:{Ansi.RESET} {exc}")
            exit_code = c.Infra.ScriptExitCode.INFRA
        except Exception as exc:
            eprint(f"{Ansi.RED}error:{Ansi.RESET} unexpected failure: {exc}")
            exit_code = c.Infra.ScriptExitCode.INFRA
    return int(exit_code)


def main() -> None:
    """Main function."""
    code = run_main(sys.argv[1:])
    if code not in c.Infra.SCRIPT_EXIT_CODE_VALUES:
        code = int(c.Infra.ScriptExitCode.INFRA)
    raise SystemExit(code)


if __name__ == "__main__":
    main()

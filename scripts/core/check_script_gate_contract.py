#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ALLOWED_BASH_EXITS = {"0", "1", "2", "3"}
PROMPT_PATTERNS = (
    "read -p",
    "select ",
    "inquirer",
)


@dataclass(frozen=True)
class Violation:
    file: str
    check: str
    message: str


def tracked_scripts(root: Path) -> list[Path]:
    scripts = root / "scripts"
    files: list[Path] = []
    for path in scripts.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".sh"}:
            continue
        files.append(path)
    return sorted(files)


def header_violations(path: Path, rel: str) -> list[Violation]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    top = lines[:10]
    violations: list[Violation] = []

    if path.suffix == ".py":
        if not top or top[0].strip() != "#!/usr/bin/env python3":
            violations.append(Violation(rel, "shebang", "missing python shebang"))
    if path.suffix == ".sh":
        if not top or top[0].strip() != "#!/usr/bin/env bash":
            violations.append(Violation(rel, "shebang", "missing bash shebang"))

    if not any(line.startswith("# Owner-Skill:") for line in top):
        violations.append(
            Violation(
                rel, "owner-skill", "missing Owner-Skill marker in first 10 lines"
            )
        )
    return violations


def is_validator_or_fixer(rel: str) -> bool:
    name = Path(rel).name.lower()
    return any(
        token in name
        for token in ("validate", "validator", "fix", "audit", "lint", "check")
    )


def bash_exit_violations(path: Path, rel: str) -> list[Violation]:
    if path.suffix != ".sh":
        return []
    violations: list[Violation] = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
    ):
        text = line.strip()
        match = re.match(r"^exit\s+(\d+)\s*$", text)
        if match and match.group(1) not in ALLOWED_BASH_EXITS:
            violations.append(
                Violation(
                    rel,
                    "exit-codes",
                    f"line {number}: disallowed exit code {match.group(1)}",
                )
            )
    return violations


def prompt_violations(path: Path, rel: str) -> list[Violation]:
    violations: list[Violation] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lower = text.lower()
    if "--interactive" in lower:
        return []
    for pattern in PROMPT_PATTERNS:
        if pattern in lower:
            violations.append(
                Violation(
                    rel,
                    "interactive",
                    f"contains interactive prompt pattern '{pattern}' without --interactive guard",
                )
            )
    return violations


def artifact_violations(path: Path, rel: str) -> list[Violation]:
    violations: list[Violation] = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
    ):
        if (
            ".sisyphus/" in line
            and "artifact" not in line.lower()
            and "reports" not in line.lower()
        ):
            violations.append(
                Violation(
                    rel,
                    "artifact-path",
                    f"line {number}: .sisyphus path should use artifact naming helpers",
                )
            )
    return violations


def size_violations(path: Path, rel: str) -> list[Violation]:
    if not is_validator_or_fixer(rel):
        return []
    lines = [
        line
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip()
    ]
    if len(lines) < 20:
        return [
            Violation(
                rel,
                "non-empty",
                "validator/fixer scripts must have at least 20 non-empty lines",
            )
        ]
    return []


def collect(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for path in tracked_scripts(root):
        rel = path.relative_to(root).as_posix()
        violations.extend(header_violations(path, rel))
        violations.extend(bash_exit_violations(path, rel))
        violations.extend(prompt_violations(path, rel))
        violations.extend(artifact_violations(path, rel))
        violations.extend(size_violations(path, rel))
    return violations


def configured_max_violations(root: Path) -> int:
    config = root / "docs/architecture/architecture_config.json"
    if not config.exists():
        return 0
    payload = json.loads(config.read_text(encoding="utf-8", errors="ignore"))
    docs_validation = payload.get("docs_validation", {})
    gate_contract = docs_validation.get("gate_contract", {})
    value = gate_contract.get("max_violations", 0)
    return int(value) if isinstance(value, int | float) else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=".reports/docs/evidence/gate-contract.json")
    parser.add_argument("--max-violations", type=int)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    violations = collect(root)
    max_violations = (
        args.max_violations
        if args.max_violations is not None
        else configured_max_violations(root)
    )
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": {
            "files_scanned": len(tracked_scripts(root)),
            "violations": len(violations),
            "max_violations": max_violations,
        },
        "violations": [asdict(v) for v in violations],
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    if len(violations) > max_violations:
        print(
            f"gate-contract: FAIL violations={len(violations)} max={max_violations} output={output.as_posix()}"
        )
        return 1
    print(
        f"gate-contract: OK violations={len(violations)} max={max_violations} output={output.as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

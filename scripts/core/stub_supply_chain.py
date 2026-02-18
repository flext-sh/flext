#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Detect and generate missing import stubs for pyrefly.

This script is intentionally strict:
- Never suppresses errors
- Fails when unresolved missing imports remain
- Generates stubs only under typings/generated/
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MISSING_IMPORT_RE = re.compile(r"Cannot find module `([^`]+)` \[missing-import\]")
INTERNAL_PREFIXES = ("flext_", "client-a_", "client-b_")


@dataclass(frozen=True)
class ProjectResult:
    project: str
    internal_missing_imports: list[str]
    missing_imports: list[str]
    generated: list[str]


def run_cmd(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except FileNotFoundError as exc:
        msg = f"Command not found: {command[0]}"
        raise RuntimeError(msg) from exc


def discover_projects(root: Path) -> list[Path]:
    projects: list[Path] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "pyproject.toml").exists() and (entry / "src").is_dir():
            projects.append(entry)
    return projects


def existing_stub(module: str, root: Path) -> bool:
    rel = module.replace(".", "/")
    manual = root / "typings" / rel
    generated = root / "typings" / "generated" / rel
    candidates = [
        manual.with_suffix(".pyi"),
        generated.with_suffix(".pyi"),
        manual / "__init__.pyi",
        generated / "__init__.pyi",
    ]
    return any(p.exists() for p in candidates)


def parse_missing_imports(output: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for match in MISSING_IMPORT_RE.finditer(output):
        mod = match.group(1).strip()
        if mod and mod not in seen:
            seen.add(mod)
            ordered.append(mod)
    return ordered


def is_internal_module(module: str, project_name: str) -> bool:
    root = module.split(".", 1)[0]
    project_root = project_name.replace("-", "_")
    if root.startswith(INTERNAL_PREFIXES):
        return True
    return root == project_root


def stub_text(module: str) -> str:
    return (
        f'"""Auto-generated pyrefly stub for {module}."""\n\n'
        "from typing import Any\n\n"
        "def __getattr__(name: str) -> Any: ...\n"
    )


def ensure_parent_packages(path: Path, root: Path) -> None:
    current = path.parent
    generated_root = root / "typings" / "generated"
    while current != generated_root and current.is_relative_to(generated_root):
        init_file = current / "__init__.pyi"
        if not init_file.exists():
            _ = init_file.write_text(stub_text(current.name), encoding="utf-8")
        current = current.parent


def generate_stub(module: str, root: Path) -> list[str]:
    generated_files: list[str] = []
    generated_root = root / "typings" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    parts = module.split(".")
    if len(parts) == 1:
        stub_path = generated_root / parts[0] / "__init__.pyi"
    else:
        pkg_dir = generated_root.joinpath(*parts[:-1])
        pkg_dir.mkdir(parents=True, exist_ok=True)
        ensure_parent_packages(pkg_dir / "_placeholder.pyi", root)
        stub_path = pkg_dir / f"{parts[-1]}.pyi"

    stub_path.parent.mkdir(parents=True, exist_ok=True)
    if not stub_path.exists():
        _ = stub_path.write_text(stub_text(module), encoding="utf-8")
        generated_files.append(str(stub_path.relative_to(root)))

    if len(parts) == 1:
        ensure_parent_packages(stub_path, root)

    return generated_files


def project_missing_imports(project_dir: Path) -> list[str]:
    result = run_cmd(
        ["poetry", "run", "pyrefly", "check", "src", "--config", "pyproject.toml"],
        cwd=project_dir,
    )
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    return parse_missing_imports(output)


def process_project(project_dir: Path, root: Path, apply: bool) -> ProjectResult:
    missing = project_missing_imports(project_dir)
    internal_missing = [m for m in missing if is_internal_module(m, project_dir.name)]
    third_party_missing = [
        m for m in missing if not is_internal_module(m, project_dir.name)
    ]
    unresolved = [m for m in third_party_missing if not existing_stub(m, root)]
    generated: list[str] = []

    if apply:
        for module in unresolved:
            generated.extend(generate_stub(module, root))
        unresolved = [m for m in unresolved if not existing_stub(m, root)]

    return ProjectResult(
        project=project_dir.name,
        internal_missing_imports=internal_missing,
        missing_imports=unresolved,
        generated=generated,
    )


def write_report(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Typing stub supply-chain gate")
    _ = parser.add_argument("--all", action="store_true", help="Process all projects")
    _ = parser.add_argument(
        "--project", action="append", default=[], help="Project name"
    )
    _ = parser.add_argument(
        "--apply", action="store_true", help="Generate stubs under typings/generated"
    )
    _ = parser.add_argument(
        "--report",
        default=".reports/validate/stub-supply-chain.json",
        help="JSON report path",
    )
    args = parser.parse_args()

    root = Path.cwd()
    projects = discover_projects(root)
    if args.project:
        wanted = set(args.project)
        projects = [p for p in projects if p.name in wanted]

    if not projects:
        print("ERROR: no projects found to process", file=sys.stderr)
        return 2

    results: list[ProjectResult] = []
    for project in projects:
        results.append(process_project(project, root, args.apply))

    internal_total = sum(len(r.internal_missing_imports) for r in results)
    unresolved_total = sum(len(r.missing_imports) for r in results)
    generated_total = sum(len(r.generated) for r in results)
    report = {
        "projects": [
            {
                "project": r.project,
                "internal_missing_imports": r.internal_missing_imports,
                "missing_imports": r.missing_imports,
                "generated": r.generated,
            }
            for r in results
        ],
        "summary": {
            "project_count": len(results),
            "internal_missing_imports": internal_total,
            "unresolved_missing_imports": unresolved_total,
            "generated_stub_files": generated_total,
            "apply": bool(args.apply),
        },
    }
    write_report(Path(args.report), report)

    for r in results:
        line = (
            f"{r.project}: internal_missing_imports={len(r.internal_missing_imports)} "
            + f"unresolved_missing_imports={len(r.missing_imports)} generated={len(r.generated)}"
        )
        print(line)

    print(f"Report: {args.report}")
    if internal_total > 0:
        print(
            f"FAIL: internal missing imports detected ({internal_total}) - fix source modules, do not generate internal stubs",
            file=sys.stderr,
        )
        return 1
    if unresolved_total > 0:
        print(
            f"FAIL: unresolved missing imports remain ({unresolved_total})",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

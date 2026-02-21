#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
"""Auto-heal ``[tool.pyrefly]`` in every pyproject.toml before check runs.

Fixes search-path for root vs subproject, removes nonexistent dirs,
replaces unsupported ``ignore = true`` sub-config with project-excludes.

Usage::

    python scripts/check/fix_pyrefly_config.py [--dry-run] [--verbose]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.libs.config import DEFAULT_ENCODING
from scripts.libs.discovery import find_all_pyproject_files
from scripts.libs.paths import workspace_root_from_file

ROOT = workspace_root_from_file(__file__)
REQUIRED_EXCLUDES = ['"**/*_pb2*.py"', '"**/*_pb2_grpc*.py"']


def _resolve_project_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def find_pyproject_files(project_paths: list[Path] | None = None) -> list[Path]:
    """Return list of pyproject.toml paths under ROOT, optionally filtered by project_paths."""
    return find_all_pyproject_files(ROOT, project_paths=project_paths)


def _fix_search_paths(text: str, project_dir: Path) -> tuple[str, list[str]]:
    fixes: list[str] = []

    if project_dir == ROOT:
        if '"../typings/generated"' in text:
            text = text.replace('"../typings/generated"', '"typings/generated"')
            fixes.append("search-path ../typings/generated -> typings/generated")
        if '"../typings"' in text:
            text = text.replace('"../typings"', '"typings"')
            fixes.append("search-path ../typings -> typings")

    sp_match = re.search(r"(search-path\s*=\s*\[)(.*?)(\])", text, flags=re.DOTALL)
    if sp_match:
        original_entries = sp_match.group(2)
        entries = re.findall(r'"([^"]+)"', original_entries)
        nonexistent = [e for e in entries if not (project_dir / e).exists()]
        if nonexistent:
            new_entries = original_entries
            for entry in nonexistent:
                new_entries = re.sub(
                    rf'[ \t]*"{re.escape(entry)}"\s*,?\s*\n', "", new_entries
                )
            if new_entries != original_entries:
                text = text[: sp_match.start(2)] + new_entries + text[sp_match.end(2) :]
                fixes.append(
                    f"removed nonexistent search-path: {', '.join(nonexistent)}"
                )

    return text, fixes


def _remove_ignore_sub_config(text: str) -> tuple[str, list[str]]:
    fixes: list[str] = []
    pattern = re.compile(
        r'\s*\[\[tool\.pyrefly\.sub-config\]\]\s*\n\s*matches\s*=\s*"([^"]+)"\s*\n\s*ignore\s*=\s*true\s*\n?',
        flags=re.MULTILINE,
    )
    match = pattern.search(text)
    if match:
        text = text[: match.start()] + text[match.end() :]
        text = re.sub(r"\n{3,}", "\n\n", text)
        fixes.append(f"removed ignore=true sub-config for '{match.group(1)}'")
    return text, fixes


def _ensure_project_excludes(text: str) -> tuple[str, list[str]]:
    fixes: list[str] = []
    pe_match = re.search(r"(project-excludes\s*=\s*\[)(.*?)(\])", text, flags=re.DOTALL)
    if pe_match:
        existing = pe_match.group(2)
        to_add = [g for g in REQUIRED_EXCLUDES if g not in existing]
        if to_add:
            new_content = existing.rstrip()
            sep = ", " if new_content.strip() else ""
            new_content += sep + ", ".join(to_add) + " "
            text = text[: pe_match.start(2)] + new_content + text[pe_match.end(2) :]
            fixes.append(f"added {', '.join(to_add)} to project-excludes")
    else:
        sp_end = re.search(
            r"([ \t]*)search-path\s*=\s*\[.*?\]\s*\n", text, flags=re.DOTALL
        )
        if sp_end:
            indent = sp_end.group(1)
            line = f"{indent}project-excludes = [{', '.join(REQUIRED_EXCLUDES)}]\n"
            text = text[: sp_end.end()] + line + text[sp_end.end() :]
            fixes.append("added project-excludes for pb2 files")
    return text, fixes


def process_file(path: Path, *, dry_run: bool = False) -> list[str]:
    """Apply pyrefly config repairs to a single pyproject file."""
    text = path.read_text(encoding=DEFAULT_ENCODING)
    if "[tool.pyrefly]" not in text:
        return []

    original = text
    all_fixes: list[str] = []

    text, fixes = _fix_search_paths(text, path.parent)
    all_fixes.extend(fixes)

    text, fixes = _remove_ignore_sub_config(text)
    all_fixes.extend(fixes)

    if any("removed ignore" in f for f in all_fixes) or path.parent == ROOT:
        text, fixes = _ensure_project_excludes(text)
        all_fixes.extend(fixes)

    if text != original and not dry_run:
        _ = path.write_text(text, encoding=DEFAULT_ENCODING)

    return all_fixes


def main() -> int:
    """Run pyrefly config fixes across discovered projects."""
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("projects", nargs="*")
    _ = parser.add_argument("--dry-run", action="store_true")
    _ = parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    dry_run = args.dry_run
    verbose = args.verbose
    project_paths = [_resolve_project_path(project) for project in args.projects]

    total_fixes = 0
    for path in find_pyproject_files(project_paths or None):
        fixes = process_file(path, dry_run=dry_run)
        if fixes:
            total_fixes += len(fixes)
            if verbose:
                try:
                    rel = path.relative_to(ROOT)
                except ValueError:
                    rel = path
                for fix in fixes:
                    print(f"  {'(dry)' if dry_run else '✓'} {rel}: {fix}")

    if verbose and total_fixes == 0:
        print("  All pyrefly configs clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

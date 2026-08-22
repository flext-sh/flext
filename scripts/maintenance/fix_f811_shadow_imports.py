"""Root-cause codemod for Ruff F811 facade re-import shadowing (recorded).

Ruff is the authoritative F811 detector; this script consumes its JSON and
removes ONLY the earlier, shadowed import binding that Ruff reports as the
``redefined-while-unused`` original. It never edits the winning (last) import.

Two structural shapes are handled, both proven against the FLEXT test facades
where ``from tests import c`` (the package-specific test facade) shadows an
earlier ``from <flext_pkg> import c``:

  * whole-line removal   -- the earlier import binds ONLY the shadowed name
                            (``from flext_core import c``) -> drop the line.
  * name-from-list edit  -- the earlier import binds several names
                            (``from flext_core import FlextContainer, c``)
                            -> drop only the shadowed name, keep the rest.

Safety contract (fails loud, never guesses):
  * only touches a binding when Ruff itself flags F811 for that exact name/line;
  * verifies the reported original line still contains the name before editing;
  * refuses any site whose earlier statement is not a simple
    ``from X import ...`` (star, aliased shadow name) -> manual review;
  * DRY-RUN by default: prints the unified plan; ``--apply`` mutates.
  * idempotent: a second run finds zero F811 and makes zero edits.

Usage:
    python scripts/maintenance/fix_f811_shadow_imports.py <path> [<path>...]
    python scripts/maintenance/fix_f811_shadow_imports.py <path> --apply
"""

from __future__ import annotations

import argparse
import ast
import json
import operator
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ShadowFix:
    """One resolved F811 shadow-import edit."""

    file: Path
    original_line: int  # 1-based line of the shadowed (earlier) import
    name: str  # the redefined binding to remove


def _ruff_f811(paths: list[str]) -> list[dict[str, object]]:
    """Run Ruff for F811 only and return its JSON diagnostics."""
    proc = subprocess.run(
        [
            ".venv/bin/ruff",
            "check",
            "--preview",
            "--select",
            "F811",
            "--output-format",
            "json",
            *paths,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return _parse_diags(proc.stdout)


def _parse_diags(payload: str) -> list[dict[str, object]]:
    """Parse a Ruff JSON diagnostics payload into dict rows."""
    payload = payload.strip()
    if not payload:
        return []
    parsed: object = json.loads(payload)
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _resolve(diags: list[dict[str, object]]) -> list[ShadowFix]:
    """Map Ruff F811 diagnostics to precise shadowed-binding edits."""
    fixes: list[ShadowFix] = []
    for diag in diags:
        if diag.get("code") != "F811":
            continue
        filename = diag.get("filename")
        message = diag.get("message", "")
        if not isinstance(filename, str) or not isinstance(message, str):
            continue
        # Ruff F811 message: "Redefinition of unused `c` from line 13: `c` ..."
        name_match = re.search(r"`([^`]+)`", message)
        line_match = re.search(r"from line (\d+)", message)
        name = name_match.group(1) if name_match else ""
        original_line = int(line_match.group(1)) if line_match else 0
        if not name or original_line <= 0:
            continue
        fixes.append(ShadowFix(Path(filename), original_line, name))
    return fixes


def _plan_edit(fix: ShadowFix, lines: list[str]) -> tuple[int, str | None] | None:
    """Return (line_index, replacement_or_None) for one fix, or None if unsafe.

    replacement is None -> delete the whole line;
    replacement is str  -> rewrite the line keeping the other imports.
    """
    idx = fix.original_line - 1
    if idx < 0 or idx >= len(lines):
        return None
    source_line = lines[idx]
    try:
        node = ast.parse(source_line.strip()).body[0]
    except SyntaxError:
        return None
    if not isinstance(node, ast.ImportFrom) or node.module is None:
        return None
    aliases = node.names
    if any(alias.name == "*" for alias in aliases):
        return None
    names = [alias.name for alias in aliases if alias.asname is None]
    if fix.name not in names:
        return None  # loud refusal: Ruff line/name disagree with source
    if len(aliases) == 1:
        return (idx, None)  # whole-line delete
    kept = [
        alias
        for alias in aliases
        if not (alias.asname is None and alias.name == fix.name)
    ]
    if not kept:
        return (idx, None)
    rendered = ", ".join(
        a.name if a.asname is None else f"{a.name} as {a.asname}" for a in kept
    )
    indent = source_line[: len(source_line) - len(source_line.lstrip())]
    return (idx, f"{indent}from {node.module} import {rendered}\n")


def main() -> int:
    """Scan for F811 shadow imports and preview or apply the removals."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="files or dirs to scan")
    parser.add_argument(
        "--apply", action="store_true", help="write edits (default dry-run)"
    )
    parser.add_argument(
        "--from-json",
        metavar="FILE",
        help="read Ruff F811 JSON from FILE ('-' for stdin) instead of "
        "spawning Ruff; use this where nested subprocess is unavailable",
    )
    args = parser.parse_args()

    if args.from_json:
        raw = (
            sys.stdin.read()
            if args.from_json == "-"
            else Path(args.from_json).read_text(encoding="utf-8")
        )
        diags = _parse_diags(raw)
    elif args.paths:
        diags = _ruff_f811(args.paths)
    else:
        parser.error("provide paths to scan or --from-json FILE")
    fixes = _resolve(diags)
    if not fixes:
        print("F811: no shadow-import diagnostics; nothing to do.")
        return 0

    by_file: dict[Path, list[ShadowFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file, []).append(fix)

    planned = 0
    refused: list[ShadowFix] = []
    for file, file_fixes in sorted(by_file.items()):
        lines = file.read_text(encoding="utf-8").splitlines(keepends=True)
        edits: list[tuple[int, str | None]] = []
        for fix in file_fixes:
            plan = _plan_edit(fix, lines)
            if plan is None:
                refused.append(fix)
                continue
            edits.append(plan)
        for idx, replacement in sorted(edits, key=operator.itemgetter(0), reverse=True):
            before = lines[idx].rstrip("\n")
            if replacement is None:
                action = f"- {before}"
                if args.apply:
                    del lines[idx]
            else:
                action = f"- {before}\n+ {replacement.rstrip(chr(10))}"
                if args.apply:
                    lines[idx] = replacement
            planned += 1
            print(f"{file}:{idx + 1}\n{action}")
        if args.apply and edits:
            file.write_text("".join(lines), encoding="utf-8")

    print(
        f"\nF811 shadow-import: {planned} edit(s) "
        f"{'applied' if args.apply else 'previewed (dry-run)'}; "
        f"{len(refused)} refused."
    )
    for fix in refused:
        print(f"  REFUSED (manual review): {fix.file}:{fix.original_line} `{fix.name}`")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())

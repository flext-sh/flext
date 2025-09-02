#!/usr/bin/env python3
"""Standardize flext_core imports to short aliases and update usages.

Goals
- Replace usages of:
  - FlextModels -> m
  - FlextTypes -> t
  - FlextConstants -> c
  - FlextFields -> f
  - FlextProtocols -> p
- Ensure an aliased import exists in each edited file:
  from flext_core import FlextModels as m, FlextTypes as t, FlextConstants as c, FlextFields as f, FlextProtocols as p
  (Only the aliases actually used in the file are included.)

Safety
- Dry-run by default: prints a concise plan without writing.
- Skips replacements in import statements themselves.
- Does not touch strings or comments (token-level replacement).

Usage
  python scripts/alias_flext_imports.py [--apply] [--path .] [--project SUBSTR]

Notes
-----
- This script targets direct symbol usages. If a file already uses custom aliases,
  the script will not override them.

"""

from __future__ import annotations

import argparse
import ast
import io
import re
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import sys

# Ensure local src/ is on sys.path for flext_tools imports when running from repo root
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from flext_core import FlextLogger

from flext_tools.backup import BackupManager
from flext_tools.paths import should_ignore_path
from flext_tools.quality_gateway import (
    QualityGateway,
    QualityCheckConfig,
    all_quality_checks_passed,
    get_quality_failure_summary,
    get_quality_issues,
)
from flext_tools.rollback import RollbackManager, ConfirmationMode

NAME_MAP: dict[str, str] = {
    "FlextModels": "m",
    "FlextTypes": "t",
    "FlextConstants": "c",
    "FlextFields": "f",
    "FlextProtocols": "p",
}

ALIAS_ORDER = [
    "FlextModels",
    "FlextTypes",
    "FlextConstants",
    "FlextFields",
    "FlextProtocols",
]


@dataclass
class FilePlan:
    path: Path
    replaced: dict[str, int]
    removed_import_lines: int
    added_import: bool


def collect_import_ranges(tree: ast.AST) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lineno = getattr(node, "lineno", None)
            end_lineno = getattr(node, "end_lineno", None)
            if lineno is not None:
                if end_lineno is None:
                    end_lineno = lineno
                ranges.append((lineno, end_lineno))
    return ranges


def line_in_ranges(lineno: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= lineno <= end for start, end in ranges)


def tokenize_replace_names(
    code: str, import_ranges: list[tuple[int, int]]
) -> tuple[str, dict[str, int]]:
    """Token-level safe replacement of target names with aliases."""
    replaced_counts: dict[str, int] = dict.fromkeys(NAME_MAP, 0)
    toks_in = list(tokenize.generate_tokens(io.StringIO(code).readline))
    toks_out: list[tokenize.TokenInfo] = []

    for tok in toks_in:
        if tok.type == tokenize.NAME and tok.string in NAME_MAP:
            if not line_in_ranges(tok.start[0], import_ranges):
                orig = tok.string
                alias = NAME_MAP[orig]
                replaced_counts[orig] += 1
                tok = tokenize.TokenInfo(tok.type, alias, tok.start, tok.end, tok.line)
        toks_out.append(tok)

    new_code = tokenize.untokenize(toks_out)
    return new_code, replaced_counts


FLEXT_IMPORT_RE = re.compile(r"^\s*from\s+flext_core(?:\.[\w_]+)?\s+import\s+(.+)$")


def rebuild_imports(code: str, used_aliases: set[str]) -> tuple[str, int, bool]:
    """Remove existing flext_core symbol imports for target names and add aliased import.

    Returns: (new_code, removed_lines_count, added_import_bool)
    """
    lines = code.splitlines()
    kept: list[str] = []
    removed = 0

    # Remove lines that import any of our target symbols from flext_core or submodules
    for line in lines:
        m = FLEXT_IMPORT_RE.match(line)
        if not m:
            kept.append(line)
            continue
        imported = m.group(1)
        # If any target symbol is present, drop this line
        if any(sym in imported for sym in NAME_MAP):
            removed += 1
            continue
        kept.append(line)

    if not used_aliases:
        return "\n".join(kept) + ("\n" if code.endswith("\n") else ""), removed, False

    # Build consolidated aliased import line with only used aliases and in fixed order
    specs: list[str] = []
    for sym in ALIAS_ORDER:
        alias = NAME_MAP[sym]
        if alias in used_aliases:
            specs.append(f"{sym} as {alias}")
    import_line = f"from flext_core import {', '.join(specs)}"

    # Find insertion point: after module docstring and future imports
    idx = 0
    if kept and kept[0].lstrip().startswith("#!/"):
        idx = 1
    # Skip module docstring
    if idx < len(kept) and kept[idx].lstrip().startswith('"""'):
        # Advance until closing triple quotes
        i = idx
        triple = '"""'
        if kept[idx].count(triple) >= 2:
            idx = i + 1
        else:
            i += 1
            while i < len(kept):
                if triple in kept[i]:
                    idx = i + 1
                    break
                i += 1
    # Skip future imports
    while idx < len(kept) and kept[idx].startswith("from __future__ import"):
        idx += 1

    kept.insert(idx, import_line)
    return "\n".join(kept) + ("\n" if code.endswith("\n") else ""), removed, True


def detect_used_aliases(code: str) -> set[str]:
    used = set()
    # look for alias followed by dot (to avoid variable collisions)
    for alias in NAME_MAP.values():
        if re.search(rf"\b{re.escape(alias)}\s*\.", code):
            used.add(alias)
    return used


logger = FlextLogger(__name__)


def process_file(
    path: Path, *, apply: bool, backup: BackupManager | None
) -> FilePlan | None:
    try:
        code = path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        tree = ast.parse(code)
    except Exception:
        return None

    import_ranges = collect_import_ranges(tree)
    new_code, replaced_counts = tokenize_replace_names(code, import_ranges)

    used_aliases = detect_used_aliases(new_code)
    rebuilt_code, removed_count, added_import = rebuild_imports(new_code, used_aliases)

    if rebuilt_code != code:
        if apply:
            if backup is not None:
                try:
                    backup.backup_file(path, operation_type="modify")
                except Exception:
                    logger.warning("Backup failed", file=str(path))
            path.write_text(rebuilt_code, encoding="utf-8")
        return FilePlan(
            path=path,
            replaced=replaced_counts,
            removed_import_lines=removed_count,
            added_import=added_import,
        )
    return None


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    ap.add_argument("--path", default=".", help="Root path to process (default: .)")
    ap.add_argument(
        "--project",
        default=None,
        help="Only process projects whose path contains this substring",
    )
    ap.add_argument(
        "--backup", action="store_true", help="Backup files before applying changes"
    )
    ap.add_argument(
        "--quality-guard",
        action="store_true",
        help="Run ruff+mypy before/after and rollback if quality degrades",
    )
    ap.add_argument(
        "--relaxed",
        action="store_true",
        help="Relaxed guard: if tools are missing, skip failing instead of blocking",
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    root = Path(args.path).resolve()
    plans: list[FilePlan] = []
    candidates: list[Path] = []

    # First pass: compute plans (dry), do not write
    for py in root.rglob("*.py"):
        if should_ignore_path(py):
            continue
        if args.project and args.project.lower() not in str(py).lower():
            continue
        plan = process_file(py, apply=False, backup=None)
        if plan is not None:
            plans.append(plan)
            candidates.append(py)

    if not plans:
        print("No changes detected")
        return 0

    total_replacements = sum(sum(p.replaced.values()) for p in plans)
    print(
        f"Planned changes ({'APPLIED' if args.apply else 'DRY-RUN'}): {len(plans)} files, replacements={total_replacements}"
    )
    for p in plans:
        changed = sum(p.replaced.values())
        if changed or p.removed_import_lines or p.added_import:
            print(
                f"- {p.path}: replacements={changed}, removed_imports={p.removed_import_lines}, added_import={p.added_import}"
            )

    if not args.apply:
        return 0

    # Optional quality baseline
    before_ok = True
    before_issues = 0
    gw: QualityGateway | None = None
    cfg: QualityCheckConfig | None = None
    if args.quality_guard:
        print("\n🔒 Quality guard baseline (ruff+mypy)...")
        gw = QualityGateway(workspace_path=root)
        cfg = QualityCheckConfig(
            enable_lint=True,
            enable_types=True,
            enable_tests=False,
            enable_coverage=False,
            enable_security=False,
            relaxed=args.relaxed,
        )
        res_before = gw.run_quality_checks_safe(cfg)
        if not res_before.success:
            print(f"❌ Baseline check failed: {res_before.error}")
            return 2
        data_b = res_before.value
        before_ok = all_quality_checks_passed(data_b)
        before_issues = len(get_quality_issues(data_b))
        print(
            f"Baseline: passed={before_ok}, issues={before_issues}; {get_quality_failure_summary(data_b)}"
        )

    # Apply changes with backup
    backup_mgr = BackupManager() if args.backup else None
    applied = 0
    for py in candidates:
        plan = process_file(py, apply=True, backup=backup_mgr)
        if plan is not None:
            applied += 1

    print(f"\nApplied changes to {applied} files")

    if args.quality_guard:
        assert gw is not None and cfg is not None
        print("🔒 Quality guard after changes...")
        res_after = gw.run_quality_checks_safe(cfg)
        if not res_after.success:
            print(f"❌ Post-change check failed: {res_after.error}")
            if backup_mgr is not None:
                try:
                    rb = RollbackManager(backup_dir=backup_mgr.backup_dir)
                    rb.rollback_session(
                        backup_mgr.session_id,
                        confirmation_mode=ConfirmationMode.AUTO_CONFIRM,
                    )
                    print("Rollback completed")
                except Exception as e:
                    print(f"⚠️ Rollback failed: {e}")
            return 3
        data_a = res_after.value
        after_ok = all_quality_checks_passed(data_a)
        after_issues = len(get_quality_issues(data_a))
        print(
            f"After:    passed={after_ok}, issues={after_issues}; {get_quality_failure_summary(data_a)}"
        )
        degraded = (after_issues > before_issues) or (before_ok and not after_ok)
        if degraded:
            print("❌ Quality degraded. Rolling back changes...")
            if backup_mgr is not None:
                try:
                    rb = RollbackManager(backup_dir=backup_mgr.backup_dir)
                    rb.rollback_session(
                        backup_mgr.session_id,
                        confirmation_mode=ConfirmationMode.AUTO_CONFIRM,
                    )
                    print("Rollback completed")
                except Exception as e:
                    print(f"⚠️ Rollback failed: {e}")
            return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

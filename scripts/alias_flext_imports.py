#!/usr/bin/env python3
"""Standardize flext_core imports to short aliases and update usages."""

from __future__ import annotations

import argparse
import ast
import io
import re
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from flext_core import FlextLogger, FlextTypes

from flext_tools.backup import BackupManager
from flext_tools.paths import should_ignore_path
from flext_tools.quality_gateway import (
    QualityCheckConfig,
    QualityGateway,
    all_quality_checks_passed,
    get_quality_failure_summary,
    get_quality_issues,
)
from flext_tools.rollback import RollbackManager

NAME_MAP: FlextTypes.Core.Headers = {
    "FlextModels": "M",
    "FlextTypes": "T",
    "FlextConstants": "C",
    "FlextFields": "F",
    "FlextProtocols": "P",
    "FlextResult": "R",
    "FlextCommands": "Cmd",
}

ALIAS_ORDER = [
    "FlextModels",
    "FlextTypes",
    "FlextConstants",
    "FlextFields",
    "FlextProtocols",
    "FlextResult",
    "FlextCommands",
]

SYMBOL_BY_ALIAS: FlextTypes.Core.Headers = {
    alias: sym for sym, alias in NAME_MAP.items()
}


@dataclass
class FilePlan:
    """Plan for file modifications during import alias processing."""

    path: Path
    replaced: dict[str, int]
    removed_import_lines: int
    added_import: bool


def collect_import_ranges(tree: ast.AST) -> list[tuple[int, int]]:
    """Collect line ranges for import statements in AST.

    Args:
        tree: AST tree to analyze

    Returns:
        List of (start_line, end_line) tuples for import statements

    """
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
    """Check if a line number is within any of the given ranges.

    Args:
        lineno: Line number to check
        ranges: List of (start, end) line ranges

    Returns:
        True if line is within any range, False otherwise

    """
    return any(start <= lineno <= end for start, end in ranges)


def tokenize_replace_names(
    code: str, import_ranges: list[tuple[int, int]]
) -> tuple[str, dict[str, int]]:
    """Token-level safe replacement of target names with aliases."""
    replaced_counts: dict[str, int] = dict.fromkeys(NAME_MAP, 0)
    toks_in = list(tokenize.generate_tokens(io.StringIO(code).readline))
    toks_out: list[tokenize.TokenInfo] = []

    for tok in toks_in:
        if (
            tok.type == tokenize.NAME
            and tok.string in NAME_MAP
            and not line_in_ranges(tok.start[0], import_ranges)
        ):
            orig = tok.string
            alias = NAME_MAP[orig]
            replaced_counts[orig] += 1
            tok = tokenize.TokenInfo(tok.type, alias, tok.start, tok.end, tok.line)
        toks_out.append(tok)

    new_code = tokenize.untokenize(toks_out)
    return new_code, replaced_counts


FLEXT_IMPORT_RE = re.compile(r"^\s*from\s+flext_core(?:\.[\w_]+)?\s+import\s+(.+)$")


def rebuild_imports(
    code: str, sym_to_apply: FlextTypes.Core.Headers
) -> tuple[str, int, bool]:
    """Rewrite flext_core import lines in place, adding aliases without moving lines.

    Returns: (new_code, removed_import_lines, added_import_bool)
    """
    lines = code.splitlines()
    i = 0
    changed_any = False
    removed = 0
    while i < len(lines):
        line = lines[i]
        # Detect start of a flext_core import block
        if FLEXT_IMPORT_RE.match(line):
            block_start = i
            block_end = i
            # Detect multiline using parentheses
            text = line
            open_paren = line.count("(") - line.count(")")
            while open_paren > 0 and block_end + 1 < len(lines):
                block_end += 1
                text += "\n" + lines[block_end]
                open_paren += lines[block_end].count("(") - lines[block_end].count(")")

            # Apply alias injection within this block
            new_text, applied = rewrite_import_block_preserve(text, sym_to_apply)
            if applied:
                changed_any = True
                # Replace block lines
                new_lines_blk = new_text.splitlines()
                lines[block_start : block_end + 1] = new_lines_blk
                # Adjust index to end of new block
                i = block_start + len(new_lines_blk)
                continue
        i += 1

    return (
        "\n".join(lines) + ("\n" if code.endswith("\n") else ""),
        removed,
        changed_any,
    )


def detect_used_aliases(code: str) -> set[str]:
    """Detect which aliases are actually used in the code.

    Args:
        code: Source code to analyze

    Returns:
        Set of aliases that are actually used

    """
    used = set()
    # look for alias followed by dot (to avoid variable collisions)
    for alias in NAME_MAP.values():
        if re.search(rf"\b{re.escape(alias)}\s*\.", code):
            used.add(alias)
    return used


def scan_existing_import_aliases(
    code_lines: FlextTypes.Core.StringList,
) -> tuple[FlextTypes.Core.Headers, FlextTypes.Core.Headers]:
    """Return mapping symbol->alias already present in import lines to avoid duplicates.

    Also returns alias->symbol via reverse mapping, embedded in the values string as 'alias|symbol'.
    For simplicity, we only track flext_core imports.
    """
    sym_to_alias: FlextTypes.Core.Headers = {}
    alias_to_sym: FlextTypes.Core.Headers = {}
    import_re = re.compile(r"^\s*from\s+flext_core(?:\.[\w_]+)?\s+import\s+(.+)$")
    for line in code_lines:
        m = import_re.match(line)
        if not m:
            continue
        names = m.group(1)
        # Split by comma
        parts = [p.strip() for p in names.split(",")]
        for p in parts:
            if not p:
                continue
            if " as " in p:
                name, alias = [x.strip() for x in p.split(" as ", 1)]
                if name in NAME_MAP:
                    sym_to_alias[name] = alias
                    alias_to_sym[alias] = name
    # ensure no duplicates beyond mapping
    return sym_to_alias, alias_to_sym


def rewrite_import_line_preserve(
    line: str, sym_to_apply: FlextTypes.Core.Headers
) -> tuple[str, FlextTypes.Core.Headers]:
    """Rewrite a single 'from flext_core[.sub] import ...' line, adding aliases for target symbols.

    Returns modified line and dict of symbol->alias actually applied in this line.
    Preserves module path and overall structure.
    """
    applied: FlextTypes.Core.Headers = {}
    m = re.match(r"^(\s*from\s+flext_core(?:\.[\w_]+)?\s+import\s+)(.+?)(\s*)$", line)
    if not m:
        return line, applied
    prefix, names, suffix = m.groups()
    parts = [p.strip() for p in names.split(",")]
    new_parts: FlextTypes.Core.StringList = []
    for p in parts:
        if not p:
            continue
        base = p
        alias_existing = None
        if " as " in p:
            base, alias_existing = [x.strip() for x in p.split(" as ", 1)]
        if base in sym_to_apply and not alias_existing:
            alias = sym_to_apply[base]
            new_parts.append(f"{base} as {alias}")
            applied[base] = alias
        else:
            new_parts.append(p)
    return f"{prefix}{', '.join(new_parts)}{suffix}", applied


def rewrite_import_block_preserve(
    block_text: str, sym_to_apply: FlextTypes.Core.Headers
) -> tuple[str, FlextTypes.Core.Headers]:
    """Rewrite a multi-line import block preserving formatting and positions.

    It rewrites each line using rewrite_import_line_preserve.
    """
    applied_total: FlextTypes.Core.Headers = {}
    out_lines: FlextTypes.Core.StringList = []
    for ln in block_text.splitlines():
        new_ln, applied = rewrite_import_line_preserve(ln, sym_to_apply)
        out_lines.append(new_ln)
        applied_total.update(applied)
    return "\n".join(out_lines), applied_total


logger = FlextLogger(__name__)


def process_file(
    path: Path, *, apply: bool, backup: BackupManager | None, ast_check: bool = False
) -> FilePlan | None:
    """Process a single file for import alias replacement.

    Args:
        path: Path to the file to process
        apply: Whether to actually apply changes
        backup: Backup manager for file operations
        ast_check: Whether to perform AST validation

    Returns:
        FilePlan with modification details, or None if processing failed

    """
    try:
        code = path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        tree = ast.parse(code)
    except Exception:
        return None

    import_ranges = collect_import_ranges(tree)
    # Scan for existing aliases to avoid duplicates and conflicts
    sym_to_alias_existing, alias_to_sym_existing = scan_existing_import_aliases(
        code.splitlines()
    )
    # Ban symbols whose desired alias collides with existing alias on different symbol
    banned_symbols = set()
    for sym, alias in NAME_MAP.items():
        if alias in alias_to_sym_existing and alias_to_sym_existing[alias] != sym:
            banned_symbols.add(sym)
        if sym in sym_to_alias_existing and sym_to_alias_existing[sym] != alias:
            banned_symbols.add(sym)

    # Perform token replacements except for banned symbols
    replaced_counts: dict[str, int] = dict.fromkeys(NAME_MAP, 0)
    toks_in = list(tokenize.generate_tokens(io.StringIO(code).readline))
    toks_out: list[tokenize.TokenInfo] = []
    for tok in toks_in:
        if tok.type == tokenize.NAME and tok.string in NAME_MAP:
            sym = tok.string
            # Nunca substituir dentro de linhas de import
            if (
                not line_in_ranges(tok.start[0], import_ranges)
                and sym not in banned_symbols
            ):
                alias = NAME_MAP[sym]
                tok = tokenize.TokenInfo(tok.type, alias, tok.start, tok.end, tok.line)
                replaced_counts[sym] = replaced_counts.get(sym, 0) + 1
        toks_out.append(tok)
    partially_rewritten = tokenize.untokenize(toks_out)

    # Build sym_to_apply map based on NAME_MAP excluding banned and already aliased
    sym_to_apply: FlextTypes.Core.Headers = {}
    for sym, alias in NAME_MAP.items():
        if sym in banned_symbols:
            continue
        # If already has an alias (any), skip changing it
        if sym_to_alias_existing.get(sym):
            continue
        sym_to_apply[sym] = alias

    rebuilt_code, removed_count, added_import = rebuild_imports(
        partially_rewritten, sym_to_apply
    )

    if ast_check:
        try:
            ast.parse(rebuilt_code)
        except Exception:
            # If AST fails, skip this file change
            return None

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
    """Main entry point for the import alias processing script.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)

    """
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
        plan = process_file(py, apply=False, backup=None, ast_check=True)
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
        plan = process_file(py, apply=True, backup=backup_mgr, ast_check=True)
        if plan is not None:
            applied += 1

    print(f"\nApplied changes to {applied} files")

    if args.quality_guard:
        if gw is None:
            print("❌ Quality gateway not available")
            return 1
        if cfg is None:
            print("❌ Quality configuration not available")
            return 1
        print("🔒 Quality guard after changes...")
        res_after = gw.run_quality_checks_safe(cfg)
        if not res_after.success:
            print(f"❌ Post-change check failed: {res_after.error}")
            if backup_mgr is not None:
                try:
                    rb = RollbackManager(backup_dir=backup_mgr.backup_dir)
                    rb.rollback_session(
                        backup_mgr.session_id,
                        confirmation_mode=RollbackManager.ConfirmationMode.AUTO_CONFIRM,
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
                        confirmation_mode=RollbackManager.ConfirmationMode.AUTO_CONFIRM,
                    )
                    print("Rollback completed")
                except Exception as e:
                    print(f"⚠️ Rollback failed: {e}")
            return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

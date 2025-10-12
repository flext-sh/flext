#!/usr/bin/env python3
"""Propose standardized test filenames across all projects.

Rules:
- Keep `test_` prefix
- Remove unnecessary adjectives: coverage, comprehensive, extended, final, real, simple, etc.
- Remove environment/type markers already indicated by folder: unit, integration, e2e
- Avoid collisions by preserving an extra distinguishing token when needed

By default, runs in dry-run and prints a mapping. Use `--apply` to rename.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from flext_core import FlextCore

ADJ = {
    "extended",
    "comprehensive",
    "final",
    "coverage",
    "percent",
    "simple",
    "deep",
    "real",
    "enhanced",
    "boost",
    "extra",
    "advanced",
    "fixed",
    "complete",
    "completed",
    "basic",
    "e2e",
    "integration",
    "unit",
    "full",
    "functionality",
    "workflow",
    "workflows",
    "real_world",
    "main",
    "true",
}


SKIP_DIRS = {
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    "site-packages",
}


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped based on directory exclusions.

    Args:
        path: The path to check

    Returns:
        True if the path should be skipped, False otherwise

    """
    return any(part in SKIP_DIRS for part in path.parts)


def simplify(base: str) -> FlextCore.Types.StringList:
    """Return filtered tokens for a test basename without extension and 'test_' prefix."""
    tokens = re.split(r"[_\-]+", base)
    filtered = [t for t in tokens if t and t.lower() not in ADJ]
    if not filtered:
        filtered = [tokens[0]] if tokens else ["tests"]
    # collapse consecutive duplicates
    out: FlextCore.Types.StringList = []
    for t in filtered:
        if not out or out[-1] != t:
            out.append(t)
    return out


def propose(dir_path: Path) -> dict[Path, Path]:
    """Propose standardized test file names for a directory.

    Args:
        dir_path: Directory path to analyze for test files

    Returns:
        Dictionary mapping original paths to proposed new paths

    """
    mapping: dict[Path, Path] = {}
    by_target: defaultdict[str, list[Path]] = defaultdict(list)

    for p in dir_path.rglob("test_*.py"):
        if should_skip(p):
            continue
        base = p.stem  # test_xxx
        tail = base[len("test_") :]
        tokens = simplify(tail)
        target = "test_" + "_".join(tokens) + ".py"
        by_target[target].append(p)

    # Resolve collisions by retaining one additional token when available
    for target, paths in by_target.items():
        if len(paths) == 1:
            mapping[paths[0]] = paths[0].with_name(target)
            continue
        # If multiple map to same target, try to disambiguate by preserving one ADJ token from original
        for idx, p in enumerate(paths, 1):
            base = p.stem[len("test_") :]
            toks = re.split(r"[_\-]+", base)
            # find any non-removed token to differentiate
            extra = next(
                (t for t in toks if t and t.lower() not in ADJ and t not in target),
                None,
            )
            if extra is None:
                # fallback to ordinal suffix
                suffix = f"_{idx}"
                candidate = target[:-3] + suffix + ".py"
            else:
                candidate = target[:-3] + f"_{extra}.py"
            mapping[p] = p.with_name(candidate)

    return mapping


def main(argv: Iterable[str] | None = None) -> int:
    """Main entry point for the test standardization script.

    Args:
        argv: Command line arguments, defaults to sys.argv if None

    Returns:
        Exit code (0 for success)

    """
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (otherwise dry-run)",
    )
    ap.add_argument("--project", help="Filter by project name substring", default=None)
    args = ap.parse_args(list(argv) if argv is not None else None)

    roots = [p for p in Path().glob("*") if p.is_dir() and (p / "tests").exists()]
    if args.project:
        roots = [r for r in roots if args.project.lower() in r.name.lower()]

    total = 0
    for project in sorted(roots):
        test_root = project / "tests"
        mapping = propose(test_root)
        if not mapping:
            continue

        print(f"\n== {project.name} ==")
        for src, dst in sorted(mapping.items()):
            if src.name != dst.name:
                print(f"{src.relative_to(project)} -> {dst.relative_to(project)}")
                if args.apply:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    Path(src).rename(dst)
                    total += 1

    print(f"\nChanges {('applied' if args.apply else 'proposed')}: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

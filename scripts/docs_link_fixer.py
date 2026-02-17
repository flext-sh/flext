#!/usr/bin/env python3
"""Documentation link fixer used by Makefile.docs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}


def iter_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def maybe_fix_link(md_file: Path, raw_link: str) -> str | None:
    if raw_link.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return None
    base = raw_link.split("#", maxsplit=1)[0]
    if not base:
        return None
    candidate = (md_file.parent / base).resolve()
    if candidate.exists():
        return None
    if not base.endswith(".md"):
        md_candidate = (md_file.parent / f"{base}.md").resolve()
        if md_candidate.exists():
            suffix = raw_link[len(base) :]
            return f"{base}.md{suffix}"
    return None


def process_file(md_file: Path, apply: bool) -> int:
    content = md_file.read_text(encoding="utf-8", errors="ignore")
    replacement_count = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal replacement_count
        text, link = match.groups()
        fixed = maybe_fix_link(md_file, link)
        if fixed is None:
            return match.group(0)
        replacement_count += 1
        return f"[{text}]({fixed})"

    updated = LINK_RE.sub(replacer, content)
    if apply and replacement_count > 0:
        md_file.write_text(updated, encoding="utf-8")
    return replacement_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix markdown links")
    parser.add_argument("--root", default=".", help="Root folder")
    parser.add_argument("--apply", action="store_true", help="Apply fixes")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    total = 0
    for md_file in iter_markdown_files(root):
        count = process_file(md_file, args.apply)
        if count:
            action = "applied" if args.apply else "would apply"
            print(f"{md_file.relative_to(root)}: {count} fix(es) {action}")
        total += count

    print(f"total_fixes={total} mode={'apply' if args.apply else 'dry-run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

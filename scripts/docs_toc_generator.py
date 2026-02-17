#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-maintenance/SKILL.md
"""Generate or update markdown TOC blocks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
TOC_START = "<!-- TOC START -->"
TOC_END = "<!-- TOC END -->"
HEADING_RE = re.compile(r"^(##|###)\s+(.+?)\s*$", re.MULTILINE)


def iter_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def anchorize(title: str) -> str:
    anchor = title.strip().lower()
    anchor = re.sub(r"[^a-z0-9\s-]", "", anchor)
    anchor = re.sub(r"\s+", "-", anchor)
    anchor = re.sub(r"-+", "-", anchor)
    return anchor


def build_toc(content: str) -> str:
    items: list[str] = []
    for level, title in HEADING_RE.findall(content):
        anchor = anchorize(title)
        if not anchor:
            continue
        indent = "  " if level == "###" else ""
        items.append(f"{indent}- [{title}](#{anchor})")
    if not items:
        return f"{TOC_START}\n- No sections found\n{TOC_END}"
    return f"{TOC_START}\n" + "\n".join(items) + f"\n{TOC_END}"


def update_toc(content: str) -> tuple[str, bool]:
    toc_block = build_toc(content)
    if TOC_START in content and TOC_END in content:
        pattern = re.compile(r"<!-- TOC START -->.*?<!-- TOC END -->", re.DOTALL)
        updated = pattern.sub(toc_block, content, count=1)
        return updated, updated != content

    lines = content.splitlines()
    if lines and lines[0].startswith("# "):
        insert_at = 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        lines.insert(insert_at, "")
        lines.insert(insert_at + 1, toc_block)
        lines.insert(insert_at + 2, "")
        updated = "\n".join(lines) + ("\n" if content.endswith("\n") else "")
        return updated, True

    updated = toc_block + "\n\n" + content
    return updated, True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate markdown TOCs")
    parser.add_argument("--root", default=".", help="Root folder")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changed = 0
    for md_file in iter_markdown_files(root):
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        updated, did_change = update_toc(content)
        if did_change:
            changed += 1
            if args.apply:
                md_file.write_text(updated, encoding="utf-8")
            mode = "updated" if args.apply else "would update"
            print(f"{md_file.relative_to(root)}: TOC {mode}")
    print(f"toc_changes={changed} mode={'apply' if args.apply else 'dry-run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Table of Contents Generator for FLEXT Documentation.

Automatically generates and updates table of contents for markdown files
based on heading structure. Supports GitHub-flavored markdown anchors.
"""

import re
from pathlib import Path
from typing import NamedTuple


class Heading(NamedTuple):
    """Represents a markdown heading."""

    level: int
    text: str
    anchor: str
    line_number: int


class TOCGenerator:
    """Generate and update table of contents in markdown files."""

    def __init__(self, min_headings: int = 3, max_level: int = 3) -> None:
        self.min_headings = min_headings
        self.max_level = max_level

    def extract_headings(self, content: str) -> list[Heading]:
        """Extract all headings from markdown content."""
        headings = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Match ATX-style headings (# Heading)
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()

                # Skip if heading contains HTML or special markers
                if "<" in text or "TOC" in text.upper():
                    continue

                # Generate GitHub-compatible anchor
                anchor = self._generate_anchor(text)

                headings.append(Heading(level, text, anchor, i))

        return headings

    def _generate_anchor(self, heading_text: str) -> str:
        """Generate GitHub-compatible anchor from heading text."""
        # Remove markdown formatting
        anchor = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading_text)
        anchor = re.sub(r"[`*_~]", "", anchor)

        # Convert to lowercase and replace spaces with hyphens
        anchor = anchor.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"\s+", "-", anchor)
        anchor = re.sub(r"-+", "-", anchor)
        return anchor.strip("-")

    def generate_toc(self, headings: list[Heading]) -> str:
        """Generate table of contents from headings."""
        if len(headings) < self.min_headings:
            return ""

        toc_lines = ["## Table of Contents", ""]

        # Find minimum level to use as base
        min_level = min(h.level for h in headings)

        for heading in headings:
            # Skip headings beyond max_level
            if heading.level > self.max_level:
                continue

            # Calculate indentation
            indent_level = heading.level - min_level
            indent = "  " * indent_level

            # Create TOC entry
            toc_entry = f"{indent}- [{heading.text}](#{heading.anchor})"
            toc_lines.append(toc_entry)

        return "\n".join(toc_lines)

    def insert_or_update_toc(self, content: str, toc: str) -> str:
        """Insert or update TOC in content."""
        # Check if TOC already exists
        toc_pattern = r"## Table of Contents\s*\n\n([\s\S]*?)(?=\n##|\Z)"
        toc_match = re.search(toc_pattern, content)

        if toc_match:
            # Replace existing TOC
            return content[: toc_match.start()] + toc + content[toc_match.end() :]
        # Insert TOC after first heading
        first_heading = re.search(r"^#\s+.+$", content, re.MULTILINE)
        if first_heading:
            insert_pos = first_heading.end()
            return content[:insert_pos] + "\n\n" + toc + "\n" + content[insert_pos:]

        return content

    def process_file(self, file_path: Path, dry_run: bool = True) -> bool:
        """Process a single markdown file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Extract headings
        headings = self.extract_headings(content)

        # Generate TOC
        toc = self.generate_toc(headings)

        if not toc:
            print(f"  ⏭  Skipped (not enough headings): {file_path.name}")
            return False

        # Insert or update TOC
        updated_content = self.insert_or_update_toc(content, toc)

        if updated_content == content:
            print(f"  ✓ No changes needed: {file_path.name}")
            return False

        if not dry_run:
            file_path.write_text(updated_content, encoding="utf-8")
            print(f"  ✅ Updated TOC: {file_path.name}")
        else:
            print(f"  🔍 Would update TOC: {file_path.name}")

        return True

    def process_directory(
        self, root_path: Path, pattern: str = "**/*.md", dry_run: bool = True
    ) -> None:
        """Process all markdown files in directory."""
        print(f"🔖 {'DRY RUN - ' if dry_run else ''}Generating TOCs...")
        print(f"Root: {root_path}\n")

        markdown_files = list(root_path.rglob(pattern))
        updated_count = 0

        for file_path in markdown_files:
            if self.process_file(file_path, dry_run):
                updated_count += 1

        print("\n📊 Summary:")
        print(f"  - Files processed: {len(markdown_files)}")
        print(f"  - Files updated: {updated_count}")

        if dry_run:
            print("\n💡 Run with --apply to actually update files")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate table of contents for markdown files"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory (default: current directory)",
    )
    parser.add_argument(
        "--pattern",
        default="**/*.md",
        help="File pattern to match (default: **/*.md)",
    )
    parser.add_argument(
        "--min-headings",
        type=int,
        default=3,
        help="Minimum headings required for TOC (default: 3)",
    )
    parser.add_argument(
        "--max-level",
        type=int,
        default=3,
        help="Maximum heading level to include (default: 3)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )

    args = parser.parse_args()

    generator = TOCGenerator(min_headings=args.min_headings, max_level=args.max_level)
    generator.process_directory(args.root, args.pattern, dry_run=not args.apply)


if __name__ == "__main__":
    main()

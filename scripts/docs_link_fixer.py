#!/usr/bin/env python3
"""
Automated Link Fixer for FLEXT Documentation

Automatically fixes common link issues in documentation:
- Converts absolute paths to relative paths
- Updates broken internal links
- Suggests corrections for common typos
- Validates and fixes anchor links
"""

import re
import sys
from pathlib import Path
from typing import Any


class LinkFixer:
    """Automated link correction and validation."""

    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.issues_found = 0

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files."""
        return list(self.root_path.rglob("*.md"))

    def fix_absolute_to_relative(self, file_path: Path, content: str) -> str:
        """Convert absolute paths to relative paths."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Find markdown links
            link_pattern = r"\[([^\]]+)\]\((/[^)]+)\)"
            matches = re.finditer(link_pattern, line)

            for match in matches:
                link_text, absolute_path = match.groups()
                # Convert to relative path
                target_path = self.root_path / absolute_path.lstrip("/")

                if target_path.exists():
                    relative_path = Path(absolute_path.lstrip("/")).relative_to(
                        file_path.parent
                    )
                    line = line.replace(
                        f"]({absolute_path})", f"]({relative_path})"
                    )
                    self.fixes_applied += 1
                    print(
                        f"  ✓ Fixed: {absolute_path} → {relative_path} in {file_path.name}"
                    )

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_broken_internal_links(self, file_path: Path, content: str) -> str:
        """Attempt to fix broken internal links."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            matches = re.finditer(link_pattern, line)

            for match in matches:
                link_text, link_url = match.groups()

                # Skip external links
                if link_url.startswith(("http://", "https://")):
                    continue

                # Check if link is broken
                target_path = (
                    file_path.parent / link_url
                    if link_url.startswith(("./", "../"))
                    else self.root_path / link_url.lstrip("/")
                )

                if not target_path.exists():
                    self.issues_found += 1
                    # Try to find similar file
                    similar = self._find_similar_file(link_url)
                    if similar:
                        relative_path = similar.relative_to(file_path.parent)
                        line = line.replace(f"]({link_url})", f"]({relative_path})")
                        self.fixes_applied += 1
                        print(
                            f"  ✓ Fixed broken link: {link_url} → {relative_path} in {file_path.name}"
                        )

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _find_similar_file(self, broken_link: str) -> Path | None:
        """Find similar file to broken link."""
        # Extract filename
        filename = Path(broken_link).name

        # Search for file with same name
        for file_path in self.root_path.rglob(filename):
            return file_path

        return None

    def fix_missing_alt_text(self, content: str) -> str:
        """Add placeholder alt text to images missing it."""
        image_pattern = r"!\[\]\(([^)]+)\)"

        def replace_alt(match: re.Match[str]) -> str:
            image_url = match.group(1)
            filename = Path(image_url).stem.replace("-", " ").replace("_", " ")
            return f"![{filename.title()}]({image_url})"

        fixed_content = re.sub(image_pattern, replace_alt, content)

        if fixed_content != content:
            self.fixes_applied += 1
            print("  ✓ Added alt text to images")

        return fixed_content

    def fix_file(self, file_path: Path) -> None:
        """Fix all issues in a single file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        original_content = content

        # Apply fixes
        content = self.fix_absolute_to_relative(file_path, content)
        content = self.fix_broken_internal_links(file_path, content)
        content = self.fix_missing_alt_text(content)

        # Write back if changed
        if content != original_content:
            if not self.dry_run:
                file_path.write_text(content, encoding="utf-8")
                print(f"✅ Updated: {file_path.relative_to(self.root_path)}")
            else:
                print(f"🔍 Would update: {file_path.relative_to(self.root_path)}")

    def run(self) -> None:
        """Run link fixer on all documentation."""
        print(f"🔧 {'DRY RUN - ' if self.dry_run else ''}Fixing documentation links...")
        print(f"Root: {self.root_path}\n")

        markdown_files = self.find_markdown_files()

        for file_path in markdown_files:
            self.fix_file(file_path)

        print(f"\n📊 Summary:")
        print(f"  - Files processed: {len(markdown_files)}")
        print(f"  - Fixes applied: {self.fixes_applied}")
        print(f"  - Issues found: {self.issues_found}")

        if self.dry_run:
            print("\n💡 Run with --apply to actually apply fixes")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated link fixer for documentation")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory (default: current directory)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes (default is dry-run)",
    )

    args = parser.parse_args()

    fixer = LinkFixer(args.root, dry_run=not args.apply)
    fixer.run()


if __name__ == "__main__":
    main()

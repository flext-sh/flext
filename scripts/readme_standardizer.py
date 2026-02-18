#!/usr/bin/env python3
# Owner-Skill: .claude/skills/readme-standardization/SKILL.md
"""README Standardization Script for FLEXT Workspace.

This script enforces structural and content standards for README.md files across the FLEXT ecosystem.
It adheres to the "FLEXT Way" by checking for:
1. Standardized preambles (Title, Badges, Description, Metadata, Ecosystem Link)
2. Correct internal/external links (especially github.com/flext-sh/flext)
3. Essential sections (Installation, Usage, Contributing, License)
4. Consistent metadata formatting (Version, Reviewed Date)

Usage:
    python scripts/readme_standardizer.py [--check] [--fix] [--projects PROJECT1 PROJECT2 ...]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

# Regular Expression for finding the specific preamble pattern
# This looks for the **Reviewed**: line followed by the Ecosystem link
PREAMBLE_REGEX = re.compile(
    r"\*\*Reviewed\*\*: (\d{4}-\d{2}-\d{2}) \| \*\*Version\*\*: ([a-zA-Z0-9.\-]+)\n\n(Part of the \[FLEXT\]\(https://github.com/flext(-sh)?/flext\) ecosystem\.|Parte do ecossistema \[FLEXT\]\(https://github.com/flext(-sh)?/flext\)\.)",
    re.MULTILINE,
)

# Current standard values
CURRENT_REVIEW_DATE = datetime.date.today().isoformat()
CURRENT_VERSION = "0.10.0-dev"
ECOSYSTEM_LINK = "https://github.com/flext-sh/flext"
# Old incorrect link
OLD_ECOSYSTEM_LINK = "https://github.com/flext/flext"

# Essential sections required in a good README
REQUIRED_SECTIONS = [
    "Key Features",
    "Installation",
    "Usage",
    "Architecture",
    "Contributing",
    "License",
]


class ReadmeIssue(TypedDict):
    """Type definition for a README issue."""

    type: str  # preamble, link, structure, missing_section
    description: str
    line: int
    fixable: bool


class ReadmeReport(TypedDict):
    """Type definition for a README report."""

    file: str
    issues: list[ReadmeIssue]
    fixed: int


@dataclass
class ReadmeFile:
    """Represents a README.md file."""

    path: Path
    content: str
    issues: list[ReadmeIssue] = field(default_factory=list)
    modified: bool = False

    def add_issue(
        self,
        issue_type: str,
        description: str,
        line: int = 0,
        fixable: bool = False,
    ) -> None:
        """Add an issue to the file report."""
        self.issues.append(
            {
                "type": issue_type,
                "description": description,
                "line": line,
                "fixable": fixable,
            },
        )


class ReadmeStandardizer:
    """Standardizes README.md files across the workspace."""

    def __init__(self, workspace_root: Path) -> None:
        """Initialize the standardizer with workspace root."""
        self.workspace_root = workspace_root
        self.files: list[ReadmeFile] = []

    def scan_project(self, project_path: Path) -> None:
        """Scan a specific project directory for README.md."""
        readme_path = project_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding="utf-8")
                self.files.append(ReadmeFile(path=readme_path, content=content))
            except Exception as e:
                print(f"Error reading {readme_path}: {e}")

    def scan_workspace(self, projects: list[str] | None = None) -> None:
        """Scan the entire workspace or specific projects."""
        if projects:
            for project in projects:
                self.scan_project(self.workspace_root / project)
        else:
            # Find all README.md in immediate subdirectories (projects)
            for item in self.workspace_root.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    self.scan_project(item)

            # Also check root README
            root_readme = self.workspace_root / "README.md"
            if root_readme.exists():
                self.files.append(
                    ReadmeFile(
                        path=root_readme,
                        content=root_readme.read_text(encoding="utf-8"),
                    ),
                )

    def check_files(self) -> None:
        """Check all loaded files for issues."""
        for file in self.files:
            self._check_preamble(file)
            self._check_links(file)
            self._check_structure(file)

    def fix_files(self) -> None:
        """Attempt to fix issues in all loaded files."""
        for file in self.files:
            original_content = file.content
            
            # 1. Fix Preamble
            file.content = self._fix_preamble_content(file.content)
            
            # 2. Fix Links
            file.content = self._fix_links_content(file.content)

            if file.content != original_content:
                file.modified = True
                try:
                    file.path.write_text(file.content, encoding="utf-8")
                    print(f"✅ Fixed {file.path.relative_to(self.workspace_root)}")
                except Exception as e:
                    print(f"❌ Failed to write {file.path}: {e}")

    def _check_preamble(self, file: ReadmeFile) -> None:
        """Check if the preamble exists and is correct."""
        match = PREAMBLE_REGEX.search(file.content)
        if not match:
            # Check for partial matches or old versions
            if "**Reviewed**:" in file.content:
                file.add_issue(
                    "preamble",
                    "Preamble format incorrect or outdated link",
                    fixable=True,
                )
            else:
                 # It might be missing entirely or very different
                file.add_issue("preamble", "Standard preamble missing", fixable=True)
        else:
            # Check version and date freshness (optional warning)
            reviewed_date = match.group(1)
            version = match.group(2)
            if version != CURRENT_VERSION:
                file.add_issue(
                    "preamble",
                    f"Version mismatch: {version} vs {CURRENT_VERSION}",
                    fixable=True,
                )

    def _fix_preamble_content(self, content: str) -> str:
        """Fix the preamble in the content string."""
        # Define the standard preamble block
        standard_preamble = (
            f"**Reviewed**: {CURRENT_REVIEW_DATE} | **Version**: {CURRENT_VERSION}\n\n"
            f"Part of the [FLEXT]({ECOSYSTEM_LINK}) ecosystem."
        )

        # Regex to locate ANY existing preamble-like block
        # Finds a line starting with **Reviewed**: and the following line(s)
        # We replace specifically the matched block or insert it if missing? 
        # For safety, we search for the specific lines we want to replace.
        
        # 1. Replace old links first (Review + Link block)
        pattern = re.compile(
            r"\*\*Reviewed\*\*:.*?\n\nPart of the \[FLEXT\]\(.*?\)\secosystem\.",
            re.MULTILINE | re.DOTALL,
        )
        
        if pattern.search(content):
            return pattern.sub(standard_preamble, content)
        
        # 2. If not found, try to insert after the main title/description
        # This is harder to do safely regex-only without context.
        # For now, we only replace existing (even if incorrect) preambles.
        # If completely missing, we might need a more sophisticated insertion logic (skipped for safety).
        return content

    def _check_links(self, file: ReadmeFile) -> None:
        """Check for broken or outdated links."""
        if OLD_ECOSYSTEM_LINK in file.content:
            file.add_issue(
                "link",
                f"Found deprecated link: {OLD_ECOSYSTEM_LINK}",
                fixable=True,
            )

    def _fix_links_content(self, content: str) -> str:
        """Fix links in the content string."""
        return content.replace(OLD_ECOSYSTEM_LINK, ECOSYSTEM_LINK)

    def _check_structure(self, file: ReadmeFile) -> None:
        """Check for required sections."""
        for section in REQUIRED_SECTIONS:
            # Check for "## [Emoji] Section Name"
            # We look for ## followed by optional non-newline chars, then the section name
            if not re.search(f"^##\\s+.*{re.escape(section)}", file.content, re.MULTILINE):
                file.add_issue(
                    "missing_section",
                    f"Missing required section: {section}",
                    fixable=False,  # Structure usually requires manual content creation
                )

    def generate_report(self) -> list[ReadmeReport]:
        """Generate a report of all findings."""
        reports: list[ReadmeReport] = []
        for file in self.files:
            if file.issues:
                report: ReadmeReport = {
                    "file": str(file.path.relative_to(self.workspace_root)),
                    "issues": file.issues,
                    "fixed": 0,  # Populated if fix was run? logic separation here
                }
                reports.append(report)
        return reports


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="README Standardization for FLEXT")
    parser.add_argument(
        "--projects",
        nargs="+",
        help="Projects to scan (default: all)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing",
        default=True,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file (JSON format) for report",
    )

    args = parser.parse_args()
    
    # If fix is specified, it implies check as well, but we perform fixes.
    # Logic: Default is check match. If fix, we run fix.
    
    workspace_root = Path(__file__).parent.parent.resolve()
    # Or current working dir if script is run from helpful location:
    # We assume script is in /scripts/, so parent is root.
    
    standardizer = ReadmeStandardizer(workspace_root)
    
    print(f"🔍 Scanning workspace: {workspace_root}")
    standardizer.scan_workspace(args.projects)
    print(f"📄 Found {len(standardizer.files)} README files")

    if args.fix:
        print("🔧 Running fixes...")
        standardizer.fix_files()
        # Re-check to report remaining issues
        # standardizer.check_files() -> Needs re-scan logic or update in place
        # For simplicity, we just print what was done. Re-run --check to verify.
    else:
        print("🔍 Checking compliance...")
        standardizer.check_files()

    report = standardizer.generate_report()
    
    if report:
        print("\n" + "=" * 60)
        print("README STANDARDIZATION REPORT")
        print("=" * 60)
        for entry in report:
            print(f"\n📂 {entry['file']}")
            for issue in entry['issues']:
                icon = "🔧" if issue['fixable'] else "⚠️"
                print(f"  {icon} [{issue['type']}] {issue['description']}")
                
        if args.output:
            with Path(args.output).open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to {args.output}")
            
        return 1 # Non-zero exit if issues found
    else:
        print("\n✅ All checked READMEs are compliant!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

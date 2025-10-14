#!/usr/bin/env python3
"""FLEXT Documentation Style Checker.

Ensures consistent markdown formatting, heading hierarchy, and style guidelines
across all documentation files.
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path

from flext_core import FlextCore


@dataclass
class StyleIssue:
    """Represents a style issue found in documentation."""

    file_path: Path
    line_number: int
    issue_type: str
    severity: str
    message: str
    suggestion: str | None = None
    context: str | None = None


@dataclass
class StyleCheckResults:
    """Results of style checking across files."""

    total_files: int = 0
    total_issues: int = 0
    issues_by_type: dict[str, list[StyleIssue]] = field(
        default_factory=lambda: defaultdict(list)
    )
    issues_by_severity: dict[str, list[StyleIssue]] = field(
        default_factory=lambda: defaultdict(list)
    )
    files_with_issues: set[Path] = field(default_factory=set)


class DocumentationStyleChecker:
    """Comprehensive documentation style checker."""

    def __init__(self, config: dict[str, object] | None = None) -> None:
        self.config = config or self.default_config()
        self.style_rules = self.config.get("style_rules", {})
        self.content_rules = self.config.get("content_rules", {})

    def default_config(self) -> dict[str, object]:
        """Default configuration for style checking."""
        return {
            "style_rules": {
                "max_line_length": 120,
                "heading_hierarchy": True,
                "consistent_lists": True,
                "code_block_lang": True,
                "alt_text_required": True,
                "trailing_spaces": False,
                "multiple_blank_lines": False,
                "first_heading_level": 1,
                "table_alignment": True,
            },
            "content_rules": {
                "required_sections": ["Overview", "Installation", "Usage"],
                "max_todos_per_file": 5,
                "min_headings_per_file": 3,
                "max_consecutive_blank_lines": 2,
            },
        }

    def check_file(self, file_path: Path) -> list[StyleIssue]:
        """Check a single file for style issues."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Check each line
            for line_num, line in enumerate(lines, 1):
                issues.extend(self.check_line(line, line_num, lines, file_path))

            # Check overall file structure
            issues.extend(self.check_file_structure(content, lines, file_path))

        except Exception as e:
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=0,
                    issue_type="file_error",
                    severity="critical",
                    message=f"Could not read file: {e}",
                )
            )

        return issues

    def check_line(
        self,
        line: str,
        line_num: int,
        all_lines: FlextCore.Types.StringList,
        file_path: Path,
    ) -> list[StyleIssue]:
        """Check a single line for style issues."""
        issues = []

        # Check line length
        max_length = self.style_rules.get("max_line_length", 120)
        if len(line) > max_length and not self.is_code_block_line(
            line, all_lines, line_num - 1
        ):
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type="line_length",
                    severity="low",
                    message=f"Line too long ({len(line)} > {max_length} characters)",
                    suggestion="Break line into multiple lines or shorten content",
                    context=line[:80] + "..." if len(line) > 80 else line,
                )
            )

        # Check trailing spaces
        if self.style_rules.get("trailing_spaces", False) and line.rstrip() != line:
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type="trailing_spaces",
                    severity="low",
                    message="Line has trailing whitespace",
                    suggestion="Remove trailing spaces",
                    context=line,
                )
            )

        # Check heading formatting
        if line.strip().startswith("#"):
            issues.extend(self.check_heading(line, line_num, file_path))

        # Check list formatting
        if self.is_list_item(line):
            issues.extend(
                self.check_list_formatting(line, line_num, all_lines, file_path)
            )

        # Check code blocks
        if line.strip().startswith("```"):
            issues.extend(self.check_code_block(line, line_num, all_lines, file_path))

        # Check image alt text
        if "![" in line and self.style_rules.get("alt_text_required", True):
            issues.extend(self.check_image_alt_text(line, line_num, file_path))

        # Check table alignment
        if "|" in line and self.style_rules.get("table_alignment", True):
            issues.extend(
                self.check_table_alignment(line, line_num, all_lines, file_path)
            )

        return issues

    def check_heading(
        self, line: str, line_num: int, file_path: Path
    ) -> list[StyleIssue]:
        """Check heading formatting."""
        issues = []

        # Check heading format
        if not re.match(r"^#{1,6}\s+", line.strip()):
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type="heading_format",
                    severity="medium",
                    message="Heading should have space after # symbols",
                    suggestion="Add space after # symbols",
                    context=line,
                )
            )

        # Check heading content
        heading_text = re.sub(r"^#{1,6}\s+", "", line.strip())
        if not heading_text:
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type="empty_heading",
                    severity="medium",
                    message="Heading is empty",
                    suggestion="Add heading text",
                    context=line,
                )
            )

        return issues

    def check_list_formatting(
        self,
        line: str,
        line_num: int,
        all_lines: FlextCore.Types.StringList,
        file_path: Path,
    ) -> list[StyleIssue]:
        """Check list item formatting."""
        issues = []

        if not self.style_rules.get("consistent_lists", True):
            return issues

        # Check for consistent list markers
        list_match = re.match(r"^(\s*)([-\*\+])\s+", line)
        if list_match:
            marker = list_match.group(2)
            # Check previous list items for consistency
            for prev_line_num in range(max(0, line_num - 6), line_num):
                prev_line = all_lines[prev_line_num]
                if self.is_list_item(prev_line):
                    prev_marker = re.match(r"^(\s*)([-\*\+])\s+", prev_line)
                    if prev_marker and prev_marker.group(2) != marker:
                        issues.append(
                            StyleIssue(
                                file_path=file_path,
                                line_number=line_num,
                                issue_type="inconsistent_lists",
                                severity="low",
                                message=f"List marker '{marker}' inconsistent with previous marker",
                                suggestion="Use consistent list markers (-, *, or +)",
                                context=line,
                            )
                        )
                        break

        return issues

    def check_code_block(
        self,
        line: str,
        line_num: int,
        all_lines: FlextCore.Types.StringList,
        file_path: Path,
    ) -> list[StyleIssue]:
        """Check code block formatting."""
        issues = []

        if not self.style_rules.get("code_block_lang", True):
            return issues

        # Check opening code block
        if line.strip() == "```" and line_num < len(all_lines) - 1:
            next_line = all_lines[line_num]  # Next line has the code
            if next_line.strip() and not next_line.strip().startswith("```"):
                # This is likely a code block without language
                issues.append(
                    StyleIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type="code_block_lang",
                        severity="low",
                        message="Code block missing language specification",
                        suggestion="Add language after ``` (e.g., ```python)",
                        context=line,
                    )
                )

        return issues

    def check_image_alt_text(
        self, line: str, line_num: int, file_path: Path
    ) -> list[StyleIssue]:
        """Check image alt text."""
        issues = []

        # Find image references
        img_match = re.search(r"!\[([^\]]*)\]", line)
        if img_match:
            alt_text = img_match.group(1).strip()
            if not alt_text:
                issues.append(
                    StyleIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type="missing_alt_text",
                        severity="medium",
                        message="Image missing alt text",
                        suggestion="Add descriptive alt text for accessibility",
                        context=line,
                    )
                )

        return issues

    def check_table_alignment(
        self,
        line: str,
        line_num: int,
        all_lines: FlextCore.Types.StringList,
        file_path: Path,
    ) -> list[StyleIssue]:
        """Check table column alignment."""
        issues = []

        # Check if this looks like a table row
        if "|" in line and not line.strip().startswith("|"):
            # Count pipes
            pipe_count = line.count("|")
            if pipe_count > 1:
                # Check if this is a table separator row
                if re.match(r"^\s*\|[\s\-\|:]+\|\s*$", line):
                    return issues  # Skip separator rows

                # Check surrounding lines for table context
                prev_line = all_lines[line_num - 2] if line_num > 1 else ""
                next_line = all_lines[line_num] if line_num < len(all_lines) - 1 else ""

                if "|" in prev_line or "|" in next_line:
                    # This appears to be part of a table
                    prev_pipes = prev_line.count("|") if "|" in prev_line else 0
                    next_pipes = next_line.count("|") if "|" in next_line else 0

                    if pipe_count not in {prev_pipes, next_pipes}:
                        issues.append(
                            StyleIssue(
                                file_path=file_path,
                                line_number=line_num,
                                issue_type="table_alignment",
                                severity="low",
                                message=f"Table column count mismatch (expected {max(prev_pipes, next_pipes)}, got {pipe_count})",
                                suggestion="Ensure all table rows have the same number of columns",
                                context=line,
                            )
                        )

        return issues

    def check_file_structure(
        self, content: str, lines: FlextCore.Types.StringList, file_path: Path
    ) -> list[StyleIssue]:
        """Check overall file structure."""
        issues = []

        # Check for multiple consecutive blank lines
        max_blank = self.content_rules.get("max_consecutive_blank_lines", 2)
        blank_count = 0
        for line_num, line in enumerate(lines, 1):
            if line.strip() == "":
                blank_count += 1
            else:
                if blank_count > max_blank:
                    issues.append(
                        StyleIssue(
                            file_path=file_path,
                            line_number=line_num - blank_count,
                            issue_type="multiple_blank_lines",
                            severity="low",
                            message=f"Too many consecutive blank lines ({blank_count} > {max_blank})",
                            suggestion="Reduce to maximum 2 consecutive blank lines",
                            context=f"Lines {line_num - blank_count} to {line_num - 1}",
                        )
                    )
                blank_count = 0

        # Check heading count
        headings = [line for line in lines if line.strip().startswith("#")]
        min_headings = self.content_rules.get("min_headings_per_file", 3)
        if (
            len(headings) < min_headings and len(lines) > 50
        ):  # Only check for substantial files
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="insufficient_headings",
                    severity="medium",
                    message=f"File has insufficient headings ({len(headings)} < {min_headings})",
                    suggestion="Add more section headings to improve document structure",
                )
            )

        # Check for required sections
        required_sections = self.content_rules.get("required_sections", [])
        found_sections = set()
        for heading in headings:
            heading_text = re.sub(r"^#{1,6}\s+", "", heading.strip()).lower()
            for required in required_sections:
                if required.lower() in heading_text:
                    found_sections.add(required)

        missing_sections = set(required_sections) - found_sections
        if missing_sections and len(lines) > 100:  # Only check substantial files
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="missing_sections",
                    severity="medium",
                    message=f"Missing required sections: {', '.join(missing_sections)}",
                    suggestion="Add the missing sections to complete the documentation",
                )
            )

        # Check TODO/FIXME count
        todos = len(re.findall(r"\b(TODO|FIXME)\b", content, re.IGNORECASE))
        max_todos = self.content_rules.get("max_todos_per_file", 5)
        if todos > max_todos:
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="excessive_todos",
                    severity="medium",
                    message=f"Too many TODO/FIXME items ({todos} > {max_todos})",
                    suggestion="Resolve or prioritize TODO items",
                )
            )

        # Check heading hierarchy
        if self.style_rules.get("heading_hierarchy", True):
            issues.extend(self.check_heading_hierarchy(lines, file_path))

        return issues

    def check_heading_hierarchy(
        self, lines: FlextCore.Types.StringList, file_path: Path
    ) -> list[StyleIssue]:
        """Check heading hierarchy and proper structure."""
        issues = []
        heading_levels = []
        first_heading_level = self.style_rules.get("first_heading_level", 1)

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                level = len(re.match(r"^#+", line).group())
                heading_levels.append((level, line_num, line.strip()))

        # Check first heading level
        if heading_levels and heading_levels[0][0] != first_heading_level:
            issues.append(
                StyleIssue(
                    file_path=file_path,
                    line_number=heading_levels[0][1],
                    issue_type="heading_hierarchy",
                    severity="medium",
                    message=f"First heading should be level {first_heading_level}, found level {heading_levels[0][0]}",
                    suggestion=f"Change to {'#' * first_heading_level} for proper document structure",
                    context=heading_levels[0][2],
                )
            )

        # Check for skipped levels
        for i in range(1, len(heading_levels)):
            current_level = heading_levels[i][0]
            prev_level = heading_levels[i - 1][0]

            if current_level > prev_level + 1:
                issues.append(
                    StyleIssue(
                        file_path=file_path,
                        line_number=heading_levels[i][1],
                        issue_type="heading_hierarchy",
                        severity="medium",
                        message=f"Heading level skips from {prev_level} to {current_level}",
                        suggestion="Use consecutive heading levels or adjust structure",
                        context=heading_levels[i][2],
                    )
                )

        return issues

    def is_list_item(self, line: str) -> bool:
        """Check if a line is a list item."""
        return bool(re.match(r"^\s*[-\*\+]\s+", line))

    def is_code_block_line(
        self, line: str, all_lines: FlextCore.Types.StringList, line_index: int
    ) -> bool:
        """Check if a line is inside a code block."""
        in_code_block = False

        for i in range(min(line_index + 1, len(all_lines))):
            current_line = all_lines[i]
            if current_line.strip().startswith("```"):
                in_code_block = not in_code_block

        return in_code_block

    def check_files(self, file_paths: list[Path]) -> StyleCheckResults:
        """Check multiple files for style issues."""
        results = StyleCheckResults()

        for file_path in file_paths:
            issues = self.check_file(file_path)
            results.total_files += 1
            results.total_issues += len(issues)

            if issues:
                results.files_with_issues.add(file_path)

            for issue in issues:
                results.issues_by_type[issue.issue_type].append(issue)
                results.issues_by_severity[issue.severity].append(issue)

        return results

    def generate_report(self, results: StyleCheckResults) -> str:
        """Generate comprehensive style check report."""
        from datetime import datetime

        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# FLEXT Documentation Style Check Report

**Generated:** {timestamp}
**Files Checked:** {results.total_files}
**Total Issues:** {results.total_issues}

## 📊 Summary

| Metric | Value | Status |
|--------|-------|---------|
| Files Checked | {results.total_files} | ✅ |
| Files with Issues | {len(results.files_with_issues)} | {"⚠️" if results.files_with_issues else "✅"} |
| Total Issues | {results.total_issues} | {"⚠️" if results.total_issues > 0 else "✅"} |
| Critical Issues | {len(results.issues_by_severity.get("critical", []))} | {"❌" if results.issues_by_severity.get("critical") else "✅"} |
| High Priority | {len(results.issues_by_severity.get("high", []))} | {"⚠️" if results.issues_by_severity.get("high") else "✅"} |

## 🔍 Issues by Type

"""

        for issue_type, issues in results.issues_by_type.items():
            if issues:
                severity = issues[0].severity
                status_icon = {
                    "critical": "❌",
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(severity, "⚪")
                report += f"### {status_icon} {issue_type.replace('_', ' ').title()} ({len(issues)})\n\n"

                # Group by file for readability
                issues_by_file = defaultdict(list)
                for issue in issues:
                    issues_by_file[issue.file_path].append(issue)

                for file_path, file_issues in issues_by_file.items():
                    report += f"#### {file_path.name}\n\n"
                    for issue in file_issues[:5]:  # Limit to 5 per file
                        report += f"- **Line {issue.line_number}:** {issue.message}\n"
                        if issue.suggestion:
                            report += f"  - 💡 {issue.suggestion}\n"
                        if issue.context:
                            report += f"  - 📝 `{issue.context[:100]}{'...' if len(issue.context) > 100 else ''}`\n"
                    if len(file_issues) > 5:
                        report += f"- ... and {len(file_issues) - 5} more issues\n"
                    report += "\n"

        # Severity breakdown
        report += """## 📈 Issues by Severity

"""

        severity_order = ["critical", "high", "medium", "low"]
        for severity in severity_order:
            count = len(results.issues_by_severity.get(severity, []))
            if count > 0:
                icon = {
                    "critical": "❌",
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(severity, "⚪")
                report += f"- {icon} **{severity.title()}:** {count} issues\n"

        # Recommendations
        report += """

## 💡 Recommendations

"""

        if results.issues_by_severity.get("critical"):
            report += f"- **🔴 Address {len(results.issues_by_severity['critical'])} critical issues immediately**\n"

        if results.issues_by_severity.get("high"):
            report += f"- **🟡 Fix {len(results.issues_by_severity['high'])} high-priority issues soon**\n"

        if results.total_issues > 0:
            report += (
                f"- **Run automated fixes for {results.total_issues} total issues**\n"
            )
            report += (
                "- **Consider updating style configuration** for team preferences\n"
            )
            report += "- **Set up pre-commit hooks** to prevent style issues\n"

        # Quality score
        if results.total_files > 0:
            quality_score = 1.0 - (
                results.total_issues / (results.total_files * 10)
            )  # Rough heuristic
            quality_score = max(0.0, min(1.0, quality_score))
            report += f"\n## 📊 Style Quality Score: {quality_score:.2%}\n"

        return report


def discover_docs(base_path: Path | None = None) -> list[Path]:
    """Discover all documentation files."""
    if base_path is None:
        base_path = Path()

    docs = []
    for pattern in ["*.md", "*.mdx"]:
        docs.extend(base_path.rglob(pattern))

    return docs


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="FLEXT Documentation Style Checker")
    parser.add_argument(
        "files", nargs="*", help="Specific files to check (default: all docs)"
    )
    parser.add_argument("--config", help="Configuration file")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument(
        "--fix", action="store_true", help="Automatically fix safe issues"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load configuration
    config = {}
    if args.config and Path(args.config).exists():
        with Path(args.config).open(encoding="utf-8") as f:
            config = json.load(f)

    checker = DocumentationStyleChecker(config)

    # Discover files
    if args.files:
        file_paths = [Path(f) for f in args.files if Path(f).exists()]
    else:
        file_paths = discover_docs()

    if not file_paths:
        print("No documentation files found!")
        return

    print(f"📁 Checking {len(file_paths)} documentation files...")

    # Check files
    results = checker.check_files(file_paths)

    # Generate report
    report = checker.generate_report(results)

    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"📄 Report saved to: {args.output}")
    else:
        print(report)

    # Summary
    if results.total_issues > 0:
        print(
            f"⚠️ Found {results.total_issues} style issues across {len(results.files_with_issues)} files"
        )
        critical = len(results.issues_by_severity.get("critical", []))
        if critical > 0:
            print(f"❌ {critical} critical issues require immediate attention")
    else:
        print("✅ All files passed style checks!")


if __name__ == "__main__":
    main()

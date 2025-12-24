#!/usr/bin/env python3
"""Comprehensive Markdown Linting Script for FLEXT Workspace.

This script:
1. Runs markdownlint on all .md files in the workspace
2. Applies automatic fixes where possible
3. Identifies issues that need manual correction
4. Saves results in SARIF format for CI/CD integration
5. Provides detailed reports for manual fixes

Usage:
    python markdown_lint_workspace.py [--fix] [--sarif-output FILE] [--verbose]
"""

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class MarkdownLinter:
    """Comprehensive markdown linting for FLEXT workspace."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root)
        self.config_file = self.workspace_root / ".markdownlint.json"

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in the workspace, excluding common ignore patterns."""
        ignore_patterns = [
            ".git/**",
            "node_modules/**",
            ".venv/**",
            "__pycache__/**",
            "*.egg-info/**",
            "build/**",
            "dist/**",
            ".pytest_cache/**",
            ".mypy_cache/**",
            ".ruff_cache/**",
            ".coverage/**",
            "htmlcov/**",
        ]

        all_md_files = []
        for pattern in ["**/*.md", "**/*.markdown"]:
            all_md_files.extend(
                glob.glob(pattern, root_dir=self.workspace_root, recursive=True)
            )

        # Convert to Path objects and filter
        md_files = []
        for md_file in all_md_files:
            path = self.workspace_root / md_file

            # Check if file should be ignored
            should_ignore = False
            for ignore_pattern in ignore_patterns:
                if path.match(ignore_pattern) or ignore_pattern.rstrip("/").replace(
                    "**/", ""
                ) in str(path):
                    should_ignore = True
                    break

            if not should_ignore and path.exists():
                md_files.append(path)

        return sorted(md_files)

    def run_markdownlint(
        self, files: list[Path], fix: bool = False, verbose: bool = False
    ) -> dict[str, Any]:
        """Run markdownlint on the specified files."""
        cmd = ["npx", "markdownlint-cli"]

        if fix:
            cmd.append("--fix")

        cmd.extend(["--json"])
        cmd.extend([str(f) for f in files])

        if verbose:
            print(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse JSON output
            issues = json.loads(result.stdout) if result.stdout.strip() else []

            return {
                "success": result.returncode == 0,
                "issues": issues,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "issues": [],
                "stderr": "Timeout expired",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "issues": [], "stderr": str(e), "returncode": -1}

    def generate_sarif_report(
        self, issues: list[dict], output_file: str | None = None
    ) -> str:
        """Generate SARIF report from markdownlint issues."""
        sarif_report = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "markdownlint",
                            "version": "0.40.0",
                            "informationUri": "https://github.com/DavidAnson/markdownlint",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Collect unique rules
        rules_seen = set()

        for issue in issues:
            file_path = issue.get("fileName", "")
            line_number = issue.get("lineNumber", 1)
            rule_id = issue.get("ruleNames", ["unknown"])[0]
            message = issue.get(
                "ruleDescription", issue.get("ruleInformation", "Unknown issue")
            )
            rule_info = issue.get("ruleInformation", "")

            # Add rule if not seen before
            if rule_id not in rules_seen:
                rule = {
                    "id": rule_id,
                    "name": rule_id,
                    "shortDescription": {"text": message},
                    "helpUri": rule_info if rule_info.startswith("http") else None,
                }
                sarif_report["runs"][0]["tool"]["driver"]["rules"].append(rule)
                rules_seen.add(rule_id)

            # Add result
            result = {
                "ruleId": rule_id,
                "level": "warning",
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_path},
                            "region": {
                                "startLine": line_number,
                                "startColumn": issue.get("columnNumber", 1),
                            },
                        }
                    }
                ],
            }

            sarif_report["runs"][0]["results"].append(result)

        # Convert to JSON string
        sarif_json = json.dumps(sarif_report, indent=2)

        # Save to file if specified
        if output_file:
            Path(output_file).write_text(sarif_json, encoding="utf-8")
            print(f"SARIF report saved to: {output_file}")

        return sarif_json

    def categorize_issues(self, issues: list[dict]) -> dict[str, list[dict]]:
        """Categorize issues by type and fixability."""
        categories = {
            "auto_fixable": [],  # Issues that can be fixed automatically
            "manual_fix": [],  # Issues requiring manual intervention
            "style_issues": [],  # Style/consistency issues
            "structural": [],  # Structural markdown issues
            "link_issues": [],  # Link and reference issues
            "other": [],  # Other issues
        }

        rule_mappings = {
            # Auto-fixable rules
            "MD009": "auto_fixable",  # Trailing spaces
            "MD010": "auto_fixable",  # Hard tabs
            "MD012": "auto_fixable",  # Multiple consecutive blank lines
            "MD027": "auto_fixable",  # Multiple spaces after blockquote symbol
            "MD028": "auto_fixable",  # Blank line inside blockquote
            "MD030": "auto_fixable",  # Spaces after list markers
            "MD032": "auto_fixable",  # Lists should be surrounded by blank lines
            "MD037": "auto_fixable",  # Spaces inside emphasis markers
            "MD038": "auto_fixable",  # Spaces inside code span elements
            "MD039": "auto_fixable",  # Spaces inside link text
            "MD047": "auto_fixable",  # Files should end with a single newline
            # Style issues
            "MD004": "style_issues",  # Unordered list style
            "MD005": "style_issues",  # Inconsistent indentation for list items
            "MD007": "style_issues",  # Unordered list indentation
            "MD014": "style_issues",  # Dollar signs used before commands without showing output
            "MD018": "style_issues",  # No space after hash on atx style heading
            "MD019": "style_issues",  # Multiple spaces after hash on atx style heading
            "MD020": "style_issues",  # No space inside hash on atx style heading
            "MD021": "style_issues",  # Multiple spaces inside hash on atx style heading
            "MD022": "style_issues",  # Headings should be surrounded by blank lines
            "MD023": "style_issues",  # Headings must start at the beginning of the line
            "MD026": "style_issues",  # Trailing punctuation in heading
            "MD035": "style_issues",  # Horizontal rule style
            "MD036": "style_issues",  # Emphasis used instead of heading
            "MD040": "style_issues",  # Fenced code blocks should have a language specified
            "MD045": "style_issues",  # Images should have alternate text
            "MD046": "style_issues",  # Code block style
            "MD048": "style_issues",  # Code fence style
            "MD049": "style_issues",  # Emphasis style
            "MD050": "style_issues",  # Strong style
            # Structural issues
            "MD001": "structural",  # Heading levels should only increment by one level at a time
            "MD002": "structural",  # First heading should be a top-level heading
            "MD003": "structural",  # Heading style
            "MD006": "structural",  # Consider starting bulleted lists at the beginning of the line
            "MD011": "structural",  # Reversed link syntax
            "MD031": "structural",  # Fenced code blocks should be surrounded by blank lines
            "MD042": "structural",  # No empty links
            # Link and reference issues
            "MD034": "link_issues",  # Bare URL used
            "MD051": "link_issues",  # Link fragments should be valid
            "MD052": "link_issues",  # Reference links and images should use a label that is defined
            "MD053": "link_issues",  # Link and image reference definitions should be needed
            # Content/structure issues requiring manual review
            "MD013": "manual_fix",  # Line length
            "MD024": "manual_fix",  # Multiple headings with the same content
            "MD025": "manual_fix",  # Multiple top-level headings in the same document
            "MD029": "manual_fix",  # Ordered list item prefix
            "MD033": "manual_fix",  # Inline HTML
            "MD041": "manual_fix",  # First line in file should be a top-level heading
            "MD043": "manual_fix",  # Required heading structure
            "MD044": "manual_fix",  # Proper names should have the correct capitalization
            "MD056": "manual_fix",  # Table column count
        }

        for issue in issues:
            rule_id = issue.get("ruleNames", ["unknown"])[0]
            category = rule_mappings.get(rule_id, "other")
            categories[category].append(issue)

        return categories

    def print_report(
        self, issues: list[dict], categories: dict[str, list[dict]]
    ) -> None:
        """Print a comprehensive report of issues found."""
        print("🔍 MARKDOWN LINTING REPORT")
        print("=" * 50)
        print(f"📊 Total issues found: {len(issues)}")
        print()

        for category, category_issues in categories.items():
            if not category_issues:
                continue

            category_names = {
                "auto_fixable": "🔧 Auto-fixable Issues",
                "manual_fix": "✏️  Manual Fix Required",
                "style_issues": "🎨 Style Issues",
                "structural": "🏗️  Structural Issues",
                "link_issues": "🔗 Link Issues",
                "other": "❓ Other Issues",
            }

            print(
                f"{category_names.get(category, category.upper())}: {len(category_issues)}"
            )

            # Group by file
            files = {}
            for issue in category_issues:
                file_path = issue.get("fileName", "unknown")
                if file_path not in files:
                    files[file_path] = []
                files[file_path].append(issue)

            for file_path, file_issues in files.items():
                print(f"  📄 {file_path}: {len(file_issues)} issues")
                for issue in file_issues[:3]:  # Show first 3 issues per file
                    rule_id = issue.get("ruleNames", ["unknown"])[0]
                    line = issue.get("lineNumber", "?")
                    desc = issue.get("ruleDescription", "Unknown issue")
                    print(f"    • {rule_id} (line {line}): {desc}")

                if len(file_issues) > 3:
                    print(f"    ... and {len(file_issues) - 3} more issues")

            print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comprehensive Markdown Linting for FLEXT Workspace.",
    )
    parser.add_argument(
        "--sarif-output",
        type=str,
        default="markdownlint-remaining.sarif",
        help="Save remaining issues to SARIF file",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )

    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    if not workspace_root.exists():
        print(f"Error: Workspace root {workspace_root} does not exist")
        sys.exit(1)

    linter = MarkdownLinter(workspace_root)

    print(f"🔍 Scanning workspace: {workspace_root}")

    # Find all markdown files
    md_files = linter.find_markdown_files()
    print(f"📄 Found {len(md_files)} markdown files")

    if not md_files:
        print("No markdown files found. Exiting.")
        return

    # Process files in smaller batches to avoid timeouts
    batch_size = 10  # Smaller batch size for reliability
    all_remaining_issues = []
    fixed_count = 0

    print(f"🔧 Step 1: Applying automatic fixes in batches of {batch_size}...")

    # Apply fixes in batches
    total_batches = (len(md_files) - 1) // batch_size + 1
    for i in range(0, len(md_files), batch_size):
        batch = md_files[i : i + batch_size]
        batch_num = i // batch_size + 1

        print(f"  📦 Batch {batch_num}/{total_batches} ({len(batch)} files)...")

        try:
            fix_result = linter.run_markdownlint(batch, fix=True, verbose=args.verbose)
            if fix_result["issues"]:
                batch_fixed = len(fix_result["issues"])
                fixed_count += batch_fixed
                print(f"    ✅ Fixed {batch_fixed} issues in this batch")
        except Exception as e:
            print(f"    ⚠️  Error in batch {batch_num}: {e}")

    print(f"✅ Auto-fixed {fixed_count} issues total")

    print("🔍 Step 2: Checking for remaining issues...")

    # Check remaining issues in same batches
    for i in range(0, len(md_files), batch_size):
        batch = md_files[i : i + batch_size]
        batch_num = i // batch_size + 1

        try:
            final_result = linter.run_markdownlint(
                batch, fix=False, verbose=args.verbose
            )

            if final_result["success"] and final_result["issues"]:
                batch_issues = len(final_result["issues"])
                all_remaining_issues.extend(final_result["issues"])
                print(f"  📦 Batch {batch_num}: {batch_issues} remaining issues")
            elif not final_result["success"]:
                print(f"  ⚠️  Batch {batch_num}: failed to check")
        except Exception as e:
            print(f"  ⚠️  Batch {batch_num}: error - {e}")

    remaining_issues = all_remaining_issues
    print(f"📊 Total remaining issues: {len(remaining_issues)}")

    # Quick categorization for summary
    categories = linter.categorize_issues(remaining_issues)

    # Save reports immediately
    print("\n💾 Saving reports...")

    # Save JSON first (always works)
    json_file = "markdownlint-remaining.json"
    try:
        with Path(json_file).open("w", encoding="utf-8") as f:
            json.dump(remaining_issues, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON saved: {json_file}")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")
        return

    # Save SARIF
    try:
        sarif_file = args.sarif_output
        linter.generate_sarif_report(remaining_issues, sarif_file)
        print(f"✅ SARIF saved: {sarif_file}")
    except Exception as e:
        print(f"⚠️  SARIF save failed: {e}")

    # Group issues by file
    if remaining_issues:
        issues_by_file = {}
        for issue in remaining_issues:
            file_path = issue.get("fileName", "unknown")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        print(f"📂 Files needing fixes: {len(issues_by_file)}")
        # Show top 5 files with most issues
        sorted_files = sorted(
            issues_by_file.items(), key=lambda x: len(x[1]), reverse=True
        )
        for file_path, issues in sorted_files[:5]:
            print(f"  • {file_path}: {len(issues)} issues")
        if len(sorted_files) > 5:
            print(f"  ... and {len(sorted_files) - 5} more files")
    else:
        print("🎉 No files need manual fixes!")

    # Summary
    manual_fix = len(categories["manual_fix"])
    style_issues = len(categories["style_issues"])
    structural = len(categories["structural"])
    link_issues = len(categories["link_issues"])

    print("\n🎯 SUMMARY:")
    print(f"✅ Auto-fixed: {fixed_count} issues")
    print(f"📋 Remaining: {len(remaining_issues)} issues")

    if len(remaining_issues) == 0:
        print("🎉 All markdown files are now compliant!")
        return

    print("\n📋 Issues requiring manual attention:")
    if manual_fix > 0:
        print(f"  • Manual fixes: {manual_fix} (structural/content issues)")
    if style_issues > 0:
        print(f"  • Style issues: {style_issues} (formatting/consistency)")
    if structural > 0:
        print(f"  • Structural issues: {structural} (headings, lists, etc.)")
    if link_issues > 0:
        print(f"  • Link issues: {link_issues} (broken references, fragments)")

    print("\n🔧 Next Steps:")
    print("1. Use the SARIF/JSON reports to identify files needing fixes")
    print("2. Fix issues manually ONE BY ONE in the affected files")
    print("3. Re-run this script to verify each fix")
    print("4. Commit the corrected markdown files")
    print("\n💡 Tip: Start with the files that have fewer issues first!")

    # Always save summary, even if no issues remain
    summary_file = "markdown-lint-manual-fixes.md"
    try:
        with Path(summary_file).open("w", encoding="utf-8") as f:
            f.write("# Markdown Lint - Processing Results\n\n")
            f.write(f"- **Auto-fixed:** {fixed_count} issues\n")
            f.write(f"- **Remaining:** {len(remaining_issues)} issues\n")
            f.write(f"- **Total files processed:** {len(md_files)}\n\n")

            if remaining_issues:
                f.write("## Files Requiring Manual Fixes\n\n")
                f.write(
                    "**Process these files one by one, starting with the ones with fewer issues.**\n\n"
                )

                # Group all issues by file
                issues_by_file = {}
                for issue in remaining_issues:
                    file_path = issue.get("fileName", "unknown")
                    if file_path not in issues_by_file:
                        issues_by_file[file_path] = []
                    issues_by_file[file_path].append(issue)

                # Sort files by number of issues (easiest first)
                sorted_files = sorted(issues_by_file.items(), key=lambda x: len(x[1]))

                for file_path, file_issues in sorted_files:
                    f.write(f"### {file_path} ({len(file_issues)} issues)\n\n")

                    # Group by rule within each file
                    rules_in_file = {}
                    for issue in file_issues:
                        rule_id = issue.get("ruleNames", ["unknown"])[0]
                        if rule_id not in rules_in_file:
                            rules_in_file[rule_id] = []
                        rules_in_file[rule_id].append(issue)

                    for rule_id, issues in rules_in_file.items():
                        rule_desc = issues[0].get("ruleDescription", "Unknown issue")
                        f.write(f"#### {rule_id}: {rule_desc}\n\n")

                        for issue in issues[:15]:  # Show up to 15 issues per rule
                            line = issue.get("lineNumber", "?")
                            error_context = issue.get("errorContext", "").strip()
                            if error_context:
                                f.write(f"- **Line {line}**: `{error_context}`\n")
                            else:
                                error_detail = issue.get("errorDetail", "No details")
                                f.write(f"- **Line {line}**: {error_detail}\n")

                        if len(issues) > 15:
                            f.write(f"- ... and {len(issues) - 15} more occurrences\n")

                        f.write("\n")

                    f.write("---\n\n")

                f.write("## How to Fix Issues\n\n")
                f.write("1. Open each file listed above in your editor\n")
                f.write("2. Go to the line numbers shown\n")
                f.write("3. Fix the issues according to the rule descriptions\n")
                f.write("4. Save the file\n")
                f.write("5. Run this script again to verify the fix\n")
                f.write("6. Move to the next file\n\n")

                f.write("## Common Fix Patterns\n\n")
                f.write("### MD035 - Horizontal rule style\n")
                f.write("**Problem:** Using underscores instead of dashes\n")
                f.write(
                    "**Fix:** Replace `______________________________________________________________________` with `---`\n\n"
                )

                f.write("### MD060 - Table column style\n")
                f.write("**Problem:** Table columns not properly aligned\n")
                f.write("**Fix:** Manually adjust table column alignment\n\n")

                f.write("### MD051 - Link fragments\n")
                f.write("**Problem:** Broken link fragments (e.g., `#invalid-link`)\n")
                f.write("**Fix:** Remove invalid links or fix fragment names\n\n")

                f.write("### MD025 - Multiple top-level headings\n")
                f.write("**Problem:** Multiple H1 headings in same file\n")
                f.write("**Fix:** Change extra H1 to H2 or remove duplicates\n\n")

            else:
                f.write("## ✅ All Issues Resolved!\n\n")
                f.write(
                    "All markdown files in the workspace are now compliant with the linting rules.\n\n"
                )

        print(f"📄 Processing summary saved to {summary_file}")

        if remaining_issues:
            print(
                f"📄 Process files in order: easiest to hardest ({len(sorted_files)} files total)"
            )
            print("💡 Start with files that have fewer issues!")

    except Exception as e:
        print(f"❌ Error saving summary: {e}")


if __name__ == "__main__":
    main()

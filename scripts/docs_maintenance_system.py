#!/usr/bin/env python3
"""FLEXT Documentation Maintenance System.

Comprehensive documentation maintenance framework with quality assurance,
validation, and automated updates for the FLEXT ecosystem.

Usage:
    python scripts/docs_maintenance_system.py [command] [options]

Commands:
    audit       - Run comprehensive content quality audit
    validate    - Validate links and references
    optimize    - Optimize and enhance content
    sync        - Synchronize with version control
    report      - Generate quality assurance reports
    comprehensive - Run all maintenance operations

Options:
    --config FILE    - Configuration file (default: docs/docs_maintenance_config.json)
    --output DIR     - Output directory for reports (default: docs/reports/)
    --verbose        - Enable verbose output
    --dry-run        - Show what would be changed without making changes
"""

import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from flext_core import FlextCore


@dataclass
class DocFile:
    """Represents a documentation file with metadata."""

    path: Path
    size: int
    mtime: float
    lines: int
    words: int
    headings: FlextCore.Types.StringList
    links: FlextCore.Types.StringList
    images: FlextCore.Types.StringList
    issues: FlextCore.Types.StringList = field(default_factory=list)
    score: float = 0.0


@dataclass
class AuditResult:
    """Results of a documentation audit."""

    total_files: int = 0
    total_words: int = 0
    total_links: int = 0
    total_images: int = 0
    broken_links: int = 0
    missing_images: int = 0
    outdated_files: int = 0
    style_issues: int = 0
    completeness_score: float = 0.0
    files: list[DocFile] = field(default_factory=list)
    issues: dict[str, FlextCore.Types.StringList] = field(default_factory=dict)


class DocumentationMaintenanceSystem:
    """Comprehensive documentation maintenance system."""

    def __init__(self, config_file: str | None = None) -> None:
        self.config_file = config_file or "docs/docs_maintenance_config.json"
        self.config = self.load_config()
        self.output_dir = Path(self.config.get("output_dir", "docs/reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "max_age_days": 30,
            "min_words_per_file": 100,
            "link_timeout": 10,
            "concurrent_requests": 5,
            "style_rules": {
                "max_line_length": 120,
                "heading_hierarchy": True,
                "consistent_lists": True,
                "code_block_lang": True,
                "alt_text_required": True,
            },
            "quality_thresholds": {
                "completeness": 0.8,
                "freshness": 0.7,
                "accessibility": 0.9,
                "consistency": 0.85,
            },
            "output_dir": "docs/reports",
            "ignore_patterns": [
                "**/__pycache__/**",
                "**/.git/**",
                "**/node_modules/**",
                "**/build/**",
                "**/dist/**",
            ],
        }

        if Path(self.config_file).exists():
            with Path(self.config_file).open(encoding="utf-8") as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def discover_docs(self) -> list[Path]:
        """Discover all documentation files in the workspace."""
        docs = []
        for pattern in ["*.md", "*.mdx"]:
            docs.extend(Path().rglob(pattern))

        # Apply ignore patterns
        ignore_patterns = self.config.get("ignore_patterns", [])
        filtered_docs = []

        for doc in docs:
            should_ignore = False
            for pattern in ignore_patterns:
                if doc.match(pattern):
                    should_ignore = True
                    break
            if not should_ignore:
                filtered_docs.append(doc)

        return sorted(filtered_docs)

    def analyze_file(self, file_path: Path) -> DocFile:
        """Analyze a single documentation file."""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding="utf-8")

            lines = content.split("\n")
            words = len(re.findall(r"\b\w+\b", content))

            # Extract headings
            headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)

            # Extract links
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            link_urls = [url for _, url in links]

            # Extract images
            images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)

            # Initial analysis for issues
            issues = []
            score = 1.0

            # Check for basic completeness
            if words < self.config["min_words_per_file"]:
                issues.append(
                    f"Low word count: {words} (min: {self.config['min_words_per_file']})"
                )
                score -= 0.2

            # Check for TODO/FIXME markers
            todos = len(re.findall(r"\b(TODO|FIXME)\b", content, re.IGNORECASE))
            if todos > 0:
                issues.append(f"Found {todos} TODO/FIXME markers")

            # Check heading hierarchy
            if not self.check_heading_hierarchy(headings):
                issues.append("Inconsistent heading hierarchy")
                score -= 0.1

            # Check for missing alt text in images
            missing_alt = sum(1 for alt, _ in images if not alt.strip())
            if missing_alt > 0:
                issues.append(f"Missing alt text for {missing_alt} images")
                score -= 0.1

            return DocFile(
                path=file_path,
                size=stat.st_size,
                mtime=stat.st_mtime,
                lines=len(lines),
                words=words,
                headings=headings,
                links=link_urls,
                images=images,
                issues=issues,
                score=max(0.0, score),
            )

        except Exception as e:
            return DocFile(
                path=file_path,
                size=0,
                mtime=0,
                lines=0,
                words=0,
                headings=[],
                links=[],
                images=[],
                issues=[f"Error analyzing file: {e}"],
                score=0.0,
            )

    def check_heading_hierarchy(self, headings: FlextCore.Types.StringList) -> bool:
        """Check if heading hierarchy is consistent."""
        if not headings:
            return True

        levels = []
        for heading in headings:
            level = (
                len(re.match(r"^#+", heading).group())
                if re.match(r"^#+", heading)
                else 1
            )
            levels.append(level)

        # Check for reasonable hierarchy (no skipping levels)
        return all(levels[i] <= levels[i - 1] + 1 for i in range(1, len(levels)))

    def validate_links(
        self, doc_file: DocFile, timeout: int = 10
    ) -> tuple[int, FlextCore.Types.StringList]:
        """Validate external links in a document."""
        broken_links = []
        checked = 0

        for link in doc_file.links:
            if link.startswith(("http://", "https://")):
                try:
                    response = requests.head(
                        link, timeout=timeout, allow_redirects=True
                    )
                    if response.status_code >= 400:
                        broken_links.append(f"{link} (HTTP {response.status_code})")
                except requests.RequestException as e:
                    broken_links.append(f"{link} ({e!s})")
                checked += 1

        return checked, broken_links

    def validate_images(
        self, doc_file: DocFile
    ) -> tuple[int, FlextCore.Types.StringList]:
        """Validate image references in a document."""
        missing_images = []
        checked = 0

        for _alt, src in doc_file.images:
            if src.startswith(("http://", "https://")):
                try:
                    response = requests.head(src, timeout=5)
                    if response.status_code >= 400:
                        missing_images.append(f"{src} (HTTP {response.status_code})")
                except requests.RequestException as e:
                    missing_images.append(f"{src} ({e!s})")
            else:
                # Local image - check if file exists
                img_path = doc_file.path.parent / src
                if not img_path.exists():
                    missing_images.append(f"{src} (file not found)")
            checked += 1

        return checked, missing_images

    def check_freshness(self, doc_file: DocFile) -> bool:
        """Check if a document is fresh (not outdated)."""
        max_age_days = self.config["max_age_days"]
        age_days = (time.time() - doc_file.mtime) / (24 * 3600)
        return age_days <= max_age_days

    def run_audit(self, verbose: bool = False) -> AuditResult:
        """Run comprehensive documentation audit."""
        print("🔍 Running documentation audit...")

        result = AuditResult()
        doc_files = self.discover_docs()

        print(f"📁 Found {len(doc_files)} documentation files")

        for i, file_path in enumerate(doc_files):
            if verbose and (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(doc_files)} files...")

            doc_file = self.analyze_file(file_path)

            # Validate links and images
            _, broken_links = self.validate_links(doc_file)
            _, missing_images = self.validate_images(doc_file)

            doc_file.issues.extend([f"Broken link: {link}" for link in broken_links])
            doc_file.issues.extend([f"Missing image: {img}" for img in missing_images])

            # Check freshness
            if not self.check_freshness(doc_file):
                age_days = int((time.time() - doc_file.mtime) / (24 * 3600))
                doc_file.issues.append(f"Outdated: {age_days} days old")
                result.outdated_files += 1

            # Update counters
            result.total_files += 1
            result.total_words += doc_file.words
            result.total_links += len(doc_file.links)
            result.total_images += len(doc_file.images)
            result.broken_links += len(broken_links)
            result.missing_images += len(missing_images)
            result.style_issues += len([
                i
                for i in doc_file.issues
                if any(
                    keyword in i.lower() for keyword in ["heading", "alt text", "style"]
                )
            ])

            result.files.append(doc_file)

        # Calculate completeness score
        if result.total_files > 0:
            avg_score = sum(f.score for f in result.files) / result.total_files
            result.completeness_score = avg_score

        # Categorize issues
        result.issues = self.categorize_issues(result.files)

        print("✅ Audit complete!")
        return result

    def categorize_issues(
        self, files: list[DocFile]
    ) -> dict[str, FlextCore.Types.StringList]:
        """Categorize issues by type."""
        categories = defaultdict(list)

        for doc_file in files:
            for issue in doc_file.issues:
                if "broken link" in issue.lower():
                    categories["broken_links"].append(f"{doc_file.path}: {issue}")
                elif "missing image" in issue.lower():
                    categories["missing_images"].append(f"{doc_file.path}: {issue}")
                elif "outdated" in issue.lower():
                    categories["outdated"].append(f"{doc_file.path}: {issue}")
                elif "todo" in issue.lower() or "fixme" in issue.lower():
                    categories["todos"].append(f"{doc_file.path}: {issue}")
                elif "heading" in issue.lower():
                    categories["style"].append(f"{doc_file.path}: {issue}")
                elif "alt text" in issue.lower():
                    categories["accessibility"].append(f"{doc_file.path}: {issue}")
                else:
                    categories["other"].append(f"{doc_file.path}: {issue}")

        return dict(categories)

    def generate_report(
        self, audit_result: AuditResult, output_file: str | None = None
    ) -> str:
        """Generate comprehensive audit report."""
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# FLEXT Documentation Audit Report

**Generated:** {timestamp}
**Files Analyzed:** {audit_result.total_files}
**Total Words:** {audit_result.total_words:,}
**Completeness Score:** {audit_result.completeness_score:.2%}

## 📊 Summary

| Metric | Value | Status |
|--------|-------|---------|
| Total Files | {audit_result.total_files} | ✅ |
| Total Words | {audit_result.total_words:,} | ✅ |
| External Links | {audit_result.total_links} | {"⚠️" if audit_result.broken_links > 0 else "✅"} |
| Images | {audit_result.total_images} | {"⚠️" if audit_result.missing_images > 0 else "✅"} |
| Broken Links | {audit_result.broken_links} | {"❌" if audit_result.broken_links > 0 else "✅"} |
| Missing Images | {audit_result.missing_images} | {"❌" if audit_result.missing_images > 0 else "✅"} |
| Outdated Files | {audit_result.outdated_files} | {"⚠️" if audit_result.outdated_files > 0 else "✅"} |
| Style Issues | {audit_result.style_issues} | {"⚠️" if audit_result.style_issues > 0 else "✅"} |

## 🔍 Issues by Category

"""

        for category, issues in audit_result.issues.items():
            if issues:
                report += (
                    f"### {category.replace('_', ' ').title()} ({len(issues)})\n\n"
                )
                for issue in issues[:10]:  # Show first 10 issues per category
                    report += f"- {issue}\n"
                if len(issues) > 10:
                    report += f"- ... and {len(issues) - 10} more\n"
                report += "\n"

        # Recommendations
        report += """## 💡 Recommendations

"""

        if audit_result.broken_links > 0:
            report += f"- **Fix {audit_result.broken_links} broken links**\n"
        if audit_result.missing_images > 0:
            report += f"- **Fix {audit_result.missing_images} missing images**\n"
        if audit_result.outdated_files > 0:
            report += f"- **Update {audit_result.outdated_files} outdated files**\n"
        if audit_result.style_issues > 0:
            report += f"- **Fix {audit_result.style_issues} style issues**\n"

        if audit_result.completeness_score < 0.8:
            report += "- **Improve overall documentation completeness**\n"

        report += "\n## 📈 Quality Scores\n\n"
        report += f"- **Completeness:** {audit_result.completeness_score:.2%}\n"
        report += f"- **Freshness:** {(1 - audit_result.outdated_files / max(1, audit_result.total_files)):.2%}\n"
        report += f"- **Link Health:** {(1 - audit_result.broken_links / max(1, audit_result.total_links)):.2%}\n"
        report += f"- **Asset Integrity:** {(1 - audit_result.missing_images / max(1, audit_result.total_images)):.2%}\n"

        if output_file:
            output_path = self.output_dir / output_file
            output_path.write_text(report)
            print(f"📄 Report saved to: {output_path}")

        return report

    def optimize_content(self, dry_run: bool = False) -> dict[str, Any]:
        """Optimize and enhance documentation content."""
        print("🔧 Optimizing documentation content...")

        optimizations = {
            "files_processed": 0,
            "optimizations_applied": 0,
            "issues_fixed": [],
        }

        doc_files = self.discover_docs()

        for file_path in doc_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                # Apply optimizations
                content = self.optimize_markdown(content, file_path)

                if content != original_content:
                    if not dry_run:
                        file_path.write_text(content, encoding="utf-8")
                        print(f"✅ Optimized: {file_path}")
                    else:
                        print(f"📋 Would optimize: {file_path}")

                    optimizations["optimizations_applied"] += 1

                optimizations["files_processed"] += 1

            except Exception as e:
                print(f"❌ Error optimizing {file_path}: {e}")

        return optimizations

    def optimize_markdown(self, content: str, file_path: Path) -> str:
        """Apply markdown optimizations."""
        lines = content.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            # Fix common issues
            if line.strip().startswith("#"):
                # Ensure proper heading spacing
                line = re.sub(r"^#{1,6}(.+)$", r"\1".strip(), line)
                line = re.sub(
                    r"^(.+)$",
                    lambda m: f"{'#' * self.get_heading_level(line)} {m.group(1)}",
                    line,
                )

            # Fix list formatting
            if re.match(r"^\s*[-\*\+]\s*", line):
                # Ensure consistent list markers
                line = re.sub(r"^\s*[-\*\+]\s*", "- ", line)

            # Fix code block language specification
            if line.strip() == "```" and i > 0:
                prev_line = lines[i - 1].strip()
                if not prev_line.startswith("```") and prev_line:
                    # Try to infer language from file extension or content
                    lang = self.infer_code_language(prev_line, file_path)
                    if lang:
                        line = f"```{lang}"

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def get_heading_level(self, line: str) -> int:
        """Get heading level from content."""
        # Simple heuristic based on line length and content
        words = len(line.split())
        if words > 50:
            return 1  # Long headings are likely H1
        if words > 20:
            return 2  # Medium headings are likely H2
        if words > 10:
            return 3  # Shorter headings are likely H3
        return 4  # Very short headings are likely H4+

    def infer_code_language(self, prev_line: str, file_path: Path) -> str | None:
        """Infer programming language from context."""
        # Check file extension
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".sql": "sql",
        }

        for ext, lang in ext_map.items():
            if file_path.name.endswith(ext) or ext in prev_line.lower():
                return lang

        # Check content keywords
        if any(
            keyword in prev_line.lower() for keyword in ["import", "def ", "class "]
        ):
            return "python"
        if any(
            keyword in prev_line.lower() for keyword in ["function", "const ", "let "]
        ):
            return "javascript"
        if "select" in prev_line.lower() and "from" in prev_line.lower():
            return "sql"

        return None

    def run_comprehensive_maintenance(
        self, verbose: bool = False, dry_run: bool = False
    ) -> dict[str, Any]:
        """Run all maintenance operations comprehensively."""
        print("🚀 Starting comprehensive documentation maintenance...")

        results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "audit": {},
            "optimization": {},
            "validation": {},
            "summary": {},
        }

        # 1. Run audit
        print("\n1️⃣ Running content quality audit...")
        audit_result = self.run_audit(verbose=verbose)
        results["audit"] = {
            "total_files": audit_result.total_files,
            "completeness_score": audit_result.completeness_score,
            "issues_found": sum(len(issues) for issues in audit_result.issues.values()),
        }

        # 2. Generate audit report
        print("\n2️⃣ Generating audit report...")
        report_file = (
            f"docs_maintenance_audit_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
        )
        self.generate_report(audit_result, report_file)

        # 3. Run optimization
        print("\n3️⃣ Optimizing documentation content...")
        optimization_results = self.optimize_content(dry_run=dry_run)
        results["optimization"] = optimization_results

        # 4. Validation summary
        results["validation"] = {
            "broken_links": audit_result.broken_links,
            "missing_images": audit_result.missing_images,
            "outdated_files": audit_result.outdated_files,
            "style_issues": audit_result.style_issues,
        }

        # 5. Summary
        results["summary"] = {
            "overall_health": "good"
            if audit_result.completeness_score > 0.8
            else "needs_attention",
            "priority_actions": [],
        }

        if audit_result.broken_links > 0:
            results["summary"]["priority_actions"].append(
                f"Fix {audit_result.broken_links} broken links"
            )
        if audit_result.outdated_files > 0:
            results["summary"]["priority_actions"].append(
                f"Update {audit_result.outdated_files} outdated files"
            )
        if audit_result.completeness_score < 0.8:
            results["summary"]["priority_actions"].append(
                "Improve documentation completeness"
            )

        print("\n✅ Comprehensive maintenance complete!")
        print(f"📄 Audit report saved to: {self.output_dir / report_file}")

        # Save results
        results_file = (
            self.output_dir
            / f"maintenance_results_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
        )
        with Path(results_file).open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"📊 Results saved to: {results_file}")

        return results


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Documentation Maintenance System"
    )
    parser.add_argument(
        "command",
        choices=["audit", "validate", "optimize", "sync", "report", "comprehensive"],
        help="Maintenance command to run",
    )
    parser.add_argument("--config", help="Configuration file")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    # Initialize system
    system = DocumentationMaintenanceSystem(args.config)

    try:
        if args.command == "audit":
            result = system.run_audit(verbose=args.verbose)
            print(system.generate_report(result))

        elif args.command == "validate":
            result = system.run_audit(verbose=args.verbose)
            print("🔗 Link validation complete")
            print(
                f"📊 Found {result.broken_links} broken links, {result.missing_images} missing images"
            )

        elif args.command == "optimize":
            results = system.optimize_content(dry_run=args.dry_run)
            print(f"🔧 Optimized {results['optimizations_applied']} files")

        elif args.command == "comprehensive":
            results = system.run_comprehensive_maintenance(
                verbose=args.verbose, dry_run=args.dry_run
            )
            print("📊 Summary:")
            print(".2f")
            print(f"   Files processed: {results['optimization']['files_processed']}")
            print(
                f"   Optimizations applied: {results['optimization']['optimizations_applied']}"
            )
            print(f"   Issues found: {results['audit']['issues_found']}")

        elif args.command == "report":
            result = system.run_audit(verbose=args.verbose)
            report_file = f"docs_maintenance_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
            system.generate_report(result, report_file)

        elif args.command == "sync":
            print("🔄 Synchronizing with version control...")
            # This would integrate with git for automated commits
            print("⚠️ Sync functionality not yet implemented")

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

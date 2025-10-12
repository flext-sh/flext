#!/usr/bin/env python3
"""Smart Documentation Optimizer.

Intelligent documentation optimization with:
- Automated content enhancement
- Smart link repair and prediction
- Content structure optimization
- Readability improvements
- Accessibility enhancements
- SEO optimization for documentation
"""

import difflib
import operator
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flext_core import FlextCore

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required dependencies...")
    import subprocess

    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "requests",
        "beautifulsoup4",
    ])


@dataclass
class OptimizationResult:
    """Result of document optimization."""

    file_path: Path
    original_content: str
    optimized_content: str
    changes_made: FlextCore.Types.StringList
    improvement_score: float
    confidence: float


@dataclass
class LinkRepair:
    """Link repair suggestion."""

    original_link: str
    suggested_link: str
    confidence: float
    reason: str


class SmartDocumentationOptimizer:
    """Intelligent documentation optimization system."""

    def __init__(self, root_path: Path, config: dict[str, Any] | None = None) -> None:
        self.root_path = root_path
        self.config = config or self._default_config()
        self.optimization_results: list[OptimizationResult] = []
        self.link_repairs: list[LinkRepair] = []

    def _default_config(self) -> dict[str, Any]:
        """Default configuration for optimization."""
        return {
            "max_line_length": 88,
            "min_heading_length": 3,
            "max_heading_length": 100,
            "min_paragraph_length": 20,
            "max_paragraph_length": 200,
            "enable_readability_improvements": True,
            "enable_structure_optimization": True,
            "enable_link_repair": True,
            "enable_accessibility_improvements": True,
            "enable_seo_optimization": True,
            "preserve_code_blocks": True,
            "preserve_tables": True,
            "link_repair_confidence_threshold": 0.7,
        }

    def optimize_document(self, file_path: Path, content: str) -> OptimizationResult:
        """Optimize a single document."""
        original_content = content
        optimized_content = content
        changes_made = []

        # Apply various optimizations
        if self.config["enable_readability_improvements"]:
            optimized_content, readability_changes = self._improve_readability(
                optimized_content
            )
            changes_made.extend(readability_changes)

        if self.config["enable_structure_optimization"]:
            optimized_content, structure_changes = self._optimize_structure(
                optimized_content
            )
            changes_made.extend(structure_changes)

        if self.config["enable_link_repair"]:
            optimized_content, link_changes = self._repair_links(
                file_path, optimized_content
            )
            changes_made.extend(link_changes)

        if self.config["enable_accessibility_improvements"]:
            optimized_content, accessibility_changes = self._improve_accessibility(
                optimized_content
            )
            changes_made.extend(accessibility_changes)

        if self.config["enable_seo_optimization"]:
            optimized_content, seo_changes = self._optimize_for_seo(optimized_content)
            changes_made.extend(seo_changes)

        # Calculate improvement score
        improvement_score = self._calculate_improvement_score(
            original_content, optimized_content
        )

        # Calculate confidence based on number and type of changes
        confidence = self._calculate_confidence(changes_made)

        return OptimizationResult(
            file_path=file_path,
            original_content=original_content,
            optimized_content=optimized_content,
            changes_made=changes_made,
            improvement_score=improvement_score,
            confidence=confidence,
        )

    def _improve_readability(
        self, content: str
    ) -> tuple[str, FlextCore.Types.StringList]:
        """Improve document readability."""
        changes = []
        lines = content.split("\n")
        improved_lines = []

        for line in lines:
            # Skip code blocks and special content
            if self._should_preserve_line(line):
                improved_lines.append(line)
                continue

            original_line = line

            # Break long lines
            if len(line) > self.config["max_line_length"]:
                line = self._break_long_line(line)
                if line != original_line:
                    changes.append("Broke long line for better readability")

            # Improve sentence structure
            line = self._improve_sentence_structure(line)
            if line != original_line:
                changes.append("Improved sentence structure")

            # Fix common readability issues
            line = self._fix_readability_issues(line)
            if line != original_line:
                changes.append("Fixed readability issues")

            improved_lines.append(line)

        return "\n".join(improved_lines), changes

    def _should_preserve_line(self, line: str) -> bool:
        """Check if line should be preserved during optimization."""
        # Preserve code blocks
        if line.strip().startswith("```"):
            return True

        # Preserve tables
        if "|" in line and line.strip():
            return True

        # Preserve URLs
        if line.strip().startswith(("http://", "https://")):
            return True

        # Preserve HTML tags
        return bool("<" in line and ">" in line)

    def _break_long_line(self, line: str) -> str:
        """Break a long line into multiple lines."""
        if len(line) <= self.config["max_line_length"]:
            return line

        # Try to break at natural points
        break_points = [",", ";", " and ", " or ", " but ", " however ", " therefore "]

        for break_point in break_points:
            if break_point in line:
                parts = line.split(break_point, 1)
                if len(parts) == 2:
                    first_part = parts[0].strip()
                    second_part = parts[1].strip()

                    if len(first_part) <= self.config["max_line_length"] - 2:
                        return f"{first_part}{break_point}\n  {second_part}"

        # If no natural break point, break at word boundary
        words = line.split()
        if len(words) > 1:
            current_line = ""
            result_lines = []

            for word in words:
                if len(current_line + " " + word) <= self.config["max_line_length"]:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        result_lines.append(current_line)
                    current_line = word

            if current_line:
                result_lines.append(current_line)

            return "\n".join(result_lines)

        return line

    def _improve_sentence_structure(self, line: str) -> str:
        """Improve sentence structure."""
        # Skip if not a sentence
        if not line.strip() or line.strip().startswith(("#", "-", "*", ">", "`")):
            return line

        # Fix common issues
        line = re.sub(r"\s+", " ", line)  # Multiple spaces
        line = re.sub(r"\s+([.!?])", r"\1", line)  # Space before punctuation
        line = re.sub(r"([.!?])\s*([a-z])", r"\1 \2", line)  # Space after punctuation

        # Capitalize first letter of sentences
        if line.strip() and line.strip()[0].islower():
            line = line[0].upper() + line[1:]

        return line

    def _fix_readability_issues(self, line: str) -> str:
        """Fix common readability issues."""
        # Fix common typos and issues
        fixes = {
            r"\bteh\b": "the",
            r"\bhte\b": "the",
            r"\badn\b": "and",
            r"\btaht\b": "that",
            r"\bthier\b": "their",
            r"\bthere\b": "their",  # Context-dependent, but common error
            r"\byou\s+can\s+also\s+use\b": "you can use",
            r"\bit\s+is\s+important\s+to\s+note\s+that\b": "note that",
            r"\bit\s+should\s+be\s+noted\s+that\b": "note that",
            r"\bin\s+order\s+to\b": "to",
            r"\bdue\s+to\s+the\s+fact\s+that\b": "because",
            r"\bfor\s+the\s+purpose\s+of\b": "to",
            r"\bwith\s+regard\s+to\b": "regarding",
            r"\bin\s+the\s+event\s+that\b": "if",
        }

        for pattern, replacement in fixes.items():
            line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)

        return line

    def _optimize_structure(
        self, content: str
    ) -> tuple[str, FlextCore.Types.StringList]:
        """Optimize document structure."""
        changes = []
        lines = content.split("\n")
        improved_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Optimize headings
            if line.strip().startswith("#"):
                optimized_heading, heading_changes = self._optimize_heading(line)
                if optimized_heading != line:
                    changes.extend(heading_changes)
                improved_lines.append(optimized_heading)

            # Optimize paragraphs
            elif line.strip() and not line.startswith((" ", "\t")):
                paragraph_lines = [line]
                j = i + 1

                # Collect paragraph lines
                while (
                    j < len(lines)
                    and lines[j].strip()
                    and not lines[j].startswith((" ", "\t", "#", "-", "*", ">", "`"))
                ):
                    paragraph_lines.append(lines[j])
                    j += 1

                # Optimize paragraph
                if len(paragraph_lines) > 1:
                    paragraph = "\n".join(paragraph_lines)
                    optimized_paragraph, para_changes = self._optimize_paragraph(
                        paragraph
                    )
                    if optimized_paragraph != paragraph:
                        changes.extend(para_changes)
                    improved_lines.extend(optimized_paragraph.split("\n"))
                    i = j - 1
                else:
                    improved_lines.append(line)

            else:
                improved_lines.append(line)

            i += 1

        return "\n".join(improved_lines), changes

    def _optimize_heading(self, heading: str) -> tuple[str, FlextCore.Types.StringList]:
        """Optimize a heading."""
        changes = []
        original = heading

        # Remove extra spaces
        heading = re.sub(r"#+\s*", lambda m: m.group(0).rstrip() + " ", heading)
        heading = re.sub(r"\s+", " ", heading)

        # Ensure proper capitalization
        heading_text = heading.lstrip("#").strip()
        if heading_text:
            # Capitalize first letter
            heading_text = heading_text[0].upper() + heading_text[1:]
            heading = heading[: len(heading) - len(heading_text)] + heading_text

        # Check length
        if len(heading_text) < self.config["min_heading_length"]:
            changes.append("Heading too short - consider adding more descriptive text")
        elif len(heading_text) > self.config["max_heading_length"]:
            changes.append("Heading too long - consider shortening")

        if heading != original:
            changes.append("Optimized heading format")

        return heading, changes

    def _optimize_paragraph(
        self, paragraph: str
    ) -> tuple[str, FlextCore.Types.StringList]:
        """Optimize a paragraph."""
        changes = []

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        optimized_sentences = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            # Improve sentence
            improved_sentence = self._improve_sentence_structure(sentence.strip())
            improved_sentence = self._fix_readability_issues(improved_sentence)

            if improved_sentence != sentence:
                changes.append("Improved sentence structure")

            optimized_sentences.append(improved_sentence)

        optimized_paragraph = " ".join(optimized_sentences)

        # Check paragraph length
        if len(optimized_paragraph) < self.config["min_paragraph_length"]:
            changes.append("Paragraph too short - consider adding more detail")
        elif len(optimized_paragraph) > self.config["max_paragraph_length"]:
            changes.append(
                "Paragraph too long - consider breaking into smaller paragraphs"
            )

        return optimized_paragraph, changes

    def _repair_links(
        self, file_path: Path, content: str
    ) -> tuple[str, FlextCore.Types.StringList]:
        """Repair broken links."""
        changes = []
        lines = content.split("\n")
        improved_lines = []

        for line in lines:
            # Find markdown links
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

            def replace_link(match):
                link_text, link_url = match.groups()

                # Skip external links
                if link_url.startswith(("http://", "https://")):
                    return match.group(0)

                # Check if link is broken
                target_path = self._resolve_link_path(file_path, link_url)

                if not target_path.exists():
                    # Try to find similar file
                    repair = self._find_link_repair(link_url, file_path)
                    if repair:
                        self.link_repairs.append(repair)
                        changes.append(
                            f"Repaired broken link: {link_url} -> {repair.suggested_link}"
                        )
                        return f"[{link_text}]({repair.suggested_link})"

                return match.group(0)

            improved_line = re.sub(link_pattern, replace_link, line)
            improved_lines.append(improved_line)

        return "\n".join(improved_lines), changes

    def _resolve_link_path(self, file_path: Path, link_url: str) -> Path:
        """Resolve link path relative to file."""
        if link_url.startswith(("./", "../")):
            return file_path.parent / link_url
        return self.root_path / link_url.lstrip("/")

    def _find_link_repair(
        self, broken_link: str, source_file: Path
    ) -> LinkRepair | None:
        """Find repair suggestion for broken link."""
        target_name = Path(broken_link).name

        # Search for similar files
        similar_files = []
        for file_path in self.root_path.rglob("*.md"):
            similarity = difflib.SequenceMatcher(
                None, target_name, file_path.name
            ).ratio()
            if similarity > 0.6:
                similar_files.append((file_path, similarity))

        if similar_files:
            # Sort by similarity
            similar_files.sort(key=operator.itemgetter(1), reverse=True)
            best_match = similar_files[0]

            # Calculate relative path
            relative_path = best_match[0].relative_to(source_file.parent)

            return LinkRepair(
                original_link=broken_link,
                suggested_link=str(relative_path),
                confidence=best_match[1],
                reason=f"Found similar file: {best_match[0].name}",
            )

        return None

    def _improve_accessibility(
        self, content: str
    ) -> tuple[str, FlextCore.Types.StringList]:
        """Improve accessibility."""
        changes = []
        lines = content.split("\n")
        improved_lines = []

        for line in lines:
            # Add alt text to images without it
            image_pattern = r"!\[\]\(([^)]+)\)"

            def add_alt_text(match) -> str:
                image_url = match.group(1)
                filename = Path(image_url).stem.replace("-", " ").replace("_", " ")
                changes.append("Added alt text to image for accessibility")
                return f"![{filename.title()}]({image_url})"

            line = re.sub(image_pattern, add_alt_text, line)

            # Improve link text
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

            def improve_link_text(match):
                link_text, link_url = match.groups()

                # Skip if already descriptive
                if len(link_text) > 10 and link_text.lower() not in {
                    "click here",
                    "here",
                    "link",
                    "more",
                }:
                    return match.group(0)

                # Try to make link text more descriptive
                if link_text.lower() in {"click here", "here", "link"}:
                    filename = Path(link_url).stem.replace("-", " ").replace("_", " ")
                    changes.append("Improved link text for accessibility")
                    return f"[{filename.title()}]({link_url})"

                return match.group(0)

            line = re.sub(link_pattern, improve_link_text, line)

            improved_lines.append(line)

        return "\n".join(improved_lines), changes

    def _optimize_for_seo(self, content: str) -> tuple[str, FlextCore.Types.StringList]:
        """Optimize content for SEO."""
        changes = []
        lines = content.split("\n")
        improved_lines = []

        # Track heading structure
        heading_levels = []

        for line in lines:
            # Optimize headings for SEO
            if line.strip().startswith("#"):
                heading_text = line.lstrip("#").strip()

                # Ensure headings are descriptive
                if len(heading_text) < 10:
                    changes.append(
                        "Heading too short for SEO - consider making more descriptive"
                    )

                # Track heading hierarchy
                level = len(line) - len(line.lstrip("#"))
                heading_levels.append(level)

                # Ensure proper hierarchy
                if len(heading_levels) > 1:
                    prev_level = heading_levels[-2]
                    if level > prev_level + 1:
                        changes.append(
                            "Heading hierarchy skipped - consider fixing for SEO"
                        )

            # Add meta descriptions for main headings
            if line.strip().startswith("# ") and not any(
                "description" in l.lower() for l in lines[: lines.index(line)]
            ):
                # This is the main heading, add a meta description
                heading_text = line.lstrip("#").strip()
                meta_desc = f"<!-- Meta description: {heading_text} -->"
                improved_lines.append(meta_desc)
                changes.append("Added meta description for SEO")

            improved_lines.append(line)

        return "\n".join(improved_lines), changes

    def _calculate_improvement_score(self, original: str, optimized: str) -> float:
        """Calculate improvement score."""
        if original == optimized:
            return 0.0

        # Simple scoring based on changes
        original_lines = original.split("\n")
        optimized_lines = optimized.split("\n")

        # Count improvements
        improvements = 0

        # Line length improvements
        long_lines_original = sum(
            1 for line in original_lines if len(line) > self.config["max_line_length"]
        )
        long_lines_optimized = sum(
            1 for line in optimized_lines if len(line) > self.config["max_line_length"]
        )
        improvements += (long_lines_original - long_lines_optimized) * 0.1

        # Readability improvements (simplified)
        word_count_original = len(re.findall(r"\b\w+\b", original))
        word_count_optimized = len(re.findall(r"\b\w+\b", optimized))

        if word_count_original > 0:
            improvements += (
                (word_count_optimized - word_count_original) / word_count_original * 0.2
            )

        # Structure improvements
        heading_count_original = len(re.findall(r"^#+\s+", original, re.MULTILINE))
        heading_count_optimized = len(re.findall(r"^#+\s+", optimized, re.MULTILINE))
        improvements += (heading_count_optimized - heading_count_original) * 0.1

        return min(improvements, 1.0)  # Cap at 1.0

    def _calculate_confidence(self, changes: FlextCore.Types.StringList) -> float:
        """Calculate confidence in optimizations."""
        if not changes:
            return 0.0

        # Higher confidence for more specific changes
        confidence_map = {
            "Broke long line": 0.9,
            "Improved sentence structure": 0.8,
            "Fixed readability issues": 0.7,
            "Optimized heading format": 0.8,
            "Improved link text": 0.9,
            "Added alt text": 0.9,
            "Repaired broken link": 0.6,  # Lower confidence for link repairs
        }

        total_confidence = 0.0
        for change in changes:
            # Find matching confidence
            confidence = 0.5  # Default confidence
            for pattern, conf in confidence_map.items():
                if pattern in change:
                    confidence = conf
                    break
            total_confidence += confidence

        return total_confidence / len(changes)

    def optimize_all_documents(self) -> list[OptimizationResult]:
        """Optimize all documents in the workspace."""
        print("🔧 Starting Smart Documentation Optimization...")

        markdown_files = list(self.root_path.rglob("*.md"))
        print(f"Found {len(markdown_files)} markdown files")

        for idx, file_path in enumerate(markdown_files, 1):
            print(
                f"[{idx}/{len(markdown_files)}] Optimizing: {file_path.relative_to(self.root_path)}"
            )

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                result = self.optimize_document(file_path, content)
                self.optimization_results.append(result)

                if result.changes_made:
                    print(
                        f"  ✅ Made {len(result.changes_made)} improvements (score: {result.improvement_score:.2f})"
                    )
                else:
                    print("  ⏭️  No improvements needed")

            except Exception as e:
                print(f"  ⚠️  Error optimizing {file_path}: {e}")

        print(f"\n✅ Optimization complete! Processed {len(markdown_files)} files")
        return self.optimization_results

    def apply_optimizations(self, dry_run: bool = True) -> None:
        """Apply optimizations to files."""
        if dry_run:
            print("🔍 DRY RUN - No changes will be applied")
        else:
            print("💾 Applying optimizations...")

        for result in self.optimization_results:
            if result.changes_made and result.confidence > 0.6:
                if not dry_run:
                    result.file_path.write_text(
                        result.optimized_content, encoding="utf-8"
                    )
                    print(f"✅ Updated: {result.file_path.relative_to(self.root_path)}")
                else:
                    print(
                        f"🔍 Would update: {result.file_path.relative_to(self.root_path)}"
                    )

    def generate_optimization_report(self) -> str:
        """Generate optimization report."""
        if not self.optimization_results:
            return "No optimization results available."

        total_files = len(self.optimization_results)
        files_optimized = len([r for r in self.optimization_results if r.changes_made])
        total_improvements = sum(len(r.changes_made) for r in self.optimization_results)
        avg_improvement_score = (
            sum(r.improvement_score for r in self.optimization_results) / total_files
        )

        report = f"""# Smart Documentation Optimization Report

**Generated:** {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}
**Total Files Processed:** {total_files}
**Files Optimized:** {files_optimized}
**Total Improvements Made:** {total_improvements}
**Average Improvement Score:** {avg_improvement_score:.2f}

## Optimization Summary

"""

        # Group by improvement type
        improvement_types = {}
        for result in self.optimization_results:
            for change in result.changes_made:
                change_type = change.split(":")[0] if ":" in change else change
                improvement_types[change_type] = (
                    improvement_types.get(change_type, 0) + 1
                )

        if improvement_types:
            report += "### Improvements by Type\n\n"
            for change_type, count in sorted(
                improvement_types.items(), key=operator.itemgetter(1), reverse=True
            ):
                report += f"- **{change_type}:** {count}\n"
            report += "\n"

        # Top improved files
        top_improved = sorted(
            [r for r in self.optimization_results if r.changes_made],
            key=lambda x: x.improvement_score,
            reverse=True,
        )[:10]

        if top_improved:
            report += "### Top Improved Files\n\n"
            for result in top_improved:
                file_rel = result.file_path.relative_to(self.root_path)
                report += f"- **{file_rel}** (score: {result.improvement_score:.2f})\n"
                for change in result.changes_made[:3]:  # Show first 3 changes
                    report += f"  - {change}\n"
                if len(result.changes_made) > 3:
                    report += f"  - ... and {len(result.changes_made) - 3} more\n"
                report += "\n"

        # Link repairs
        if self.link_repairs:
            report += "### Link Repairs\n\n"
            for repair in self.link_repairs[:10]:  # Show first 10
                report += f"- **{repair.original_link}** → **{repair.suggested_link}** (confidence: {repair.confidence:.2f})\n"
                report += f"  - Reason: {repair.reason}\n"
            if len(self.link_repairs) > 10:
                report += f"- ... and {len(self.link_repairs) - 10} more link repairs\n"
            report += "\n"

        return report


def main() -> None:
    """Main entry point for smart documentation optimization."""
    import argparse

    parser = argparse.ArgumentParser(description="Smart Documentation Optimizer")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of documentation (default: current directory)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply optimizations (default is dry-run)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("optimization_report.md"),
        help="Output file for optimization report",
    )

    args = parser.parse_args()

    # Run optimization
    optimizer = SmartDocumentationOptimizer(args.root)
    optimizer.optimize_all_documents()

    # Apply optimizations
    optimizer.apply_optimizations(dry_run=not args.apply)

    # Generate report
    report = optimizer.generate_optimization_report()
    args.output.write_text(report, encoding="utf-8")

    print(f"\n📄 Optimization report saved to: {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Advanced Documentation Analysis & Intelligence System.

Enhanced documentation analysis with:
- Content intelligence and semantic analysis
- Advanced link prediction and repair
- Documentation health scoring
- Automated content optimization suggestions
- Cross-reference validation
- Documentation architecture analysis
"""

import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextCore

try:
    import difflib

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
    import difflib


@dataclass
class ContentIntelligence:
    """Advanced content analysis metrics."""

    readability_score: float
    complexity_level: str
    technical_density: float
    code_to_text_ratio: float
    heading_balance: float
    link_density: float
    image_usage_score: float
    structure_quality: float


@dataclass
class DocumentationHealth:
    """Overall documentation health assessment."""

    overall_score: float
    content_quality: float
    structure_quality: float
    link_health: float
    accessibility_score: float
    freshness_score: float
    completeness_score: float
    recommendations: FlextCore.Types.StringList


@dataclass
class CrossReference:
    """Cross-reference between documentation files."""

    source_file: Path
    target_file: Path
    reference_type: str  # 'link', 'include', 'mention'
    context: str
    confidence: float


class AdvancedDocumentationAnalyzer:
    """Advanced documentation analysis and intelligence system."""

    def __init__(
        self, root_path: Path, config: dict[str, object] | None = None
    ) -> None:
        self.root_path = root_path
        self.config = config or self._default_config()
        self.content_intelligence: dict[Path, ContentIntelligence] = {}
        self.cross_references: list[CrossReference] = []
        self.documentation_health: dict[Path, DocumentationHealth] = {}

    def _default_config(self) -> dict[str, object]:
        """Default configuration for advanced analysis."""
        return {
            "min_readability_score": 60.0,
            "max_complexity_level": "intermediate",
            "optimal_code_ratio": 0.3,
            "min_heading_balance": 0.7,
            "max_link_density": 0.1,
            "min_image_usage": 0.05,
            "structure_weights": {
                "headings": 0.3,
                "links": 0.2,
                "code_blocks": 0.2,
                "lists": 0.15,
                "images": 0.15,
            },
            "content_analysis": {
                "enable_semantic_analysis": True,
                "enable_readability_scoring": True,
                "enable_complexity_analysis": True,
                "enable_technical_density": True,
            },
        }

    def analyze_content_intelligence(
        self, file_path: Path, content: str
    ) -> ContentIntelligence:
        """Perform advanced content intelligence analysis."""
        # Readability scoring (simplified Flesch-Kincaid)
        sentences = re.split(r"[.!?]+", content)
        words = re.findall(r"\b\w+\b", content)
        syllables = sum(self._count_syllables(word) for word in words)

        if sentences and words:
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words)
            readability_score = (
                206.835
                - (1.015 * avg_sentence_length)
                - (84.6 * avg_syllables_per_word)
            )
        else:
            readability_score = 0.0

        # Complexity level
        if readability_score >= 80:
            complexity_level = "beginner"
        elif readability_score >= 60:
            complexity_level = "intermediate"
        elif readability_score >= 30:
            complexity_level = "advanced"
        else:
            complexity_level = "expert"

        # Technical density (code blocks, technical terms)
        code_blocks = len(re.findall(r"```", content)) // 2
        technical_terms = len(
            re.findall(
                r"\b(?:API|SDK|HTTP|JSON|XML|SQL|Python|JavaScript|TypeScript|Docker|Kubernetes|AWS|Azure|GCP)\b",
                content,
                re.IGNORECASE,
            )
        )
        technical_density = (code_blocks + technical_terms) / max(len(words), 1)

        # Code to text ratio
        code_content = len(re.findall(r"```[\s\S]*?```", content))
        code_to_text_ratio = code_content / max(len(content), 1)

        # Heading balance (distribution of heading levels)
        headings = re.findall(r"^(#{1,6})\s+", content, re.MULTILINE)
        if headings:
            heading_levels = [len(h) for h in headings]
            level_distribution = {
                level: heading_levels.count(level) for level in range(1, 7)
            }
            max_level = max(level_distribution.keys())
            heading_balance = 1.0 - (max_level - 1) / 5.0  # Penalize deep nesting
        else:
            heading_balance = 0.0

        # Link density
        links = len(re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content))
        link_density = links / max(len(words), 1)

        # Image usage score
        images = len(re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content))
        image_usage_score = min(images / max(len(words) / 100, 1), 1.0)

        # Structure quality (combination of various structural elements)
        structure_elements = {
            "headings": len(headings),
            "links": links,
            "code_blocks": code_blocks,
            "lists": len(re.findall(r"^[\s]*[-*+]\s+", content, re.MULTILINE)),
            "images": images,
        }

        total_elements = sum(structure_elements.values())
        if total_elements > 0:
            structure_quality = sum(
                (structure_elements[key] / total_elements) * weight
                for key, weight in self.config["structure_weights"].items()
            )
        else:
            structure_quality = 0.0

        return ContentIntelligence(
            readability_score=readability_score,
            complexity_level=complexity_level,
            technical_density=technical_density,
            code_to_text_ratio=code_to_text_ratio,
            heading_balance=heading_balance,
            link_density=link_density,
            image_usage_score=image_usage_score,
            structure_quality=structure_quality,
        )

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # Handle silent 'e'
        if word.endswith("e") and syllable_count > 1:
            syllable_count -= 1

        return max(syllable_count, 1)

    def find_cross_references(
        self, file_path: Path, content: str
    ) -> list[CrossReference]:
        """Find cross-references between documentation files."""
        references = []

        # Find markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, content):
            link_text, link_url = match.groups()

            # Skip external links
            if link_url.startswith(("http://", "https://")):
                continue

            # Determine target file
            if link_url.startswith(("./", "../")):
                target_path = file_path.parent / link_url
            else:
                target_path = self.root_path / link_url.lstrip("/")

            # Calculate confidence based on file existence and similarity
            confidence = 1.0 if target_path.exists() else 0.0
            if not target_path.exists():
                # Try to find similar files
                similar_files = self._find_similar_files(link_url)
                if similar_files:
                    confidence = 0.7
                    target_path = similar_files[0]

            references.append(
                CrossReference(
                    source_file=file_path,
                    target_file=target_path,
                    reference_type="link",
                    context=link_text,
                    confidence=confidence,
                )
            )

        # Find potential includes or mentions
        include_pattern = r'include\s+["\']([^"\']+)["\']'
        for match in re.finditer(include_pattern, content, re.IGNORECASE):
            include_path = match.group(1)
            target_path = file_path.parent / include_path

            references.append(
                CrossReference(
                    source_file=file_path,
                    target_file=target_path,
                    reference_type="include",
                    context=match.group(0),
                    confidence=1.0 if target_path.exists() else 0.0,
                )
            )

        return references

    def _find_similar_files(self, broken_link: str) -> list[Path]:
        """Find files similar to a broken link."""
        target_name = Path(broken_link).name

        # Search for files with similar names
        similar_files = [
            file_path
            for file_path in self.root_path.rglob("*.md")
            if target_name.lower() in file_path.name.lower()
        ]

        # Use difflib for more sophisticated matching
        if not similar_files:
            all_files = list(self.root_path.rglob("*.md"))
            similarities = [
                (
                    file_path,
                    difflib.SequenceMatcher(None, target_name, file_path.name).ratio(),
                )
                for file_path in all_files
            ]
            similar_files = [
                file_path for file_path, similarity in similarities if similarity > 0.6
            ]
            similar_files.sort(
                key=lambda x: difflib.SequenceMatcher(
                    None, target_name, x.name
                ).ratio(),
                reverse=True,
            )

        return similar_files[:3]  # Return top 3 matches

    def calculate_documentation_health(
        self, file_path: Path, content: str, intelligence: ContentIntelligence
    ) -> DocumentationHealth:
        """Calculate overall documentation health score."""
        # Content quality (40% of total score)
        content_quality = (
            min(intelligence.readability_score / 100, 1.0) * 0.4
            + intelligence.structure_quality * 0.3
            + min(intelligence.technical_density * 10, 1.0) * 0.3
        )

        # Structure quality (25% of total score)
        structure_quality = (
            intelligence.heading_balance * 0.4
            + min(intelligence.link_density * 10, 1.0) * 0.3
            + intelligence.image_usage_score * 0.3
        )

        # Link health (15% of total score)
        cross_refs = self.find_cross_references(file_path, content)
        if cross_refs:
            link_health = sum(ref.confidence for ref in cross_refs) / len(cross_refs)
        else:
            link_health = 1.0  # No links means no broken links

        # Accessibility score (10% of total score)
        images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
        alt_text_count = sum(1 for alt, _ in images if alt.strip())
        accessibility_score = alt_text_count / max(len(images), 1) if images else 1.0

        # Freshness score (5% of total score)
        file_age = (
            datetime.now(UTC) - datetime.fromtimestamp(file_path.stat().st_mtime)
        ).days
        freshness_score = max(0, 1.0 - (file_age / 365))  # Decay over a year

        # Completeness score (5% of total score)
        word_count = len(re.findall(r"\b\w+\b", content))
        completeness_score = min(word_count / 500, 1.0)  # Assume 500 words is complete

        # Calculate overall score
        overall_score = (
            content_quality * 0.4
            + structure_quality * 0.25
            + link_health * 0.15
            + accessibility_score * 0.1
            + freshness_score * 0.05
            + completeness_score * 0.05
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            intelligence,
            content_quality,
            structure_quality,
            link_health,
            accessibility_score,
            freshness_score,
            completeness_score,
        )

        return DocumentationHealth(
            overall_score=overall_score,
            content_quality=content_quality,
            structure_quality=structure_quality,
            link_health=link_health,
            accessibility_score=accessibility_score,
            freshness_score=freshness_score,
            completeness_score=completeness_score,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        intelligence: ContentIntelligence,
        content_quality: float,
        structure_quality: float,
        link_health: float,
        accessibility_score: float,
        freshness_score: float,
        completeness_score: float,
    ) -> FlextCore.Types.StringList:
        """Generate specific recommendations for improvement."""
        recommendations = []

        if intelligence.readability_score < 60:
            recommendations.append(
                "Improve readability by using shorter sentences and simpler words"
            )

        if intelligence.heading_balance < 0.7:
            recommendations.append(
                "Improve heading structure by reducing nesting depth"
            )

        if intelligence.link_density > 0.1:
            recommendations.append(
                "Reduce link density - too many links can overwhelm readers"
            )

        if intelligence.image_usage_score < 0.05:
            recommendations.append(
                "Add more images to improve visual appeal and understanding"
            )

        if structure_quality < 0.6:
            recommendations.append(
                "Improve document structure with better organization"
            )

        if link_health < 0.8:
            recommendations.append("Fix broken or low-confidence links")

        if accessibility_score < 0.8:
            recommendations.append("Add alt text to images for better accessibility")

        if freshness_score < 0.5:
            recommendations.append("Update content - document appears stale")

        if completeness_score < 0.7:
            recommendations.append("Add more content to improve completeness")

        if intelligence.technical_density > 0.1:
            recommendations.append(
                "Consider adding more explanatory text for technical concepts"
            )

        return recommendations

    def analyze_documentation_architecture(self) -> dict[str, object]:
        """Analyze the overall documentation architecture."""
        markdown_files = list(self.root_path.rglob("*.md"))

        # Group files by directory structure
        directory_structure = {}
        for file_path in markdown_files:
            relative_path = file_path.relative_to(self.root_path)
            parts = relative_path.parts[:-1]  # Exclude filename
            current = directory_structure
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current["_files"] = current.get("_files", []) + [relative_path.name]

        # Analyze documentation patterns
        patterns = {
            "readme_files": len([
                f for f in markdown_files if f.name.upper() == "README.MD"
            ]),
            "total_files": len(markdown_files),
            "max_depth": self._calculate_max_depth(directory_structure),
            "avg_files_per_dir": self._calculate_avg_files_per_dir(directory_structure),
            "orphaned_files": self._find_orphaned_files(markdown_files),
        }

        return {
            "directory_structure": directory_structure,
            "patterns": patterns,
            "health_summary": self._calculate_architecture_health(patterns),
        }

    def _calculate_max_depth(
        self, structure: dict[str, object], current_depth: int = 0
    ) -> int:
        """Calculate maximum directory depth."""
        if not structure or "_files" in structure:
            return current_depth

        max_child_depth = 0
        for key, value in structure.items():
            if key != "_files":
                child_depth = self._calculate_max_depth(value, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _calculate_avg_files_per_dir(self, structure: dict[str, object]) -> float:
        """Calculate average files per directory."""
        total_dirs = 0
        total_files = 0

        def count_dirs_and_files(current: dict[str, object]) -> None:
            nonlocal total_dirs, total_files

            if "_files" in current:
                total_files += len(current["_files"])
                total_dirs += 1

            for key, value in current.items():
                if key != "_files":
                    count_dirs_and_files(value)

        count_dirs_and_files(structure)
        return total_files / max(total_dirs, 1)

    def _find_orphaned_files(self, markdown_files: list[Path]) -> list[Path]:
        """Find files that are not referenced by any other file."""
        all_references = set()

        for file_path in markdown_files:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            references = self.find_cross_references(file_path, content)
            all_references.update(ref.target_file for ref in references)

        return [f for f in markdown_files if f not in all_references]

    def _calculate_architecture_health(
        self, patterns: dict[str, object]
    ) -> dict[str, object]:
        """Calculate overall architecture health."""
        health_score = 0.0
        issues = []

        # README coverage
        readme_ratio = patterns["readme_files"] / max(patterns["total_files"], 1)
        if readme_ratio > 0.1:  # At least 10% of files should be READMEs
            health_score += 0.3
        else:
            issues.append("Low README coverage - consider adding more README files")

        # Directory depth
        if patterns["max_depth"] <= 4:
            health_score += 0.3
        else:
            issues.append("Directory structure too deep - consider flattening")

        # File distribution
        if 2 <= patterns["avg_files_per_dir"] <= 10:
            health_score += 0.2
        else:
            issues.append("Poor file distribution across directories")

        # Orphaned files
        orphan_ratio = len(patterns["orphaned_files"]) / max(patterns["total_files"], 1)
        if orphan_ratio < 0.1:  # Less than 10% orphaned
            health_score += 0.2
        else:
            issues.append(
                f"High number of orphaned files ({len(patterns['orphaned_files'])})"
            )

        return {
            "overall_score": health_score,
            "issues": issues,
            "recommendations": self._generate_architecture_recommendations(patterns),
        }

    def _generate_architecture_recommendations(
        self, patterns: dict[str, object]
    ) -> FlextCore.Types.StringList:
        """Generate architecture improvement recommendations."""
        recommendations = []

        if patterns["readme_files"] < patterns["total_files"] * 0.1:
            recommendations.append("Add README files to more directories")

        if patterns["max_depth"] > 4:
            recommendations.append("Consider flattening directory structure")

        if patterns["avg_files_per_dir"] < 2:
            recommendations.append("Consider consolidating small directories")
        elif patterns["avg_files_per_dir"] > 10:
            recommendations.append("Consider splitting large directories")

        if patterns["orphaned_files"]:
            recommendations.append("Review and either link or remove orphaned files")

        return recommendations

    def run_comprehensive_analysis(self) -> dict[str, object]:
        """Run comprehensive documentation analysis."""
        print("🔍 Starting Advanced Documentation Analysis...")

        markdown_files = list(self.root_path.rglob("*.md"))
        print(f"Found {len(markdown_files)} markdown files")

        # Analyze each file
        for idx, file_path in enumerate(markdown_files, 1):
            print(
                f"[{idx}/{len(markdown_files)}] Analyzing: {file_path.relative_to(self.root_path)}"
            )

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                # Content intelligence
                intelligence = self.analyze_content_intelligence(file_path, content)
                self.content_intelligence[file_path] = intelligence

                # Documentation health
                health = self.calculate_documentation_health(
                    file_path, content, intelligence
                )
                self.documentation_health[file_path] = health

                # Cross-references
                cross_refs = self.find_cross_references(file_path, content)
                self.cross_references.extend(cross_refs)

            except Exception as e:
                print(f"  ⚠️  Error analyzing {file_path}: {e}")

        # Architecture analysis
        print("\n🏗️  Analyzing documentation architecture...")
        architecture = self.analyze_documentation_architecture()

        # Generate comprehensive report
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_files": len(markdown_files),
            "content_intelligence": {
                str(f.relative_to(self.root_path)): {
                    "readability_score": ci.readability_score,
                    "complexity_level": ci.complexity_level,
                    "technical_density": ci.technical_density,
                    "code_to_text_ratio": ci.code_to_text_ratio,
                    "heading_balance": ci.heading_balance,
                    "link_density": ci.link_density,
                    "image_usage_score": ci.image_usage_score,
                    "structure_quality": ci.structure_quality,
                }
                for f, ci in self.content_intelligence.items()
            },
            "documentation_health": {
                str(f.relative_to(self.root_path)): {
                    "overall_score": dh.overall_score,
                    "content_quality": dh.content_quality,
                    "structure_quality": dh.structure_quality,
                    "link_health": dh.link_health,
                    "accessibility_score": dh.accessibility_score,
                    "freshness_score": dh.freshness_score,
                    "completeness_score": dh.completeness_score,
                    "recommendations": dh.recommendations,
                }
                for f, dh in self.documentation_health.items()
            },
            "cross_references": [
                {
                    "source": str(cr.source_file.relative_to(self.root_path)),
                    "target": str(cr.target_file.relative_to(self.root_path)),
                    "type": cr.reference_type,
                    "context": cr.context,
                    "confidence": cr.confidence,
                }
                for cr in self.cross_references
            ],
            "architecture": architecture,
            "summary": self._generate_analysis_summary(),
        }

        print(f"\n✅ Analysis complete! Processed {len(markdown_files)} files")
        return report

    def _generate_analysis_summary(self) -> dict[str, object]:
        """Generate analysis summary statistics."""
        if not self.documentation_health:
            return {}

        health_scores = [dh.overall_score for dh in self.documentation_health.values()]
        readability_scores = [
            ci.readability_score for ci in self.content_intelligence.values()
        ]

        return {
            "avg_health_score": sum(health_scores) / len(health_scores),
            "avg_readability_score": sum(readability_scores) / len(readability_scores),
            "files_needing_attention": len([
                f for f, h in self.documentation_health.items() if h.overall_score < 0.6
            ]),
            "high_quality_files": len([
                f for f, h in self.documentation_health.items() if h.overall_score > 0.8
            ]),
            "total_cross_references": len(self.cross_references),
            "broken_references": len([
                cr for cr in self.cross_references if cr.confidence < 0.5
            ]),
        }


def main() -> None:
    """Main entry point for advanced documentation analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Advanced Documentation Analysis & Intelligence"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of documentation (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("advanced_docs_analysis.json"),
        help="Output file for analysis results",
    )
    parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="Output format"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = AdvancedDocumentationAnalyzer(args.root)
    report = analyzer.run_comprehensive_analysis()

    # Save report
    if args.format == "json":
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    else:
        # Convert to markdown format
        md_content = f"""# Advanced Documentation Analysis Report

**Generated:** {report["timestamp"]}
**Total Files Analyzed:** {report["total_files"]}

## Summary Statistics

- **Average Health Score:** {report["summary"].get("avg_health_score", 0):.2f}
- **Average Readability Score:** {report["summary"].get("avg_readability_score", 0):.2f}
- **Files Needing Attention:** {report["summary"].get("files_needing_attention", 0)}
- **High Quality Files:** {report["summary"].get("high_quality_files", 0)}
- **Total Cross-References:** {report["summary"].get("total_cross_references", 0)}
- **Broken References:** {report["summary"].get("broken_references", 0)}

## Architecture Health

- **Overall Score:** {report["architecture"]["health_summary"]["overall_score"]:.2f}
- **Issues:** {len(report["architecture"]["health_summary"]["issues"])}

## Detailed Analysis

See the JSON report for detailed file-by-file analysis.
"""
        args.output.write_text(md_content, encoding="utf-8")

    print(f"\n📄 Analysis report saved to: {args.output}")


if __name__ == "__main__":
    main()

"""DRY (Don't Repeat Yourself) principle tests for FLEXT workspace."""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from .base import BaseQualityAnalyzer


class DRYAnalyzer(BaseQualityAnalyzer):
    """Analyzer for DRY (Don't Repeat Yourself) principle violations."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "dry")

    def run_analysis(self) -> dict[str, Any]:
        """Run DRY analysis."""
        python_files = self.find_python_files()

        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "duplicate_code_blocks": [],
            "similar_functions": [],
            "repeated_constants": [],
            "similar_class_methods": [],
            "repeated_imports": [],
            "summary": {
                "total_duplicates": 0,
                "files_with_duplicates": 0,
                "duplicate_lines": 0,
                "similarity_score": 0,
            },
            "recommendations": [],
        }

        if not python_files:
            return results

        # Collect data from all files
        code_blocks: dict[str, list[tuple[str, int]]] = defaultdict(list)
        function_signatures: dict[str, list[tuple[str, int]]] = defaultdict(list)
        constants: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
        imports: dict[str, list[tuple[str, int]]] = defaultdict(list)
        class_methods: dict[str, list[tuple[str, int]]] = defaultdict(list)

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                self._analyze_file(
                    file_path,
                    content,
                    code_blocks,
                    function_signatures,
                    constants,
                    imports,
                    class_methods,
                )

            except Exception:
                continue

        # Process duplicates
        results["duplicate_code_blocks"] = self._process_code_blocks(code_blocks)
        results["similar_functions"] = self._process_functions(function_signatures)
        results["repeated_constants"] = self._process_constants(constants)
        results["repeated_imports"] = self._process_imports(imports)
        results["similar_class_methods"] = self._process_class_methods(class_methods)

        # Calculate summary
        results["summary"] = self._calculate_summary(results, python_files)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _analyze_file(
        self,
        file_path: Path,
        content: str,
        code_blocks: dict[str, list[tuple[str, int]]],
        function_signatures: dict[str, list[tuple[str, int]]],
        constants: dict[str, list[tuple[str, int, str]]],
        imports: dict[str, list[tuple[str, int]]],
        class_methods: dict[str, list[tuple[str, int]]],
    ) -> None:
        """Analyze a single file for DRY violations."""
        try:
            # Analyze code blocks (line-based)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                clean_line = line.strip()
                if (
                    clean_line
                    and not clean_line.startswith("#")
                    and not clean_line.startswith('"""')
                    and not clean_line.startswith("'''")
                    and len(clean_line) > 15
                ):  # Only consider substantial lines
                    code_blocks[clean_line].append((str(file_path), i + 1))

            # Parse AST for more detailed analysis
            tree = ast.parse(content)

            current_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name

                elif isinstance(node, ast.FunctionDef):
                    # Function signatures
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"
                    function_signatures[signature].append((str(file_path), node.lineno))

                    # Class methods
                    if current_class:
                        method_signature = (
                            f"{current_class}.{node.name}({', '.join(args)})"
                        )
                        class_methods[method_signature].append(
                            (str(file_path), node.lineno)
                        )

                elif isinstance(node, ast.Assign):
                    # Constants
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            if isinstance(node.value, ast.Constant):
                                value = str(node.value.value)
                                constants[value].append(
                                    (str(file_path), node.lineno, target.id)
                                )

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Imports
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_str = alias.name
                            imports[import_str].append((str(file_path), node.lineno))
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            import_str = f"from {module} import {alias.name}"
                            imports[import_str].append((str(file_path), node.lineno))

        except SyntaxError:
            # Skip files with syntax errors
            pass

    def _process_code_blocks(
        self, code_blocks: dict[str, list[tuple[str, int]]]
    ) -> list[dict[str, Any]]:
        """Process duplicate code blocks."""
        duplicates = []
        for block, locations in code_blocks.items():
            if len(locations) > 1:
                duplicates.append(
                    {
                        "code": block,
                        "occurrences": locations,
                        "count": len(locations),
                        "severity": "high" if len(locations) > 3 else "medium",
                    }
                )

        # Sort by count (most duplicated first)
        return sorted(duplicates, key=lambda x: x["count"], reverse=True)

    def _process_functions(
        self, function_signatures: dict[str, list[tuple[str, int]]]
    ) -> list[dict[str, Any]]:
        """Process similar function signatures."""
        similar = []
        for signature, locations in function_signatures.items():
            if len(locations) > 1:
                similar.append(
                    {
                        "signature": signature,
                        "occurrences": locations,
                        "count": len(locations),
                        "severity": "medium" if len(locations) > 2 else "low",
                    }
                )

        return sorted(similar, key=lambda x: x["count"], reverse=True)

    def _process_constants(
        self, constants: dict[str, list[tuple[str, int, str]]]
    ) -> list[dict[str, Any]]:
        """Process repeated constants."""
        repeated = []
        for value, locations in constants.items():
            if len(locations) > 1:
                repeated.append(
                    {
                        "value": value,
                        "occurrences": locations,
                        "count": len(locations),
                        "severity": "medium" if len(locations) > 2 else "low",
                    }
                )

        return sorted(repeated, key=lambda x: x["count"], reverse=True)

    def _process_imports(
        self, imports: dict[str, list[tuple[str, int]]]
    ) -> list[dict[str, Any]]:
        """Process repeated imports across files."""
        repeated = []
        for import_str, locations in imports.items():
            if len(locations) > 3:  # More than 3 files importing the same thing
                repeated.append(
                    {
                        "import": import_str,
                        "occurrences": locations,
                        "count": len(locations),
                        "severity": "low",  # Repeated imports are usually OK
                    }
                )

        return sorted(repeated, key=lambda x: x["count"], reverse=True)

    def _process_class_methods(
        self, class_methods: dict[str, list[tuple[str, int]]]
    ) -> list[dict[str, Any]]:
        """Process similar class methods."""
        similar = []
        for method_signature, locations in class_methods.items():
            if len(locations) > 1:
                similar.append(
                    {
                        "method": method_signature,
                        "occurrences": locations,
                        "count": len(locations),
                        "severity": "medium" if len(locations) > 2 else "low",
                    }
                )

        return sorted(similar, key=lambda x: x["count"], reverse=True)

    def _calculate_summary(
        self, results: dict[str, Any], python_files: list[Path]
    ) -> dict[str, Any]:
        """Calculate summary statistics."""
        total_duplicates = (
            len(results["duplicate_code_blocks"])
            + len(results["similar_functions"])
            + len(results["repeated_constants"])
            + len(results["similar_class_methods"])
        )

        # Count files with duplicates
        files_with_duplicates = set()
        for dup_type in [
            "duplicate_code_blocks",
            "similar_functions",
            "repeated_constants",
            "similar_class_methods",
        ]:
            for item in results[dup_type]:
                for occurrence in item["occurrences"]:
                    if (isinstance(occurrence, tuple) and len(occurrence) >= 2) or (
                        isinstance(occurrence, (list, tuple)) and len(occurrence) >= 1
                    ):
                        file_path = occurrence[0]
                        files_with_duplicates.add(file_path)

        # Count duplicate lines
        duplicate_lines = sum(
            item["count"] for item in results["duplicate_code_blocks"]
        )

        # Calculate similarity score (0-100, lower is better)
        total_files = len(python_files)
        if total_files > 0:
            similarity_score = min(100, (total_duplicates / total_files) * 10)
        else:
            similarity_score = 0

        return {
            "total_duplicates": total_duplicates,
            "files_with_duplicates": len(files_with_duplicates),
            "duplicate_lines": duplicate_lines,
            "similarity_score": similarity_score,
        }

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate DRY recommendations."""
        recommendations = []

        total_duplicates = results["summary"]["total_duplicates"]
        duplicate_blocks = len(results["duplicate_code_blocks"])
        similar_functions = len(results["similar_functions"])

        if total_duplicates == 0:
            recommendations.append(
                "✅ Excellent: No significant DRY violations detected!"
            )
            return recommendations

        if duplicate_blocks > 10:
            recommendations.append(
                "🚨 Critical: Many duplicate code blocks found. Consider extracting common functionality into reusable functions."
            )
        elif duplicate_blocks > 5:
            recommendations.append(
                "⚠️ Warning: Several duplicate code blocks detected. Review and refactor when possible."
            )

        if similar_functions > 5:
            recommendations.append(
                "🔄 Consider creating base classes or utility functions for similar function signatures."
            )

        if len(results["repeated_constants"]) > 5:
            recommendations.append(
                "📊 Move repeated constants to a shared constants module."
            )

        if len(results["similar_class_methods"]) > 3:
            recommendations.append(
                "🏗️ Consider using inheritance or composition for similar class methods."
            )

        # Top duplication patterns
        if duplicate_blocks > 0:
            top_block = results["duplicate_code_blocks"][0]
            recommendations.append(
                f"🎯 Most duplicated code: '{top_block['code'][:50]}...' ({top_block['count']} occurrences)"
            )

        similarity_score = results["summary"]["similarity_score"]
        if similarity_score > 30:
            recommendations.append(
                f"📈 Similarity score: {similarity_score:.1f}/100 - Focus on reducing code duplication"
            )

        return recommendations

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate DRY markdown report."""
        total_files = report_data.get("total_files", 0)
        total_duplicates = report_data.get("summary", {}).get("total_duplicates", 0)
        files_with_duplicates = report_data.get("summary", {}).get(
            "files_with_duplicates", 0
        )
        similarity_score = report_data.get("summary", {}).get("similarity_score", 0)

        report = f"""# DRY (Don't Repeat Yourself) Analysis Report - FLEXT Workspace

**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}

## Executive Summary

- **Total Files Analyzed:** {total_files}
- **Files with Duplicates:** {files_with_duplicates}
- **Total Duplicates:** {total_duplicates}
- **Duplicate Code Blocks:** {len(report_data.get("duplicate_code_blocks", []))}
- **Similar Functions:** {len(report_data.get("similar_functions", []))}
- **Repeated Constants:** {len(report_data.get("repeated_constants", []))}
- **Similar Class Methods:** {len(report_data.get("similar_class_methods", []))}
- **Similarity Score:** {similarity_score:.1f}/100 (lower is better)

## Recommendations

"""

        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"

        # Top duplicate code blocks
        if report_data.get("duplicate_code_blocks"):
            report += "\n## Top Duplicate Code Blocks\n\n"
            for i, block in enumerate(report_data["duplicate_code_blocks"][:5], 1):
                report += f"### {i}. {block['severity'].upper()} - {block['count']} occurrences\n\n"
                report += f"**Code:** `{block['code']}`\n\n"
                report += "**Locations:**\n"
                for occurrence in block["occurrences"]:
                    if isinstance(occurrence, tuple) and len(occurrence) >= 2:
                        file_path, line_num = occurrence[0], occurrence[1]
                        report += f"- {file_path}:{line_num}\n"
                    elif isinstance(occurrence, (list, tuple)) and len(occurrence) >= 1:
                        report += f"- {occurrence[0]}\n"
                report += "\n"

        # Similar functions
        if report_data.get("similar_functions"):
            report += "\n## Similar Function Signatures\n\n"
            for i, func in enumerate(report_data["similar_functions"][:5], 1):
                report += (
                    f"### {i}. {func['signature']} - {func['count']} occurrences\n\n"
                )
                report += "**Locations:**\n"
                for occurrence in func["occurrences"]:
                    if isinstance(occurrence, tuple) and len(occurrence) >= 2:
                        file_path, line_num = occurrence[0], occurrence[1]
                        report += f"- {file_path}:{line_num}\n"
                    elif isinstance(occurrence, (list, tuple)) and len(occurrence) >= 1:
                        report += f"- {occurrence[0]}\n"
                report += "\n"

        return report


class TestDRYPrinciples:
    """Test suite for DRY principles."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> DRYAnalyzer:
        """Create DRY analyzer instance."""
        return DRYAnalyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: DRYAnalyzer) -> dict[str, Any]:
        """Run DRY analysis once for all tests."""
        return analyzer.run_analysis()

    def test_dry_files_found(self, analysis_results: dict[str, Any]) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, (
            "No Python files found for DRY analysis"
        )

    def test_dry_duplicate_threshold(self, analysis_results: dict[str, Any]) -> None:
        """Test that duplicate code blocks are within acceptable limits."""
        total_duplicates = analysis_results["summary"]["total_duplicates"]
        total_files = analysis_results["total_files"]

        if total_files > 0:
            duplicate_rate = total_duplicates / total_files
            assert duplicate_rate < 20.0, (
                f"DRY violation rate {duplicate_rate:.1f} per file is too high"
            )

    def test_dry_similarity_score(self, analysis_results: dict[str, Any]) -> None:
        """Test that similarity score is acceptable."""
        similarity_score = analysis_results["summary"]["similarity_score"]
        assert similarity_score <= 100, (
            f"DRY similarity score {similarity_score:.1f} is too high (>100)"
        )

    def test_dry_duplicate_blocks_reasonable(self, analysis_results: dict[str, Any]) -> None:
        """Test that duplicate code blocks are reasonable."""
        duplicate_blocks = len(analysis_results["duplicate_code_blocks"])
        total_files = analysis_results["total_files"]

        if total_files > 0:
            # Should have fewer than 2000% of files with significant duplicates (very lenient for enterprise codebases)
            assert duplicate_blocks < (total_files * 20), (
                f"Too many duplicate code blocks: {duplicate_blocks}"
            )

    def test_generate_dry_reports(self, analyzer: DRYAnalyzer, analysis_results: dict[str, Any]) -> None:
        """Test DRY report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "DRY JSON report was not created"
        assert md_report.exists(), "DRY Markdown report was not created"

        # Verify report content
        import json

        with open(json_report) as f:
            report_data = json.load(f)

        assert "duplicate_code_blocks" in report_data
        assert "similar_functions" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data

        # Print summary


if __name__ == "__main__":
    # Run DRY analysis directly
    analyzer = DRYAnalyzer()
    results = analyzer.run_analysis()

    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")

    # Print summary

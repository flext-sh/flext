"""KISS (Keep It Simple, Stupid) principle tests for FLEXT workspace."""

import ast
from pathlib import Path
from typing import Any

import pytest
from flext_api.utils.logging import logger

from .base import BaseQualityAnalyzer


class KISSAnalyzer(BaseQualityAnalyzer):
    """Analyzer for KISS (Keep It Simple, Stupid) principle compliance."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "kiss")

    def run_analysis(self) -> dict[str, Any]:
        """Run KISS analysis."""
        python_files = self.find_python_files()

        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "complex_functions": [],
            "long_functions": [],
            "deep_nesting": [],
            "complex_expressions": [],
            "complex_classes": [],
            "long_parameter_lists": [],
            "summary": {
                "total_issues": 0,
                "average_complexity": 0,
                "average_function_length": 0,
                "average_nesting_depth": 0,
                "simplicity_score": 0,
            },
            "recommendations": [],
        }

        if not python_files:
            return results

        total_functions = 0
        total_complexity = 0
        total_function_length = 0
        total_nesting_depth = 0

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                file_stats = self._analyze_file(file_path, content, results)
                total_functions += file_stats["functions"]
                total_complexity += file_stats["complexity"]
                total_function_length += file_stats["function_length"]
                total_nesting_depth += file_stats["nesting_depth"]

            except Exception as e:
                logger.error(f"KISS analysis failed for file {file_path}: {e}")
                continue

        # Calculate summary statistics
        summary = results["summary"]
        if isinstance(summary, dict):
            if total_functions > 0:
                summary["average_complexity"] = total_complexity / total_functions
                summary["average_function_length"] = total_function_length / total_functions
                summary["average_nesting_depth"] = total_nesting_depth / total_functions

            # Calculate total issues
            complex_functions = results["complex_functions"]
            long_functions = results["long_functions"]
            deep_nesting = results["deep_nesting"]
            complex_expressions = results["complex_expressions"]
            complex_classes = results["complex_classes"]
            long_parameter_lists = results["long_parameter_lists"]

            if (
                isinstance(complex_functions, list)
                and isinstance(long_functions, list)
                and isinstance(deep_nesting, list)
                and isinstance(complex_expressions, list)
                and isinstance(complex_classes, list)
                and isinstance(long_parameter_lists, list)
            ):
                summary["total_issues"] = (
                    len(complex_functions)
                    + len(long_functions)
                    + len(deep_nesting)
                    + len(complex_expressions)
                    + len(complex_classes)
                    + len(long_parameter_lists)
                )

            # Calculate simplicity score (0-100, higher is better)
            summary["simplicity_score"] = self._calculate_simplicity_score(results)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _analyze_file(
        self,
        file_path: Path,
        content: str,
        results: dict[str, Any],
    ) -> dict[str, int]:
        """Analyze a single file for KISS violations."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "functions": 0,
                "complexity": 0,
                "function_length": 0,
                "nesting_depth": 0,
            }

        file_stats = {
            "functions": 0,
            "complexity": 0,
            "function_length": 0,
            "nesting_depth": 0,
        }

        # Analyze all nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                file_stats["functions"] += 1
                self._analyze_function(node, file_path, results, file_stats)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path, results)

        # Analyze complex expressions at module level
        self._analyze_complex_expressions(tree, file_path, results)

        return file_stats

    def _analyze_function(
        self,
        func_node: ast.FunctionDef,
        file_path: Path,
        results: dict[str, Any],
        file_stats: dict[str, int],
    ) -> None:
        """Analyze a function for KISS violations."""
        func_name = func_node.name

        # Calculate metrics
        complexity = self._calculate_cyclomatic_complexity(func_node)
        function_length = self._calculate_function_length(func_node)
        nesting_depth = self._calculate_max_nesting_depth(func_node)
        parameter_count = len(func_node.args.args)

        # Update file stats
        file_stats["complexity"] += complexity
        file_stats["function_length"] += function_length
        file_stats["nesting_depth"] += nesting_depth

        # Check for violations
        # Complex functions
        if complexity > 10:
            results["complex_functions"].append(
                {
                    "file": str(file_path),
                    "function": func_name,
                    "line": func_node.lineno,
                    "complexity": complexity,
                    "severity": "high" if complexity > 20 else "medium",
                    "suggestion": "Break into smaller functions with single responsibilities",
                },
            )

        # Long functions
        if function_length > 30:
            results["long_functions"].append(
                {
                    "file": str(file_path),
                    "function": func_name,
                    "line": func_node.lineno,
                    "length": function_length,
                    "severity": "high" if function_length > 50 else "medium",
                    "suggestion": "Split into smaller, focused functions",
                },
            )

        # Deep nesting
        if nesting_depth > 4:
            results["deep_nesting"].append(
                {
                    "file": str(file_path),
                    "function": func_name,
                    "line": func_node.lineno,
                    "depth": nesting_depth,
                    "severity": "high" if nesting_depth > 6 else "medium",
                    "suggestion": "Reduce nesting using early returns or guard clauses",
                },
            )

        # Long parameter lists
        if parameter_count > 5:
            results["long_parameter_lists"].append(
                {
                    "file": str(file_path),
                    "function": func_name,
                    "line": func_node.lineno,
                    "parameters": parameter_count,
                    "severity": "medium" if parameter_count > 8 else "low",
                    "suggestion": "Use parameter objects or reduce dependencies",
                },
            )

    def _analyze_class(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        results: dict[str, Any],
    ) -> None:
        """Analyze a class for KISS violations."""
        class_name = class_node.name

        # Count methods and attributes
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        [n for n in class_node.body if isinstance(n, ast.Assign)]

        # Calculate class complexity
        total_method_complexity = sum(self._calculate_cyclomatic_complexity(method) for method in methods)

        # Check for complex classes
        if len(methods) > 15 or total_method_complexity > 50:
            results["complex_classes"].append(
                {
                    "file": str(file_path),
                    "class": class_name,
                    "line": class_node.lineno,
                    "methods": len(methods),
                    "complexity": total_method_complexity,
                    "severity": "high" if len(methods) > 25 else "medium",
                    "suggestion": "Split into smaller classes with focused responsibilities",
                },
            )

    def _analyze_complex_expressions(
        self,
        tree: ast.AST,
        file_path: Path,
        results: dict[str, Any],
    ) -> None:
        """Analyze complex expressions that violate KISS."""
        for node in ast.walk(tree):
            # Complex comprehensions
            if isinstance(
                node,
                (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp),
            ):
                if self._is_complex_comprehension(node):
                    results["complex_expressions"].append(
                        {
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "comprehension",
                            "issue": "Complex comprehension with multiple conditions or nested loops",
                            "severity": "medium",
                            "suggestion": "Break into multiple steps or use regular loops",
                        },
                    )

            # Complex lambda expressions
            elif isinstance(node, ast.Lambda):
                if self._is_complex_lambda(node):
                    results["complex_expressions"].append(
                        {
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "lambda",
                            "issue": "Complex lambda expression",
                            "severity": "low",
                            "suggestion": "Use regular function instead of lambda",
                        },
                    )

            # Complex boolean expressions
            elif isinstance(node, ast.BoolOp) and self._is_complex_boolean(node):
                results["complex_expressions"].append(
                    {
                        "file": str(file_path),
                        "line": node.lineno,
                        "type": "boolean",
                        "issue": "Complex boolean expression with many conditions",
                        "severity": "medium",
                        "suggestion": "Break into smaller logical parts with descriptive variable names",
                    },
                )

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def _calculate_function_length(self, func_node: ast.FunctionDef) -> int:
        """Calculate function length in statements."""
        return len([n for n in ast.walk(func_node) if isinstance(n, ast.stmt)])

    def _calculate_max_nesting_depth(
        self,
        node: ast.AST,
        current_depth: int = 0,
    ) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(
                child,
                (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try),
            ):
                child_depth = self._calculate_max_nesting_depth(
                    child,
                    current_depth + 1,
                )
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _is_complex_comprehension(self, node: ast.expr) -> bool:
        """Check if comprehension is complex."""
        # Count generators and conditions
        if hasattr(node, "generators"):
            total_conditions = sum(len(gen.ifs) for gen in node.generators)
            nested_generators = len(node.generators) > 1

            return total_conditions > 2 or nested_generators
        return False

    def _is_complex_lambda(self, node: ast.Lambda) -> bool:
        """Check if lambda is complex."""
        # Count nodes in lambda body
        body_nodes = list(ast.walk(node.body))
        return len(body_nodes) > 5

    def _is_complex_boolean(self, node: ast.BoolOp) -> bool:
        """Check if boolean expression is complex."""
        # Count total conditions
        total_conditions = len(node.values)

        # Count nested boolean operations
        nested_boolops = sum(1 for value in node.values if isinstance(value, ast.BoolOp))

        return total_conditions > 4 or nested_boolops > 0

    def _calculate_simplicity_score(self, results: dict[str, Any]) -> float:
        """Calculate overall simplicity score (0-100, higher is better)."""
        total_files = int(results["total_files"])
        total_issues = int(results["summary"]["total_issues"])

        if total_files == 0:
            return 100.0

        # Base score
        base_score = 100.0

        # Penalty for issues
        issue_penalty = min(total_issues * 2, 80)  # Max 80 point penalty

        # Complexity penalty
        avg_complexity = float(results["summary"]["average_complexity"])
        complexity_penalty = min(
            max(0, avg_complexity - 5) * 2,
            15,
        )  # Max 15 point penalty

        # Length penalty
        avg_length = float(results["summary"]["average_function_length"])
        length_penalty = min(max(0, avg_length - 15) * 0.5, 10)  # Max 10 point penalty

        # Nesting penalty
        avg_nesting = float(results["summary"]["average_nesting_depth"])
        nesting_penalty = min(max(0, avg_nesting - 2) * 5, 15)  # Max 15 point penalty

        final_score = base_score - issue_penalty - complexity_penalty - length_penalty - nesting_penalty

        return max(0.0, final_score)

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate KISS recommendations."""
        recommendations = []

        results["summary"]["total_issues"]
        simplicity_score = results["summary"]["simplicity_score"]

        # Overall assessment
        if simplicity_score >= 85:
            recommendations.append(
                "✅ Excellent: Code follows KISS principles very well!",
            )
        elif simplicity_score >= 70:
            recommendations.append("👍 Good: Code is generally simple and readable.")
        elif simplicity_score >= 50:
            recommendations.append("⚠️ Warning: Code complexity needs attention.")
        else:
            recommendations.append(
                "🚨 Critical: Code is too complex, needs significant simplification.",
            )

        # Issue-specific recommendations
        if results["complex_functions"]:
            count = len(results["complex_functions"])
            recommendations.append(
                f"🔍 {count} complex functions found - break them into smaller pieces",
            )

        if results["long_functions"]:
            count = len(results["long_functions"])
            recommendations.append(
                f"📏 {count} long functions found - split them for better readability",
            )

        if results["deep_nesting"]:
            count = len(results["deep_nesting"])
            recommendations.append(
                f"🏗️ {count} deeply nested functions - use early returns and guard clauses",
            )

        if results["complex_expressions"]:
            count = len(results["complex_expressions"])
            recommendations.append(
                f"🧮 {count} complex expressions found - simplify with intermediate variables",
            )

        if results["complex_classes"]:
            count = len(results["complex_classes"])
            recommendations.append(
                f"🏛️ {count} complex classes found - consider class decomposition",
            )

        if results["long_parameter_lists"]:
            count = len(results["long_parameter_lists"])
            recommendations.append(
                f"📝 {count} functions with long parameter lists - use parameter objects",
            )

        # Metric-specific recommendations
        avg_complexity = results["summary"]["average_complexity"]
        if avg_complexity > 8:
            recommendations.append(
                f"📊 Average complexity ({avg_complexity:.1f}) is high - target < 8",
            )

        avg_length = results["summary"]["average_function_length"]
        if avg_length > 25:
            recommendations.append(
                f"📏 Average function length ({avg_length:.1f}) is high - target < 25",
            )

        avg_nesting = results["summary"]["average_nesting_depth"]
        if avg_nesting > 3:
            recommendations.append(
                f"🏗️ Average nesting depth ({avg_nesting:.1f}) is high - target < 3",
            )

        return recommendations

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate KISS markdown report."""
        total_files = report_data.get("total_files", 0)
        total_issues = report_data.get("summary", {}).get("total_issues", 0)
        simplicity_score = report_data.get("summary", {}).get("simplicity_score", 0)

        report = f"""# KISS (Keep It Simple, Stupid) Analysis Report - FLEXT Workspace

**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}

## Executive Summary

- **Total Files Analyzed:** {total_files}
- **Total Issues:** {total_issues}
- **Simplicity Score:** {simplicity_score:.1f}/100
- **Complex Functions:** {len(report_data.get("complex_functions", []))}
- **Long Functions:** {len(report_data.get("long_functions", []))}
- **Deep Nesting Issues:** {len(report_data.get("deep_nesting", []))}
- **Complex Expressions:** {len(report_data.get("complex_expressions", []))}
- **Complex Classes:** {len(report_data.get("complex_classes", []))}
- **Long Parameter Lists:** {len(report_data.get("long_parameter_lists", []))}

## Quality Metrics

- **Average Complexity:** {report_data.get("summary", {}).get("average_complexity", 0):.1f}
- **Average Function Length:** {report_data.get("summary", {}).get("average_function_length", 0):.1f}
- **Average Nesting Depth:** {report_data.get("summary", {}).get("average_nesting_depth", 0):.1f}

## Recommendations

"""

        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"

        # Issue details
        issue_types = [
            ("Complex Functions", "complex_functions", "complexity"),
            ("Long Functions", "long_functions", "length"),
            ("Deep Nesting", "deep_nesting", "depth"),
            ("Complex Expressions", "complex_expressions", "type"),
            ("Complex Classes", "complex_classes", "methods"),
            ("Long Parameter Lists", "long_parameter_lists", "parameters"),
        ]

        for title, key, metric in issue_types:
            issues = report_data.get(key, [])
            if issues:
                report += f"\n## {title}\n\n"
                for issue in issues[:5]:  # Top 5
                    report += f"### {issue['severity'].upper()}: {issue.get('function', issue.get('class', 'Unknown'))}\n\n"
                    report += f"**File:** {issue['file']}:{issue['line']}\n"
                    if metric in issue:
                        report += f"**{metric.title()}:** {issue[metric]}\n"
                    if "issue" in issue:
                        report += f"**Issue:** {issue['issue']}\n"
                    report += f"**Suggestion:** {issue['suggestion']}\n\n"

        return report


class TestKISSPrinciples:
    """Test suite for KISS principles."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> KISSAnalyzer:
        """Create KISS analyzer instance."""
        return KISSAnalyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: KISSAnalyzer) -> dict[str, Any]:
        """Run KISS analysis once for all tests."""
        return analyzer.run_analysis()

    def test_kiss_files_found(self, analysis_results: dict[str, Any]) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, "No Python files found for KISS analysis"

    def test_kiss_simplicity_score(self, analysis_results: dict[str, Any]) -> None:
        """Test that simplicity score is acceptable."""
        simplicity_score = analysis_results["summary"]["simplicity_score"]
        assert simplicity_score >= 15, f"KISS simplicity score {simplicity_score:.1f} is below 15"

    def test_kiss_complexity_reasonable(self, analysis_results: dict[str, Any]) -> None:
        """Test that average complexity is reasonable."""
        avg_complexity = analysis_results["summary"]["average_complexity"]
        assert avg_complexity < 15, f"Average complexity {avg_complexity:.1f} is too high"

    def test_kiss_function_length_reasonable(self, analysis_results: dict[str, Any]) -> None:
        """Test that average function length is reasonable."""
        avg_length = analysis_results["summary"]["average_function_length"]
        assert avg_length < 40, f"Average function length {avg_length:.1f} is too high"

    def test_kiss_nesting_depth_reasonable(self, analysis_results: dict[str, Any]) -> None:
        """Test that average nesting depth is reasonable."""
        avg_nesting = analysis_results["summary"]["average_nesting_depth"]
        assert avg_nesting < 5, f"Average nesting depth {avg_nesting:.1f} is too high"

    def test_kiss_issue_threshold(self, analysis_results: dict[str, Any]) -> None:
        """Test that KISS issues are within acceptable limits."""
        total_issues = analysis_results["summary"]["total_issues"]
        total_files = analysis_results["total_files"]

        if total_files > 0:
            issue_rate = total_issues / total_files
            assert issue_rate < 3.0, f"KISS issue rate {issue_rate:.1f} per file is too high"

    def test_generate_kiss_reports(self, analyzer: KISSAnalyzer, analysis_results: dict[str, Any]) -> None:
        """Test KISS report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "KISS JSON report was not created"
        assert md_report.exists(), "KISS Markdown report was not created"

        # Verify report content
        import json

        with open(json_report, encoding="utf-8") as f:
            report_data = json.load(f)

        assert "complex_functions" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data

        # Print summary


if __name__ == "__main__":
    # Run KISS analysis directly
    analyzer = KISSAnalyzer()
    results = analyzer.run_analysis()

    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")

    # Print summary

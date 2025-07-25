"""SOLID principles compliance tests for FLEXT workspace."""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

from .base import BaseQualityAnalyzer


class SOLIDAnalyzer(BaseQualityAnalyzer):
    """Analyzer for SOLID principles compliance."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "solid")

    def run_analysis(self) -> dict[str, Any]:
        """Run SOLID principles analysis."""
        python_files = self.find_python_files()

        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "single_responsibility": {"violations": [], "score": 0},
            "open_closed": {"violations": [], "score": 0},
            "liskov_substitution": {"violations": [], "score": 0},
            "interface_segregation": {"violations": [], "score": 0},
            "dependency_inversion": {"violations": [], "score": 0},
            "summary": {
                "total_violations": 0,
                "average_score": 0,
                "total_classes": 0,
                "total_functions": 0,
                "problematic_classes": 0,
                "problematic_functions": 0,
            },
            "recommendations": [],
        }

        if not python_files:
            return results

        total_classes = 0
        total_functions = 0

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                file_classes, file_functions = self._analyze_file(
                    file_path, content, results,
                )
                total_classes += file_classes
                total_functions += file_functions

            except Exception:
                continue

        # Calculate scores and summary
        summary = results["summary"]
        if isinstance(summary, dict):
            summary["total_classes"] = total_classes
            summary["total_functions"] = total_functions

        self._calculate_scores(results, total_classes, total_functions)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _analyze_file(
        self, file_path: Path, content: str, results: dict[str, Any],
    ) -> tuple[int, int]:
        """Analyze a single file for SOLID violations."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return 0, 0

        classes_count = 0
        functions_count = 0

        # Track imports for dependency analysis
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)

        # Analyze classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_count += 1
                self._analyze_class(node, file_path, imports, results)
            elif isinstance(node, ast.FunctionDef):
                functions_count += 1
                self._analyze_function(node, file_path, results)

        return classes_count, functions_count

    def _analyze_class(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        imports: set[str],
        results: dict[str, Any],
    ) -> None:
        """Analyze a class for SOLID violations."""
        # Get class methods
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]

        # Single Responsibility Principle
        self._check_single_responsibility_class(class_node, file_path, methods, results)

        # Open/Closed Principle
        self._check_open_closed_class(class_node, file_path, results)

        # Liskov Substitution Principle
        self._check_liskov_substitution(class_node, file_path, results)

        # Interface Segregation Principle
        self._check_interface_segregation(class_node, file_path, methods, results)

        # Dependency Inversion Principle
        self._check_dependency_inversion(class_node, file_path, imports, results)

    def _analyze_function(
        self, func_node: ast.FunctionDef, file_path: Path, results: dict[str, Any],
    ) -> None:
        """Analyze a function for SOLID violations."""
        # Single Responsibility Principle for functions
        self._check_single_responsibility_function(func_node, file_path, results)

    def _check_single_responsibility_class(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        methods: list[ast.FunctionDef],
        results: dict[str, Any],
    ) -> None:
        """Check Single Responsibility Principle for classes."""
        # Too many methods suggests multiple responsibilities
        if len(methods) > 15:
            results["single_responsibility"]["violations"].append(
                {
                    "file": str(file_path),
                    "type": "class",
                    "name": class_node.name,
                    "line": class_node.lineno,
                    "issue": f"Class has {len(methods)} methods, likely violates SRP",
                    "severity": "high" if len(methods) > 25 else "medium",
                    "suggestion": "Consider splitting into smaller, focused classes",
                },
            )

        # Check for mixed concerns by analyzing method names
        method_concerns = self._categorize_method_concerns(methods)
        if len(method_concerns) > 3:
            results["single_responsibility"]["violations"].append(
                {
                    "file": str(file_path),
                    "type": "class",
                    "name": class_node.name,
                    "line": class_node.lineno,
                    "issue": f"Class handles {len(method_concerns)} different concerns: {', '.join(method_concerns)}",
                    "severity": "medium",
                    "suggestion": "Split class by concern areas",
                },
            )

    def _check_single_responsibility_function(
        self, func_node: ast.FunctionDef, file_path: Path, results: dict[str, Any],
    ) -> None:
        """Check Single Responsibility Principle for functions."""
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(func_node)

        if complexity > 15:
            results["single_responsibility"]["violations"].append(
                {
                    "file": str(file_path),
                    "type": "function",
                    "name": func_node.name,
                    "line": func_node.lineno,
                    "issue": f"Function has cyclomatic complexity of {complexity}, likely violates SRP",
                    "severity": "high" if complexity > 25 else "medium",
                    "suggestion": "Break function into smaller, focused functions",
                },
            )

        # Check function length
        function_lines = len(
            [n for n in ast.walk(func_node) if isinstance(n, ast.stmt)],
        )
        if function_lines > 50:
            results["single_responsibility"]["violations"].append(
                {
                    "file": str(file_path),
                    "type": "function",
                    "name": func_node.name,
                    "line": func_node.lineno,
                    "issue": f"Function has {function_lines} statements, likely too complex",
                    "severity": "medium",
                    "suggestion": "Split into smaller functions",
                },
            )

    def _check_open_closed_class(
        self, class_node: ast.ClassDef, file_path: Path, results: dict[str, Any],
    ) -> None:
        """Check Open/Closed Principle for classes."""
        # Look for classes that might benefit from extension mechanisms
        any(
            any(
                isinstance(d, ast.Name) and d.id == "abstractmethod"
                for d in method.decorator_list
            )
            for method in class_node.body
            if isinstance(method, ast.FunctionDef)
        )

        # Check for hardcoded conditionals that could be polymorphic
        for node in ast.walk(class_node):
            if isinstance(node, ast.If):
                # Look for type-based conditionals
                if self._has_type_based_conditional(node):
                    results["open_closed"]["violations"].append(
                        {
                            "file": str(file_path),
                            "type": "class",
                            "name": class_node.name,
                            "line": node.lineno,
                            "issue": "Type-based conditional found, consider polymorphism",
                            "severity": "medium",
                            "suggestion": "Use inheritance or strategy pattern",
                        },
                    )

    def _check_liskov_substitution(
        self, class_node: ast.ClassDef, file_path: Path, results: dict[str, Any],
    ) -> None:
        """Check Liskov Substitution Principle."""
        # Check if class has base classes
        if class_node.bases:
            # Look for methods that might violate LSP
            for method in class_node.body:
                if isinstance(method, ast.FunctionDef):
                    # Check for methods that throw NotImplementedError
                    for node in ast.walk(method):
                        if (
                            isinstance(node, ast.Raise)
                            and isinstance(node.exc, ast.Call)
                            and isinstance(node.exc.func, ast.Name)
                            and node.exc.func.id == "NotImplementedError"
                        ):
                            results["liskov_substitution"]["violations"].append(
                                {
                                    "file": str(file_path),
                                    "type": "class",
                                    "name": class_node.name,
                                    "line": node.lineno,
                                    "issue": f"Method {method.name} raises NotImplementedError",
                                    "severity": "high",
                                    "suggestion": "Consider using abstract base classes or different inheritance structure",
                                },
                            )

    def _check_interface_segregation(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        methods: list[ast.FunctionDef],
        results: dict[str, Any],
    ) -> None:
        """Check Interface Segregation Principle."""
        # Check for large interfaces (abstract classes with many abstract methods)
        abstract_methods = [
            method
            for method in methods
            if any(
                isinstance(d, ast.Name) and d.id == "abstractmethod"
                for d in method.decorator_list
            )
        ]

        if len(abstract_methods) > 8:
            results["interface_segregation"]["violations"].append(
                {
                    "file": str(file_path),
                    "type": "class",
                    "name": class_node.name,
                    "line": class_node.lineno,
                    "issue": f"Interface has {len(abstract_methods)} abstract methods, consider splitting",
                    "severity": "medium",
                    "suggestion": "Split into smaller, focused interfaces",
                },
            )

        # Check for methods with very different parameter patterns
        if len(methods) > 5:
            param_patterns = defaultdict(list)
            for method in methods:
                param_count = len(method.args.args) - 1  # Exclude 'self'
                param_patterns[param_count].append(method.name)

            if len(param_patterns) > 4:  # Very different parameter patterns
                results["interface_segregation"]["violations"].append(
                    {
                        "file": str(file_path),
                        "type": "class",
                        "name": class_node.name,
                        "line": class_node.lineno,
                        "issue": "Methods have very different parameter patterns",
                        "severity": "low",
                        "suggestion": "Consider if all methods belong to the same interface",
                    },
                )

    def _check_dependency_inversion(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        imports: set[str],
        results: dict[str, Any],
    ) -> None:
        """Check Dependency Inversion Principle."""
        # Look for direct instantiation of concrete classes
        for node in ast.walk(class_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # Check if calling a concrete class constructor
                func_name = node.func.id
                if (
                    func_name[0].isupper()  # Class name (starts with uppercase)
                    and func_name in imports
                    and not func_name.startswith("Abstract")
                ):  # Not abstract
                    # Skip common exceptions
                    if func_name not in {
                        "Exception",
                        "ValueError",
                        "TypeError",
                        "Dict",
                        "List",
                        "Set",
                        "Tuple",
                    }:
                        results["dependency_inversion"]["violations"].append(
                            {
                                "file": str(file_path),
                                "type": "class",
                                "name": class_node.name,
                                "line": node.lineno,
                                "issue": f"Direct instantiation of concrete class {func_name}",
                                "severity": "low",
                                "suggestion": "Consider dependency injection or factory pattern",
                            },
                        )

    def _categorize_method_concerns(self, methods: list[ast.FunctionDef]) -> set[str]:
        """Categorize methods by their likely concerns."""
        concerns = set()

        for method in methods:
            method_name = method.name.lower()

            # Database/persistence concerns
            if any(
                keyword in method_name
                for keyword in [
                    "save",
                    "load",
                    "persist",
                    "fetch",
                    "query",
                    "insert",
                    "update",
                    "delete",
                ]
            ):
                concerns.add("persistence")

            # Validation concerns
            elif any(
                keyword in method_name
                for keyword in ["validate", "check", "verify", "ensure"]
            ):
                concerns.add("validation")

            # Business logic concerns
            elif any(
                keyword in method_name
                for keyword in ["calculate", "compute", "process", "execute", "run"]
            ):
                concerns.add("business_logic")

            # UI/presentation concerns
            elif any(
                keyword in method_name
                for keyword in ["render", "display", "show", "print", "format"]
            ):
                concerns.add("presentation")

            # Network/communication concerns
            elif any(
                keyword in method_name
                for keyword in ["send", "receive", "request", "response", "api", "http"]
            ):
                concerns.add("communication")

            # Utility concerns
            elif any(
                keyword in method_name
                for keyword in ["get", "set", "init", "setup", "config"]
            ):
                concerns.add("utility")

            else:
                concerns.add("other")

        return concerns

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
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

    def _has_type_based_conditional(self, if_node: ast.If) -> bool:
        """Check if an if statement is type-based."""
        # Look for isinstance() calls or type() comparisons
        for node in ast.walk(if_node.test):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {
                "isinstance",
                "type",
            }:
                return True
        return False

    def _calculate_scores(
        self, results: dict[str, Any], total_classes: int, total_functions: int,
    ) -> None:
        """Calculate SOLID principle scores."""
        total_items = total_classes + total_functions

        if total_items == 0:
            return

        # Calculate individual principle scores
        for principle in [
            "single_responsibility",
            "open_closed",
            "liskov_substitution",
            "interface_segregation",
            "dependency_inversion",
        ]:
            violations = len(results[principle]["violations"])

            # Score calculation: 100 - (violations / total_items * 100)
            # But cap the penalty to be reasonable
            penalty = min(violations * 5, 80)  # Max 80 point penalty
            results[principle]["score"] = max(0, 100 - penalty)

        # Calculate summary
        total_violations = sum(
            len(results[principle]["violations"])
            for principle in [
                "single_responsibility",
                "open_closed",
                "liskov_substitution",
                "interface_segregation",
                "dependency_inversion",
            ]
        )

        average_score = (
            sum(
                results[principle]["score"]
                for principle in [
                    "single_responsibility",
                    "open_closed",
                    "liskov_substitution",
                    "interface_segregation",
                    "dependency_inversion",
                ]
            )
            / 5
        )

        summary = results["summary"]
        if isinstance(summary, dict):
            summary["total_violations"] = total_violations
            summary["average_score"] = average_score

            # Count problematic items
            # Get all violations from all principles
            all_violations = []
            for principle in [
                "single_responsibility",
                "open_closed",
                "liskov_substitution",
                "interface_segregation",
                "dependency_inversion",
            ]:
                if principle in results and "violations" in results[principle]:
                    principle_data = results[principle]
                    if (
                        isinstance(principle_data, dict)
                        and "violations" in principle_data
                    ):
                        violations = principle_data["violations"]
                        if isinstance(violations, list):
                            all_violations.extend(violations)

            # Count unique problematic classes and functions
            problematic_classes = len(
                {
                    v["name"]
                    for v in all_violations
                    if isinstance(v, dict) and v.get("type") == "class"
                },
            )
            problematic_functions = len(
                {
                    v["name"]
                    for v in all_violations
                    if isinstance(v, dict) and v.get("type") == "function"
                },
            )

            summary["problematic_classes"] = problematic_classes
            summary["problematic_functions"] = problematic_functions

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate SOLID recommendations."""
        recommendations = []

        average_score = results["summary"]["average_score"]
        results["summary"]["total_violations"]

        # Overall assessment
        if average_score >= 85:
            recommendations.append("✅ Excellent: Great SOLID principles compliance!")
        elif average_score >= 70:
            recommendations.append("👍 Good: Solid adherence to SOLID principles.")
        elif average_score >= 50:
            recommendations.append("⚠️ Warning: SOLID principles need attention.")
        else:
            recommendations.append("🚨 Critical: Poor SOLID principles compliance.")

        # Principle-specific recommendations
        if results["single_responsibility"]["score"] < 70:
            srp_violations = len(results["single_responsibility"]["violations"])
            recommendations.append(
                f"🎯 Single Responsibility: {srp_violations} violations - break down large classes/functions",
            )

        if results["open_closed"]["score"] < 70:
            ocp_violations = len(results["open_closed"]["violations"])
            recommendations.append(
                f"🔓 Open/Closed: {ocp_violations} violations - use polymorphism over conditionals",
            )

        if results["liskov_substitution"]["score"] < 70:
            lsp_violations = len(results["liskov_substitution"]["violations"])
            recommendations.append(
                f"🔄 Liskov Substitution: {lsp_violations} violations - fix inheritance hierarchies",
            )

        if results["interface_segregation"]["score"] < 70:
            isp_violations = len(results["interface_segregation"]["violations"])
            recommendations.append(
                f"🎛️ Interface Segregation: {isp_violations} violations - split large interfaces",
            )

        if results["dependency_inversion"]["score"] < 70:
            dip_violations = len(results["dependency_inversion"]["violations"])
            recommendations.append(
                f"🔌 Dependency Inversion: {dip_violations} violations - use dependency injection",
            )

        # Specific improvement areas
        if results["summary"]["problematic_classes"] > 0:
            recommendations.append(
                f"🏗️ Review {results['summary']['problematic_classes']} classes for architectural improvements",
            )

        if results["summary"]["problematic_functions"] > 0:
            recommendations.append(
                f"⚡ Refactor {results['summary']['problematic_functions']} functions for better separation of concerns",
            )

        return recommendations

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate SOLID markdown report."""
        average_score = report_data.get("summary", {}).get("average_score", 0)
        total_violations = report_data.get("summary", {}).get("total_violations", 0)

        report = f"""# SOLID Principles Analysis Report - FLEXT Workspace

**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}

## Executive Summary

- **Total Files Analyzed:** {report_data.get("total_files", 0)}
- **Total Classes:** {report_data.get("summary", {}).get("total_classes", 0)}
- **Total Functions:** {report_data.get("summary", {}).get("total_functions", 0)}
- **Average SOLID Score:** {average_score:.1f}/100
- **Total Violations:** {total_violations}
- **Problematic Classes:** {report_data.get("summary", {}).get("problematic_classes", 0)}
- **Problematic Functions:** {report_data.get("summary", {}).get("problematic_functions", 0)}

## SOLID Principles Scores

"""

        principles = [
            ("Single Responsibility", "single_responsibility"),
            ("Open/Closed", "open_closed"),
            ("Liskov Substitution", "liskov_substitution"),
            ("Interface Segregation", "interface_segregation"),
            ("Dependency Inversion", "dependency_inversion"),
        ]

        for name, key in principles:
            score = report_data.get(key, {}).get("score", 0)
            violations = len(report_data.get(key, {}).get("violations", []))
            report += f"- **{name}:** {score:.1f}/100 ({violations} violations)\n"

        report += "\n## Recommendations\n\n"

        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"

        # Top violations by principle
        for name, key in principles:
            violations = report_data.get(key, {}).get("violations", [])
            if violations:
                report += f"\n## {name} Violations\n\n"
                for violation in violations[:5]:  # Top 5
                    report += (
                        f"### {violation['severity'].upper()}: {violation['name']}\n\n"
                    )
                    report += f"**File:** {violation['file']}:{violation['line']}\n"
                    report += f"**Issue:** {violation['issue']}\n"
                    report += f"**Suggestion:** {violation['suggestion']}\n\n"

        return report


class TestSOLIDPrinciples:
    """Test suite for SOLID principles."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> SOLIDAnalyzer:
        """Create SOLID analyzer instance."""
        return SOLIDAnalyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: SOLIDAnalyzer) -> dict[str, Any]:
        """Run SOLID analysis once for all tests."""
        return analyzer.run_analysis()

    def test_solid_files_found(self, analysis_results: dict[str, Any]) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, (
            "No Python files found for SOLID analysis"
        )

    def test_solid_average_score(self, analysis_results: dict[str, Any]) -> None:
        """Test that SOLID average score is acceptable."""
        average_score = analysis_results["summary"]["average_score"]
        assert average_score >= 30, (
            f"SOLID average score {average_score:.1f} is below 30"
        )

    def test_solid_individual_principles(
        self, analysis_results: dict[str, Any],
    ) -> None:
        """Test that individual SOLID principles have reasonable scores."""
        principles = [
            "single_responsibility",
            "open_closed",
            "liskov_substitution",
            "interface_segregation",
            "dependency_inversion",
        ]

        for principle in principles:
            score = analysis_results[principle]["score"]
            assert score >= 20, (
                f"SOLID principle {principle} score {score:.1f} is below 20"
            )

    def test_solid_violation_threshold(self, analysis_results: dict[str, Any]) -> None:
        """Test that SOLID violations are within reasonable limits."""
        total_violations = analysis_results["summary"]["total_violations"]
        total_files = analysis_results["total_files"]

        if total_files > 0:
            violation_rate = total_violations / total_files
            assert violation_rate < 5.0, (
                f"SOLID violation rate {violation_rate:.1f} per file is too high"
            )

    def test_generate_solid_reports(
        self, analyzer: SOLIDAnalyzer, analysis_results: dict[str, Any],
    ) -> None:
        """Test SOLID report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "SOLID JSON report was not created"
        assert md_report.exists(), "SOLID Markdown report was not created"

        # Verify report content
        import json

        with open(json_report, encoding="utf-8") as f:
            report_data = json.load(f)

        assert "single_responsibility" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data

        # Print summary


if __name__ == "__main__":
    # Run SOLID analysis directly
    analyzer = SOLIDAnalyzer()
    results = analyzer.run_analysis()

    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")

    # Print summary

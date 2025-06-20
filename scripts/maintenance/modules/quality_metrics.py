#!/usr/bin/env python3
"""Quality Metrics Module

Generates comprehensive code quality metrics and monitoring dashboard.
Based on scripts/analysis/code_quality_metrics.py and related analysis scripts.
"""

import ast
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .base import CustomFixModule, Issue


class QualityMetricsModule(CustomFixModule):
    """Module for generating comprehensive code quality metrics."""

    name = "quality_metrics"
    description = "Generates comprehensive code quality metrics and monitoring dashboard"

    # Quality thresholds
    QUALITY_THRESHOLDS = {
        "test_coverage": 85.0,
        "cyclomatic_complexity": 10,
        "maintainability_index": 70.0,
        "duplicate_code": 5.0,
        "technical_debt_ratio": 5.0,
        "code_smells": 50,
        "security_hotspots": 0,
        "bugs": 0,
        "vulnerabilities": 0,
    }

    # File size limits (lines of code)
    FILE_SIZE_LIMITS = {
        "warning": 300,
        "error": 500
    }

    def __init__(self,
                 output_format: str = "console",
                 save_report: bool = False,
                 report_dir: Path = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.output_format = output_format  # console, json, html
        self.save_report = save_report
        self.report_dir = report_dir or Path("reports")
        self.metrics: dict[str, Any] = {}

    def analyze_project_structure(self, project_path: Path) -> dict[str, Any]:
        """Analyze basic project structure metrics."""
        metrics = {
            "total_files": 0,
            "python_files": 0,
            "test_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "average_file_size": 0,
            "largest_files": [],
            "modules": 0,
            "classes": 0,
            "functions": 0,
        }

        python_files = list(project_path.rglob("*.py"))
        metrics["python_files"] = len(python_files)

        # Filter out cache and venv files
        python_files = [
            f for f in python_files
            if not any(part.startswith(".") for part in f.parts)
            and "venv" not in str(f)
            and "__pycache__" not in str(f)
        ]

        file_sizes: list = []
        large_files: list = []

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                file_lines = len(lines)
                metrics["total_lines"] += file_lines
                file_sizes.append(file_lines)

                # Track large files
                if file_lines > self.FILE_SIZE_LIMITS["warning"]:
                    large_files.append({
                        "file": str(py_file.relative_to(project_path)),
                        "lines": file_lines,
                        "severity": "error" if file_lines > self.FILE_SIZE_LIMITS["error"] else "warning"
                    })

                # Count different line types
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        metrics["blank_lines"] += 1
                    elif stripped.startswith("#"):
                        metrics["comment_lines"] += 1
                        metrics["code_lines"] += 1

                # Test file detection
                if "test" in str(py_file).lower():
                    metrics["test_files"] += 1

                # AST analysis for classes and functions
                try:
                    tree = ast.parse(content)
                    metrics["modules"] += 1

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            metrics["classes"] += 1
                        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                            metrics["functions"] += 1

                except SyntaxError:
                    continue

            except Exception:
                continue

        metrics["average_file_size"] = sum(
            file_sizes) / len(file_sizes) if file_sizes else 0
        metrics["largest_files"] = sorted(
            large_files,
            key=lambda x: x["lines"],
            reverse=True)[
            :10]

        return metrics

    def analyze_complexity(self, project_path: Path) -> dict[str, Any]:
        """Analyze code complexity metrics."""
        complexity_metrics = {
            "average_complexity": 0.0,
            "max_complexity": 0,
            "complex_functions": [],
            "total_functions": 0,
        }

        python_files = [
            f for f in project_path.rglob("*.py")
            if not any(part.startswith(".") for part in f.parts)
            and "venv" not in str(f)
        ]

        total_complexity = 0
        function_complexities: list = []

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef |
                                  ast.AsyncFunctionDef):
                        complexity = self._calculate_cyclomatic_complexity(
                            node)
                        complexity_metrics["total_functions"] += 1
                        total_complexity += complexity

                        if complexity > self.QUALITY_THRESHOLDS["cyclomatic_complexity"]:
                            function_complexities.append({
                                "file": str(py_file.relative_to(project_path)),
                                "function": node.name,
                                "complexity": complexity,
                                "line": node.lineno
                            })

            except Exception:
                continue

        if complexity_metrics["total_functions"] > 0:
            complexity_metrics["average_complexity"] = total_complexity / \
                complexity_metrics["total_functions"]

        if function_complexities:
            complexity_metrics["max_complexity"] = max(
                f["complexity"] for f in function_complexities)
            complexity_metrics["complex_functions"] = sorted(
                function_complexities,
                key=lambda x: x["complexity"],
                reverse=True
            )[:20]  # Top 20 most complex functions

        return complexity_metrics

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.While | ast.For | ast.AsyncFor):
                complexity += 1
            elif isinstance(child, ast.And | ast.Or):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1

        return complexity

    def analyze_test_coverage(self, project_path: Path) -> dict[str, Any]:
        """Analyze test coverage metrics."""
        coverage_metrics = {
            "coverage_percentage": 0.0,
            "lines_covered": 0,
            "lines_total": 0,
            "missing_coverage": [],
            "coverage_available": False
        }

        # Try to run coverage analysis
        try:
            # Check if coverage data exists
            coverage_file = project_path / ".coverage"
            if coverage_file.exists():
                result = subprocess.run(
                    ["coverage", "report", "--format=json"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    coverage_data = json.loads(result.stdout)
                    coverage_metrics["coverage_percentage"] = coverage_data.get(
                        "totals", {}).get("percent_covered", 0.0)
                    coverage_metrics["lines_covered"] = coverage_data.get(
                        "totals", {}).get("covered_lines", 0)
                    coverage_metrics["lines_total"] = coverage_data.get(
                        "totals", {}).get("num_statements", 0)
                    coverage_metrics["coverage_available"] = True

                    # Find files with low coverage
                    files = coverage_data.get("files", {})
                    low_coverage: list = []
                    for file_path, file_data in files.items():
                        file_coverage = file_data.get(
                            "summary", {}).get(
                            "percent_covered", 0)
                        if file_coverage < self.QUALITY_THRESHOLDS["test_coverage"]:
                            low_coverage.append({
                                "file": file_path,
                                "coverage": file_coverage,
                                "missing_lines": file_data.get("missing_lines", [])
                            })

                    coverage_metrics["missing_coverage"] = sorted(
                        low_coverage,
                        key=lambda x: x["coverage"]
                    )[:10]

        except Exception:
            pass  # Coverage analysis not available

        return coverage_metrics

    def analyze_code_quality_issues(
            self, project_path: Path) -> dict[str, Any]:
        """Analyze code quality issues using ruff and other tools."""
        quality_issues = {
            "total_issues": 0,
            "errors": 0,
            "warnings": 0,
            "style_issues": 0,
            "security_issues": 0,
            "performance_issues": 0,
            "maintainability_issues": 0,
            "issue_details": [],
            "tools_available": {}
        }

        # Run ruff analysis
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--format=json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                quality_issues["tools_available"]["ruff"] = True

                for issue in ruff_issues:
                    quality_issues["total_issues"] += 1

                    # Categorize issues
                    rule_code = issue.get("code", "")
                    if rule_code.startswith(("E", "W")):
                        quality_issues["style_issues"] += 1
                    elif rule_code.startswith("S"):
                        quality_issues["security_issues"] += 1
                    elif rule_code.startswith("PERF"):
                        quality_issues["performance_issues"] += 1
                        quality_issues["warnings"] += 1

                    quality_issues["issue_details"].append({
                        "file": issue.get("filename", ""),
                        "line": issue.get("location", {}).get("row", 0),
                        "column": issue.get("location", {}).get("column", 0),
                        "code": rule_code,
                        "message": issue.get("message", ""),
                        "severity": "error" if rule_code.startswith("E") else "warning"
                    })

        except Exception:
            quality_issues["tools_available"]["ruff"] = False

        # Run mypy analysis
        try:
            result = subprocess.run(
                ["mypy", ".", "--no-error-summary"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            quality_issues["tools_available"]["mypy"] = True

            if result.stdout:
                mypy_lines = result.stdout.split("\n")
                for line in mypy_lines:
                    if ": error:" in line or ": warning:" in line:
                        quality_issues["total_issues"] += 1
                        if ": error:" in line:
                            quality_issues["errors"] += 1
                            quality_issues["warnings"] += 1

        except Exception:
            quality_issues["tools_available"]["mypy"] = False

        return quality_issues

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze individual files for quality metrics."""
        issues: list = []

        if file_path.suffix == ".py":
            # Check file size
            lines = content.split("\n")
            line_count = len(lines)

            if line_count > self.FILE_SIZE_LIMITS["error"]:
                issues.append(
                    Issue(
                        line=line_count,
                        column=1,
                        code="QUALITY001",
                        message=f"File too large: {line_count} lines (limit: {
                            self.FILE_SIZE_LIMITS['error']})",
                        suggestion="Consider splitting this file into smaller modules"))
            elif line_count > self.FILE_SIZE_LIMITS["warning"]:
                issues.append(
                    Issue(
                        line=line_count,
                        column=1,
                        code="QUALITY002",
                        message=f"File large: {line_count} lines (warning at: {
                            self.FILE_SIZE_LIMITS['warning']})",
                        suggestion="Consider refactoring to reduce file size"))

            # Check for complex functions
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef |
                                  ast.AsyncFunctionDef):
                        complexity = self._calculate_cyclomatic_complexity(
                            node)
                        if complexity > self.QUALITY_THRESHOLDS["cyclomatic_complexity"]:
                            issues.append(
                                Issue(
                                    line=node.lineno,
                                    column=1,
                                    code="QUALITY003",
                                    message=f"Function '{
                                        node.name}' has high complexity: {complexity}",
                                    suggestion="Consider breaking down this function into smaller functions"))

            except SyntaxError:
                issues.append(Issue(
                    line=1,
                    column=1,
                    code="QUALITY004",
                    message="Syntax error in Python file",
                    suggestion="Fix syntax errors before quality analysis"
                ))

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply basic quality fixes (most require manual intervention)."""
        # Most quality issues require manual refactoring
        # This module focuses on detection and reporting
        return content

    def generate_quality_report(
            self, workspace_path: Path = None) -> dict[str, Any]:
        """Generate comprehensive quality report for workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Generating quality metrics for: {workspace_path}[/blue]")

        # Find all projects
        projects: list = []
        for pyproject_file in workspace_path.rglob("pyproject.toml"):
            if not any(part.startswith(".") for part in pyproject_file.parts):
                projects.append(pyproject_file.parent)

        if self.verbose:
            self.console.print(
                f"[green]Analyzing {
                    len(projects)} projects[/green]")

        workspace_metrics = {
            "timestamp": time.time(),
            "workspace_path": str(workspace_path),
            "total_projects": len(projects),
            "projects": {},
            "summary": {
                "total_files": 0,
                "total_lines": 0,
                "total_issues": 0,
                "average_complexity": 0.0,
                "overall_coverage": 0.0,
                "quality_score": 0.0
            }
        }

        total_complexity = 0
        total_coverage = 0
        projects_with_coverage = 0
        total_functions = 0

        for project_path in projects:
            project_name = project_path.name

            if self.verbose:
                self.console.print(
                    f"[yellow]Analyzing {project_name}[/yellow]")

            # Analyze different aspects
            structure_metrics = self.analyze_project_structure(project_path)
            complexity_metrics = self.analyze_complexity(project_path)
            coverage_metrics = self.analyze_test_coverage(project_path)
            quality_metrics = self.analyze_code_quality_issues(project_path)

            project_metrics = {
                "structure": structure_metrics,
                "complexity": complexity_metrics,
                "coverage": coverage_metrics,
                "quality": quality_metrics
            }

            workspace_metrics["projects"][project_name] = project_metrics

            # Aggregate for summary
            workspace_metrics["summary"]["total_files"] += structure_metrics["python_files"]
            workspace_metrics["summary"]["total_lines"] += structure_metrics["total_lines"]
            workspace_metrics["summary"]["total_issues"] += quality_metrics["total_issues"]

            if complexity_metrics["total_functions"] > 0:
                total_complexity += complexity_metrics["average_complexity"] * \
                    complexity_metrics["total_functions"]
                total_functions += complexity_metrics["total_functions"]

            if coverage_metrics["coverage_available"]:
                total_coverage += coverage_metrics["coverage_percentage"]
                projects_with_coverage += 1

        # Calculate summary metrics
        if total_functions > 0:
            workspace_metrics["summary"]["average_complexity"] = total_complexity / \
                total_functions

        if projects_with_coverage > 0:
            workspace_metrics["summary"]["overall_coverage"] = total_coverage / \
                projects_with_coverage

        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(workspace_metrics)
        workspace_metrics["summary"]["quality_score"] = quality_score

        # Store metrics
        self.metrics = workspace_metrics

        # Show results
        if self.verbose:
            self._show_quality_dashboard(workspace_metrics)

        # Save report if requested
        if self.save_report:
            self._save_quality_report(workspace_metrics)

        return workspace_metrics

    def _calculate_quality_score(self, metrics: dict[str, Any]) -> float:
        """Calculate overall quality score based on various metrics."""
        score = 100.0

        summary = metrics["summary"]

        # Deduct points for issues
        if summary["total_files"] > 0:
            issues_per_file = summary["total_issues"] / summary["total_files"]
            score -= min(issues_per_file * 5, 30)  # Max 30 point deduction

        # Deduct points for complexity
        if summary["average_complexity"] > self.QUALITY_THRESHOLDS["cyclomatic_complexity"]:
            complexity_penalty = (
                summary["average_complexity"] - self.QUALITY_THRESHOLDS["cyclomatic_complexity"]) * 2
            score -= min(complexity_penalty, 20)  # Max 20 point deduction

        # Deduct points for low coverage
        coverage_target = self.QUALITY_THRESHOLDS["test_coverage"]
        if summary["overall_coverage"] < coverage_target:
            coverage_penalty = (
                coverage_target - summary["overall_coverage"]) / 2
            score -= min(coverage_penalty, 25)  # Max 25 point deduction

        return max(score, 0.0)

    def _show_quality_dashboard(self, metrics: dict[str, Any]) -> None:
        """Show quality metrics dashboard."""
        summary = metrics["summary"]

        # Overview table
        overview_table = Table(title="Quality Metrics Overview")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        overview_table.add_column("Status", style="yellow")

        # Overall quality score
        quality_score = summary["quality_score"]
        score_status = "🟢 Excellent" if quality_score >= 90 else "🟡 Good" if quality_score >= 75 else "🔴 Needs Improvement"
        overview_table.add_row(
            "Quality Score", f"{
                quality_score:.1f}/100", score_status)

        # Coverage
        coverage = summary["overall_coverage"]
        coverage_status = "✅" if coverage >= self.QUALITY_THRESHOLDS["test_coverage"] else "❌"
        overview_table.add_row(
            "Test Coverage", f"{coverage:.1f}%", coverage_status)

        # Complexity
        complexity = summary["average_complexity"]
        complexity_status = "✅" if complexity <= self.QUALITY_THRESHOLDS[
            "cyclomatic_complexity"] else "❌"
        overview_table.add_row(
            "Avg Complexity", f"{
                complexity:.1f}", complexity_status)

        # Issues
        issues_per_file = summary["total_issues"] / \
            summary["total_files"] if summary["total_files"] > 0 else 0
        issues_status = "✅" if issues_per_file <= 1 else "⚠️" if issues_per_file <= 5 else "❌"
        overview_table.add_row(
            "Issues per File", f"{
                issues_per_file:.1f}", issues_status)

        self.console.print(overview_table)

        # Project comparison table
        project_table = Table(title="Project Quality Comparison")
        project_table.add_column("Project", style="cyan")
        project_table.add_column("Files", justify="right")
        project_table.add_column("Lines", justify="right")
        project_table.add_column("Coverage", justify="right")
        project_table.add_column("Complexity", justify="right")
        project_table.add_column("Issues", justify="right")

        for project_name, project_metrics in metrics["projects"].items():
            structure = project_metrics["structure"]
            complexity = project_metrics["complexity"]
            coverage = project_metrics["coverage"]
            quality = project_metrics["quality"]

            project_table.add_row(
                project_name,
                str(structure["python_files"]),
                str(structure["total_lines"]),
                f"{coverage['coverage_percentage']:.1f}%" if coverage["coverage_available"] else "N/A",
                f"{complexity['average_complexity']:.1f}",
                str(quality["total_issues"])
            )

        self.console.print(project_table)

        # Summary panel
        panel_text = (
            f"📊 Projects Analyzed: {metrics['total_projects']}\n"
            f"📁 Total Files: {summary['total_files']}\n"
            f"📝 Total Lines: {summary['total_lines']:,}\n"
            f"🔍 Total Issues: {summary['total_issues']}\n"
            f"⭐ Quality Score: {quality_score:.1f}/100"
        )

        panel_style = "green" if quality_score >= 90 else "yellow" if quality_score >= 75 else "red"
        self.console.print(
            Panel(
                panel_text,
                title="Quality Summary",
                border_style=panel_style))

    def _save_quality_report(self, metrics: dict[str, Any]) -> None:
        """Save quality report to file."""
        self.report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        if self.output_format == "json":
            report_file = self.report_dir / f"quality_metrics_{timestamp}.json"
            with open(report_file, "w") as f:
                json.dump(metrics, f, indent=2, default=str)

        if self.verbose:
            self.console.print(
                f"[green]📄 Quality report saved: {report_file}[/green]")

    def run_workspace_analysis(self, workspace_path: Path = None) -> bool:
        """Run quality analysis across the entire workspace."""
        metrics = self.generate_quality_report(workspace_path)
        return metrics["summary"]["quality_score"] >= 75.0

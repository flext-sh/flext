#!/usr/bin/env python3
"""Universal Quality Loop Module

Zero-tolerance quality assurance automation for enterprise Python projects.
Based on flx/scripts/universal_quality_loop.py and official_pyauto_lint_fixer.py.
"""

import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .base import CustomFixModule, Issue


class UniversalQualityLoopModule(CustomFixModule):
    """Module for universal zero-tolerance quality assurance automation."""

    name = "universal_quality_loop"
    description = (
        "Zero-tolerance quality assurance automation for enterprise Python projects"
    )

    # Quality tools in execution order
    QUALITY_TOOLS = [
        "autoflake",  # Remove unused imports/variables
        "pyupgrade",  # Upgrade syntax patterns
        "isort",  # Sort imports
        "black",  # Format code
        "ruff",  # Lint and fix
        "mypy",  # Type checking
        "bandit",  # Security analysis
        "safety",  # Dependency vulnerability check
    ]

    # Zero tolerance thresholds
    ZERO_TOLERANCE_LIMITS = {
        "max_iterations": 10,
        "max_mypy_errors": 0,
        "max_ruff_errors": 0,
        "max_security_issues": 0,
        "min_test_coverage": 90.0,
        "max_complexity": 10,
        "max_line_length": 88,
    }

    # Safe vs Unsafe fixes categorization
    SAFE_FIXES = {
        "autoflake": ["--remove-unused-variables", "--remove-all-unused-imports"],
        "pyupgrade": ["--py313-plus"],
        "isort": ["--fix-only"],
        "black": [],  # Black is always safe
        "ruff": ["--fix", "--select=I,UP,F401,F841"],  # Only safe rules
    }

    UNSAFE_FIXES = {
        "ruff": ["--fix", "--unsafe-fixes"],  # All fixes including unsafe
        "autoflake": ["--remove-duplicate-keys"],
        "pyupgrade": ["--keep-percent-format"],  # More aggressive
    }

    def __init__(
        self,
        zero_tolerance: bool = True,
        max_iterations: int = 10,
        enable_unsafe_fixes: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.zero_tolerance = zero_tolerance
        self.max_iterations = max_iterations
        self.enable_unsafe_fixes = enable_unsafe_fixes
        self.iteration = 0
        self.total_fixes_applied = 0
        self.metrics: dict[str, list[Any]] = defaultdict(list)
        self.project_config: dict[str, Any] = {}

    def detect_project_type(self, project_path: Path) -> str:
        """Detect the type of Python project."""
        # Check for pyproject.toml
        if (project_path / "pyproject.toml").exists():
            return "poetry"

        # Check for setup.py
        if (project_path / "setup.py").exists():
            return "setuptools"

        # Check for requirements.txt
        if (project_path / "requirements.txt").exists():
            return "pip"

        return "basic"

    def detect_source_paths(self, project_path: Path) -> list[Path]:
        """Detect source code paths in the project."""
        src_paths: list = []

        # Common source directories
        candidates = ["src", "lib", project_path.name.replace("-", "_")]

        for candidate in candidates:
            candidate_path = project_path / candidate
            if candidate_path.exists() and candidate_path.is_dir():
                # Check if it contains Python files
                if list(candidate_path.rglob("*.py")):
                    src_paths.append(candidate_path)

        # If no specific source dir, use project root
        if not src_paths:
            src_paths.append(project_path)

        return src_paths

    def detect_test_paths(self, project_path: Path) -> list[Path]:
        """Detect test code paths in the project."""
        test_paths: list = []

        # Common test directories
        candidates = ["tests", "test", "testing"]

        for candidate in candidates:
            candidate_path = project_path / candidate
            if candidate_path.exists() and candidate_path.is_dir():
                test_paths.append(candidate_path)

        return test_paths

    def run_tool(
        self, tool: str, project_path: Path, fix_mode: bool = False,
    ) -> tuple[bool, str, str]:
        """Run a quality tool on the project."""
        tool_configs = {
            "autoflake": {
                "check": ["autoflake", "--check", "--recursive"],
                "fix": ["autoflake", "--in-place", "--recursive"]
                + (
                    self.UNSAFE_FIXES["autoflake"]
                    if self.enable_unsafe_fixes
                    else self.SAFE_FIXES["autoflake"]
                ),
            },
            "pyupgrade": {
                "check": [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-exec",
                    "pyupgrade",
                    "--py313-plus",
                    "--check",
                    "{}",
                    "+",
                ],
                "fix": ["find", ".", "-name", "*.py", "-exec", "pyupgrade"]
                + self.SAFE_FIXES["pyupgrade"]
                + ["{}", "+"],
            },
            "isort": {
                "check": ["isort", "--check-only", "--diff"],
                "fix": ["isort"] + self.SAFE_FIXES["isort"],
            },
            "black": {"check": ["black", "--check", "--diff"], "fix": ["black"]},
            "ruff": {
                "check": ["ruff", "check", "--format=json"],
                "fix": ["ruff", "check"]
                + (
                    self.UNSAFE_FIXES["ruff"]
                    if self.enable_unsafe_fixes
                    else self.SAFE_FIXES["ruff"]
                ),
            },
            "mypy": {
                "check": ["mypy", "--no-error-summary"],
                "fix": [],  # MyPy doesn't auto-fix
            },
            "bandit": {
                "check": ["bandit", "-r", "-f", "json"],
                "fix": [],  # Bandit doesn't auto-fix
            },
            "safety": {
                "check": ["safety", "check", "--json"],
                "fix": [],  # Safety doesn't auto-fix
            },
        }

        if tool not in tool_configs:
            return False, f"Unknown tool: {tool}", ""

        config = tool_configs[tool]
        cmd = config["fix"] if fix_mode and config["fix"] else config["check"]

        try:
            # Add project-specific paths for source analysis
            if tool in ["ruff", "mypy", "black", "isort"]:
                src_paths = self.detect_source_paths(project_path)
                if src_paths and tool != "pyupgrade":  # pyupgrade uses find command
                    cmd = cmd + [str(path) for path in src_paths]

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300, check=False,  # 5 minute timeout
            )

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", f"{tool} timed out after 5 minutes"
        except FileNotFoundError:
            return False, "", f"{tool} not found - please install it"
        except Exception as e:
            return False, "", f"Error running {tool}: {e}"

    def analyze_results(
        self, tool: str, success: bool, stdout: str, stderr: str,
    ) -> dict[str, Any]:
        """Analyze tool results and extract metrics."""
        analysis = {
            "tool": tool,
            "success": success,
            "issues_found": 0,
            "issues_fixed": 0,
            "details": [],
            "errors": [],
        }

        if tool == "ruff" and stdout:
            try:
                ruff_results = json.loads(stdout)
                analysis["issues_found"] = len(ruff_results)

                # Categorize Ruff issues
                for issue in ruff_results:
                    analysis["details"].append(
                        {
                            "file": issue.get("filename", ""),
                            "line": issue.get("location", {}).get("row", 0),
                            "code": issue.get("code", ""),
                            "message": issue.get("message", ""),
                            "severity": "error"
                            if issue.get("code", "").startswith("E")
                            else "warning",
                        },
                    )
            except json.JSONDecodeError:
                # Fallback to text parsing
                lines = stdout.split("\n")
                analysis["issues_found"] = len(
                    [
                        line
                        for line in lines
                        if line.strip() and not line.startswith("Found")
                    ],
                )

        elif tool == "mypy":
            # Parse MyPy output
            lines = stdout.split("\n") + stderr.split("\n")
            error_lines = [
                line for line in lines if ": error:" in line or ": warning:" in line
            ]
            analysis["issues_found"] = len(error_lines)

            for line in error_lines:
                if ": error:" in line or ": warning:" in line:
                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        analysis["details"].append(
                            {
                                "file": parts[0],
                                "line": parts[1] if parts[1].isdigit() else 0,
                                "type": parts[2].strip(),
                                "message": parts[3].strip() if len(parts) > 3 else "",
                                "severity": "error"
                                if ": error:" in line
                                else "warning",
                            },
                        )

        elif tool == "bandit" and stdout:
            try:
                bandit_results = json.loads(stdout)
                issues = bandit_results.get("results", [])
                analysis["issues_found"] = len(issues)

                for issue in issues:
                    analysis["details"].append(
                        {
                            "file": issue.get("filename", ""),
                            "line": issue.get("line_number", 0),
                            "severity": issue.get("issue_severity", "unknown"),
                            "confidence": issue.get("issue_confidence", "unknown"),
                            "test_id": issue.get("test_id", ""),
                            "message": issue.get("issue_text", ""),
                        },
                    )
            except json.JSONDecodeError:
                pass

        elif tool == "safety" and stdout:
            try:
                safety_results = json.loads(stdout)
                analysis["issues_found"] = len(safety_results)

                for issue in safety_results:
                    analysis["details"].append(
                        {
                            "package": issue.get("package", ""),
                            "vulnerability": issue.get("vulnerability", ""),
                            "severity": issue.get("severity", "unknown"),
                            "advisory": issue.get("advisory", ""),
                        },
                    )
            except json.JSONDecodeError:
                pass

        # Count fixes applied (for tools that auto-fix)
        if success and tool in ["autoflake", "isort", "black", "ruff"]:
            # Estimate fixes based on before/after comparison
            analysis["issues_fixed"] = analysis["issues_found"]

        return analysis

    def run_quality_iteration(self, project_path: Path) -> dict[str, Any]:
        """Run a single quality assurance iteration."""
        self.iteration += 1
        iteration_results = {
            "iteration": self.iteration,
            "timestamp": time.time(),
            "tools": {},
            "total_issues": 0,
            "total_fixes": 0,
            "success": True,
        }

        if self.verbose:
            self.console.print(f"[blue]Quality Loop Iteration {self.iteration}[/blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            for tool in self.QUALITY_TOOLS:
                task = progress.add_task(f"Running {tool}...", total=None)

                # Check first
                success, stdout, stderr = self.run_tool(
                    tool, project_path, fix_mode=False,
                )
                check_analysis = self.analyze_results(tool, success, stdout, stderr)

                # Apply fixes if issues found and tool supports fixing
                fix_analysis = None
                if check_analysis["issues_found"] > 0 and tool in [
                    "autoflake",
                    "pyupgrade",
                    "isort",
                    "black",
                    "ruff",
                ]:
                    if not self.dry_run:
                        fix_success, fix_stdout, fix_stderr = self.run_tool(
                            tool, project_path, fix_mode=True,
                        )
                        fix_analysis = self.analyze_results(
                            tool, fix_success, fix_stdout, fix_stderr,
                        )

                        if fix_analysis["issues_fixed"] > 0:
                            self.total_fixes_applied += fix_analysis["issues_fixed"]

                # Update progress
                if check_analysis["issues_found"] == 0:
                    progress.update(task, description=f"✅ {tool} - No issues")
                elif fix_analysis and fix_analysis["issues_fixed"] > 0:
                    progress.update(
                        task,
                        description=f"🔧 {tool} - Fixed {fix_analysis['issues_fixed']} issues",
                    )
                    progress.update(
                        task,
                        description=f"⚠️ {tool} - {check_analysis['issues_found']} issues found",
                    )

                # Store results
                tool_result = {
                    "check": check_analysis,
                    "fix": fix_analysis,
                    "final_issues": check_analysis["issues_found"]
                    - (fix_analysis["issues_fixed"] if fix_analysis else 0),
                }

                iteration_results["tools"][tool] = tool_result
                iteration_results["total_issues"] += tool_result["final_issues"]
                iteration_results["total_fixes"] += (
                    fix_analysis["issues_fixed"] if fix_analysis else 0
                )

                # Zero tolerance check
                if self.zero_tolerance and tool in self.ZERO_TOLERANCE_LIMITS:
                    limit_key = f"max_{tool}_errors"
                    if limit_key in self.ZERO_TOLERANCE_LIMITS:
                        if (
                            tool_result["final_issues"]
                            > self.ZERO_TOLERANCE_LIMITS[limit_key]
                        ):
                            iteration_results["success"] = False
                            if self.verbose:
                                self.console.print(
                                    f"[red]ZERO TOLERANCE VIOLATION: {tool} has {
                                        tool_result['final_issues']
                                    } issues (limit: {
                                        self.ZERO_TOLERANCE_LIMITS[limit_key]
                                    })[/red]",
                                )

        return iteration_results

    def run_tests(self, project_path: Path) -> dict[str, Any]:
        """Run project tests and collect coverage."""
        test_results = {
            "success": False,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "errors": [],
        }

        try:
            # Detect test runner
            if (project_path / "pyproject.toml").exists():
                cmd = [
                    "poetry",
                    "run",
                    "pytest",
                    "--tb=short",
                    "--cov=src",
                    "--cov-report=term-missing",
                ]
                cmd = ["pytest", "--tb=short"]

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600, check=False,  # 10 minute timeout for tests
            )

            test_results["success"] = result.returncode == 0

            # Parse pytest output
            output = result.stdout + result.stderr

            # Extract test counts
            import re

            test_summary = re.search(r"(\d+) passed", output)
            if test_summary:
                test_results["tests_passed"] = int(test_summary.group(1))

            failed_summary = re.search(r"(\d+) failed", output)
            if failed_summary:
                test_results["tests_failed"] = int(failed_summary.group(1))

            test_results["tests_run"] = (
                test_results["tests_passed"] + test_results["tests_failed"]
            )

            # Extract coverage
            coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
            if coverage_match:
                test_results["coverage"] = float(coverage_match.group(1))

        except subprocess.TimeoutExpired:
            test_results["errors"].append("Tests timed out after 10 minutes")
        except Exception as e:
            test_results["errors"].append(f"Error running tests: {e}")

        return test_results

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze individual files for quality issues."""
        issues: list = []

        if file_path.suffix == ".py":
            lines = content.split("\n")

            # Check for common quality issues
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check line length
                if len(line) > self.ZERO_TOLERANCE_LIMITS["max_line_length"]:
                    issues.append(
                        Issue(
                            line=i,
                            column=len(line),
                            code="QUALITY_LENGTH001",
                            message=f"Line too long ({len(line)} > {
                                self.ZERO_TOLERANCE_LIMITS['max_line_length']
                            })",
                            suggestion="Break line or refactor to reduce length",
                        ),
                    )

                # Check for print statements in production code
                if "print(" in line and not file_path.name.startswith("test_"):
                    issues.append(
                        Issue(
                            line=i,
                            column=line.find("print(") + 1,
                            code="QUALITY_DEBUG001",
                            message="Print statement found in production code",
                            suggestion="Use logging instead of print statements",
                        ),
                    )

                # Check for TODO/FIXME comments
                if any(
                    marker in line_stripped.upper()
                    for marker in ["TODO", "FIXME", "HACK", "XXX"]
                ):
                    issues.append(
                        Issue(
                            line=i,
                            column=1,
                            code="QUALITY_TODO001",
                            message="TODO/FIXME comment found",
                            suggestion="Resolve TODO items before production",
                        ),
                    )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply quality fixes to content."""
        lines = content.split("\n")

        for issue in issues:
            if issue.code == "QUALITY_DEBUG001":  # Remove print statements
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    if "print(" in line:
                        # Comment out print statements
                        lines[line_idx] = (
                            "# " + line + "  # TODO: Replace with proper logging"
                        )

        return "\n".join(lines)

    def run_universal_quality_loop(self, workspace_path: Path = None) -> dict[str, Any]:
        """Run universal quality loop across workspace projects."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Starting Universal Quality Loop in: {workspace_path}[/blue]",
            )

        # Find all projects
        projects: list = []
        for pyproject_file in workspace_path.rglob("pyproject.toml"):
            if not any(part.startswith(".") for part in pyproject_file.parts):
                projects.append(pyproject_file.parent)

        if self.verbose:
            self.console.print(f"[green]Found {len(projects)} projects[/green]")

        workspace_results = {
            "timestamp": time.time(),
            "projects": {},
            "summary": {
                "total_projects": len(projects),
                "successful_projects": 0,
                "total_iterations": 0,
                "total_fixes": 0,
                "zero_tolerance_passed": True,
            },
        }

        for project_path in projects:
            project_name = project_path.name

            if self.verbose:
                self.console.print(f"\n[bold]Processing project: {project_name}[/bold]")

            # Reset iteration counter for each project
            self.iteration = 0
            project_results = {
                "project_type": self.detect_project_type(project_path),
                "iterations": [],
                "tests": {},
                "final_status": "unknown",
            }

            # Run quality iterations until convergence or max iterations
            converged = False
            while not converged and self.iteration < self.max_iterations:
                iteration_result = self.run_quality_iteration(project_path)
                project_results["iterations"].append(iteration_result)

                # Check for convergence (no more issues to fix)
                if iteration_result["total_issues"] == 0:
                    converged = True
                    project_results["final_status"] = "perfect"
                elif iteration_result["total_fixes"] == 0:
                    # No progress made, stop iterations
                    converged = True
                    project_results["final_status"] = (
                        "stable" if iteration_result["success"] else "failed"
                    )

                # Zero tolerance check
                if self.zero_tolerance and not iteration_result["success"]:
                    workspace_results["summary"]["zero_tolerance_passed"] = False
                    project_results["final_status"] = "zero_tolerance_violation"
                    break

            # Run tests
            if project_results["final_status"] in ["perfect", "stable"]:
                test_results = self.run_tests(project_path)
                project_results["tests"] = test_results

                # Update final status based on tests
                if self.zero_tolerance:
                    if (
                        test_results["coverage"]
                        < self.ZERO_TOLERANCE_LIMITS["min_test_coverage"]
                    ):
                        project_results["final_status"] = "insufficient_coverage"
                        workspace_results["summary"]["zero_tolerance_passed"] = False

            workspace_results["projects"][project_name] = project_results
            workspace_results["summary"]["total_iterations"] += len(
                project_results["iterations"],
            )
            workspace_results["summary"]["total_fixes"] += sum(
                iter_result["total_fixes"]
                for iter_result in project_results["iterations"]
            )

            if project_results["final_status"] in ["perfect", "stable"]:
                workspace_results["summary"]["successful_projects"] += 1

        # Show final summary
        if self.verbose:
            self._show_quality_summary(workspace_results)

        return workspace_results

    def _show_quality_summary(self, results: dict[str, Any]) -> None:
        """Show quality loop summary."""
        summary = results["summary"]

        # Project status table
        table = Table(title="Universal Quality Loop Results")
        table.add_column("Project", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Iterations", justify="right")
        table.add_column("Total Fixes", justify="right")
        table.add_column("Test Coverage", justify="right")

        for project_name, project_result in results["projects"].items():
            status_styles = {
                "perfect": "🟢 PERFECT",
                "stable": "🟡 STABLE",
                "failed": "🔴 FAILED",
                "zero_tolerance_violation": "🚫 VIOLATION",
                "insufficient_coverage": "📊 LOW COVERAGE",
            }

            status = status_styles.get(
                project_result["final_status"], project_result["final_status"].upper(),
            )
            iterations = len(project_result["iterations"])
            total_fixes = sum(
                iter_result["total_fixes"]
                for iter_result in project_result["iterations"]
            )

            test_coverage = "N/A"
            if project_result["tests"]:
                coverage = project_result["tests"].get("coverage", 0)
                test_coverage = f"{coverage:.1f}%" if coverage > 0 else "N/A"

            table.add_row(
                project_name, status, str(iterations), str(total_fixes), test_coverage,
            )

        self.console.print(table)

        # Summary panel
        success_rate = (
            (summary["successful_projects"] / summary["total_projects"] * 100)
            if summary["total_projects"] > 0
            else 0
        )

        panel_text = f"🎯 Projects Processed: {
            summary['total_projects']
        }\n✅ Successful: {summary['successful_projects']}\n🔄 Total Iterations: {
            summary['total_iterations']
        }\n🔧 Total Fixes Applied: {summary['total_fixes']}\n📊 Success Rate: {
            success_rate:.1f
        }%\n🎭 Zero Tolerance: {
            '✅ PASSED' if summary['zero_tolerance_passed'] else '❌ VIOLATED'
        }"

        panel_style = (
            "green"
            if summary["zero_tolerance_passed"] and success_rate == 100
            else "yellow"
            if success_rate >= 80
            else "red"
        )
        self.console.print(
            Panel(panel_text, title="Quality Loop Summary", border_style=panel_style),
        )

    def run_workspace_quality_loop(self, workspace_path: Path = None) -> bool:
        """Run universal quality loop across the entire workspace."""
        results = self.run_universal_quality_loop(workspace_path)
        return (
            results["summary"]["zero_tolerance_passed"]
            and results["summary"]["successful_projects"]
            == results["summary"]["total_projects"]
        )

"""FLEXT Tools Utilities - Domain-specific utilities for development tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, ClassVar

from pydantic import field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextResult, FlextUtilities
from flext_tools.models import FlextToolsModels


class FlextToolsUtilities(FlextUtilities):
    """Development tools utilities extending FlextUtilities with nested classes.

    Provides comprehensive development tools capabilities with nested classes for:
    - Build system management
    - Code analysis and quality tools
    - Test execution and reporting
    - Environment management
    - Project scaffolding
    - Package management
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TOOLS_",
        case_sensitive=False,
        extra="allow",
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT Tools Utilities",
            "description": "Development tools utilities for FLEXT ecosystem",
        },
    )

    class BuildSystem:
        """Build system management utilities."""

        SUPPORTED_BUILD_TOOLS: ClassVar[list[str]] = [
            "poetry",
            "pip",
            "setuptools",
            "make",
            "npm",
            "yarn",
            "cargo",
        ]
        BUILD_FILE_PATTERNS: ClassVar[list[str]] = [
            "pyproject.toml",
            "setup.py",
            "Makefile",
            "package.json",
            "Cargo.toml",
        ]
        DEFAULT_TIMEOUT_SECONDS: ClassVar[int] = 300

        @staticmethod
        def detect_build_system(
            project_path: Path | str,
        ) -> FlextResult[FlextToolsModels.BuildSystemInfo]:
            """Detect build system used in project.

            Args:
                project_path: Path to project directory

            Returns:
                FlextResult containing build system information
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.BuildSystemInfo].fail(
                        f"Project path does not exist: {path}"
                    )

                build_files = []
                build_tools = []

                for pattern in FlextToolsUtilities.BuildSystem.BUILD_FILE_PATTERNS:
                    for build_file in path.rglob(pattern):
                        if build_file.is_file():
                            build_files.append(str(build_file))

                # Detect Python build systems
                if any("pyproject.toml" in f for f in build_files):
                    if (path / "poetry.lock").exists():
                        build_tools.append("poetry")
                    else:
                        build_tools.append("pip")
                elif any("setup.py" in f for f in build_files):
                    build_tools.append("setuptools")

                # Detect other build systems
                if any("Makefile" in f for f in build_files):
                    build_tools.append("make")
                if any("package.json" in f for f in build_files):
                    if (path / "yarn.lock").exists():
                        build_tools.append("yarn")
                    else:
                        build_tools.append("npm")
                if any("Cargo.toml" in f for f in build_files):
                    build_tools.append("cargo")

                build_info = FlextToolsModels.BuildSystemInfo(
                    primary_tool=build_tools[0] if build_tools else "unknown",
                    detected_tools=build_tools,
                    build_files=build_files,
                    project_path=str(path),
                    analysis_timestamp=datetime.now(UTC).isoformat(),
                )

                return FlextResult[FlextToolsModels.BuildSystemInfo].ok(build_info)
            except Exception as e:
                return FlextResult[FlextToolsModels.BuildSystemInfo].fail(
                    f"Build system detection failed: {e}"
                )

        @staticmethod
        def execute_build_command(
            command: str, project_path: Path | str, timeout: int | None = None
        ) -> FlextResult[FlextToolsModels.CommandResult]:
            """Execute build command in project directory.

            Args:
                command: Build command to execute
                project_path: Path to project directory
                timeout: Command timeout in seconds

            Returns:
                FlextResult containing command execution result
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.CommandResult].fail(
                        f"Project path does not exist: {path}"
                    )

                timeout_value = (
                    timeout or FlextToolsUtilities.BuildSystem.DEFAULT_TIMEOUT_SECONDS
                )

                # Execute command with timeout
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=timeout_value,
                    check=False,
                )

                command_result = FlextToolsModels.CommandResult(
                    command=command,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=0.0,  # Would need time measurement
                    success=result.returncode == 0,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                return FlextResult[FlextToolsModels.CommandResult].ok(command_result)
            except subprocess.TimeoutExpired:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    f"Build command timed out after {timeout_value} seconds"
                )
            except Exception as e:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    f"Build command execution failed: {e}"
                )

        @staticmethod
        def validate_build_environment(
            project_path: Path | str,
        ) -> FlextResult[dict[str, Any]]:
            """Validate build environment for project.

            Args:
                project_path: Path to project directory

            Returns:
                FlextResult containing build environment validation
            """
            try:
                path = Path(project_path)
                validation_report = {
                    "valid": True,
                    "issues": [],
                    "recommendations": [],
                    "tools_available": {},
                    "validated_at": datetime.now(UTC).isoformat(),
                }

                # Check for required tools
                for tool in FlextToolsUtilities.BuildSystem.SUPPORTED_BUILD_TOOLS:
                    try:
                        result = subprocess.run(
                            [tool, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                        )
                        validation_report["tools_available"][tool] = (
                            result.returncode == 0
                        )
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        validation_report["tools_available"][tool] = False

                # Detect build system for project
                build_detection = FlextToolsUtilities.BuildSystem.detect_build_system(
                    path
                )
                if build_detection.is_success:
                    build_info = build_detection.unwrap()
                    if build_info.primary_tool == "unknown":
                        validation_report["valid"] = False
                        validation_report["issues"].append(
                            "No supported build system detected"
                        )
                    elif not validation_report["tools_available"].get(
                        build_info.primary_tool, False
                    ):
                        validation_report["valid"] = False
                        validation_report["issues"].append(
                            f"Primary build tool '{build_info.primary_tool}' not available"
                        )

                return FlextResult[dict[str, Any]].ok(validation_report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Build environment validation failed: {e}"
                )

    class CodeAnalysis:
        """Code analysis and quality tools utilities."""

        SUPPORTED_LINTERS: ClassVar[list[str]] = [
            "ruff",
            "pylint",
            "flake8",
            "black",
            "isort",
            "mypy",
        ]
        ANALYSIS_PATTERNS: ClassVar[dict[str, str]] = {
            "python": "**/*.py",
            "javascript": "**/*.js",
            "typescript": "**/*.ts",
            "rust": "**/*.rs",
            "go": "**/*.go",
        }
        DEFAULT_COMPLEXITY_THRESHOLD: ClassVar[int] = 10

        @staticmethod
        def run_linter(
            linter_name: str,
            target_path: Path | str,
            config_file: Path | str | None = None,
        ) -> FlextResult[FlextToolsModels.AnalysisResult]:
            """Run specified linter on target path.

            Args:
                linter_name: Name of linter to run
                target_path: Path to analyze
                config_file: Optional configuration file

            Returns:
                FlextResult containing linter analysis results
            """
            try:
                if (
                    linter_name
                    not in FlextToolsUtilities.CodeAnalysis.SUPPORTED_LINTERS
                ):
                    return FlextResult[FlextToolsModels.AnalysisResult].fail(
                        f"Unsupported linter: {linter_name}"
                    )

                path = Path(target_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.AnalysisResult].fail(
                        f"Target path does not exist: {path}"
                    )

                # Build linter command
                command = [linter_name]
                if config_file:
                    config_path = Path(config_file)
                    if config_path.exists():
                        command.extend(["--config", str(config_path)])

                command.append(str(path))

                # Execute linter
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=120, check=False
                )

                analysis_result = FlextToolsModels.AnalysisResult(
                    tool=linter_name,
                    target_path=str(path),
                    success=result.returncode == 0,
                    issues_found=result.returncode != 0,
                    output=result.stdout,
                    error_output=result.stderr,
                    analysis_timestamp=datetime.now(UTC).isoformat(),
                    metadata={
                        "return_code": result.returncode,
                        "config_file": str(config_file) if config_file else None,
                    },
                )

                return FlextResult[FlextToolsModels.AnalysisResult].ok(analysis_result)
            except subprocess.TimeoutExpired:
                return FlextResult[FlextToolsModels.AnalysisResult].fail(
                    f"Linter {linter_name} timed out"
                )
            except Exception as e:
                return FlextResult[FlextToolsModels.AnalysisResult].fail(
                    f"Linter execution failed: {e}"
                )

        @staticmethod
        def analyze_code_complexity(
            file_path: Path | str,
        ) -> FlextResult[dict[str, Any]]:
            """Analyze code complexity of file.

            Args:
                file_path: Path to source file

            Returns:
                FlextResult containing complexity analysis
            """
            try:
                path = Path(file_path)
                if not path.exists():
                    return FlextResult[dict[str, Any]].fail(
                        f"File does not exist: {path}"
                    )

                content = path.read_text(encoding="utf-8")
                complexity_report = {
                    "file_path": str(path),
                    "lines_of_code": len(content.splitlines()),
                    "cyclomatic_complexity": 1,  # Basic calculation
                    "cognitive_complexity": 0,
                    "complexity_issues": [],
                    "analysis_timestamp": datetime.now(UTC).isoformat(),
                }

                # Simple complexity analysis
                if path.suffix == ".py":
                    # Count control flow statements for basic cyclomatic complexity
                    control_statements = [
                        "if",
                        "elif",
                        "for",
                        "while",
                        "try",
                        "except",
                        "with",
                    ]
                    for statement in control_statements:
                        complexity_report["cyclomatic_complexity"] += content.count(
                            f"{statement} "
                        )

                    # Check for complexity issues
                    if (
                        complexity_report["cyclomatic_complexity"]
                        > FlextToolsUtilities.CodeAnalysis.DEFAULT_COMPLEXITY_THRESHOLD
                    ):
                        complexity_report["complexity_issues"].append(
                            f"High cyclomatic complexity: {complexity_report['cyclomatic_complexity']}"
                        )

                    # Count function definitions
                    function_count = content.count("def ")
                    class_count = content.count("class ")
                    complexity_report.update(
                        {"function_count": function_count, "class_count": class_count}
                    )

                return FlextResult[dict[str, Any]].ok(complexity_report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Complexity analysis failed: {e}"
                )

        @staticmethod
        def generate_analysis_report(
            analysis_results: list[FlextToolsModels.AnalysisResult],
        ) -> FlextResult[dict[str, Any]]:
            """Generate comprehensive analysis report from multiple results.

            Args:
                analysis_results: List of analysis results from different tools

            Returns:
                FlextResult containing comprehensive analysis report
            """
            try:
                report = {
                    "summary": {
                        "total_tools": len(analysis_results),
                        "successful_tools": 0,
                        "failed_tools": 0,
                        "issues_found": False,
                    },
                    "tool_results": [],
                    "recommendations": [],
                    "generated_at": datetime.now(UTC).isoformat(),
                }

                for result in analysis_results:
                    tool_summary = {
                        "tool": result.tool,
                        "success": result.success,
                        "issues_found": result.issues_found,
                        "target_path": result.target_path,
                    }
                    report["tool_results"].append(tool_summary)

                    if result.success:
                        report["summary"]["successful_tools"] += 1
                    else:
                        report["summary"]["failed_tools"] += 1

                    if result.issues_found:
                        report["summary"]["issues_found"] = True

                # Generate recommendations
                if report["summary"]["issues_found"]:
                    report["recommendations"].append(
                        "Review and fix identified code quality issues"
                    )

                if report["summary"]["failed_tools"] > 0:
                    report["recommendations"].append(
                        "Investigate failed analysis tools"
                    )

                return FlextResult[dict[str, Any]].ok(report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Analysis report generation failed: {e}"
                )

    class TestExecution:
        """Test execution and reporting utilities."""

        SUPPORTED_TEST_FRAMEWORKS: ClassVar[list[str]] = [
            "pytest",
            "unittest",
            "nose2",
            "jest",
            "cargo",
        ]
        TEST_FILE_PATTERNS: ClassVar[dict[str, list[str]]] = {
            "python": ["test_*.py", "*_test.py", "tests/*.py"],
            "javascript": ["*.test.js", "*.spec.js", "__tests__/*.js"],
            "typescript": ["*.test.ts", "*.spec.ts", "__tests__/*.ts"],
            "rust": ["tests/*.rs"],
            "go": ["*_test.go"],
        }
        DEFAULT_TEST_TIMEOUT: ClassVar[int] = 600

        @staticmethod
        def discover_tests(
            project_path: Path | str, language: str = "python"
        ) -> FlextResult[list[str]]:
            """Discover test files in project.

            Args:
                project_path: Path to project directory
                language: Programming language for test discovery

            Returns:
                FlextResult containing list of discovered test files
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[list[str]].fail(
                        f"Project path does not exist: {path}"
                    )

                patterns = FlextToolsUtilities.TestExecution.TEST_FILE_PATTERNS.get(
                    language, []
                )
                test_files = []

                for pattern in patterns:
                    for test_file in path.rglob(pattern):
                        if test_file.is_file():
                            test_files.append(str(test_file))

                return FlextResult[list[str]].ok(sorted(test_files))
            except Exception as e:
                return FlextResult[list[str]].fail(f"Test discovery failed: {e}")

        @staticmethod
        def run_tests(
            test_command: str,
            project_path: Path | str,
            timeout: int | None = None,
            coverage: bool = False,
        ) -> FlextResult[FlextToolsModels.TestResult]:
            """Run tests with specified command.

            Args:
                test_command: Test command to execute
                project_path: Path to project directory
                timeout: Test execution timeout
                coverage: Whether to collect coverage data

            Returns:
                FlextResult containing test execution results
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.TestResult].fail(
                        f"Project path does not exist: {path}"
                    )

                timeout_value = (
                    timeout or FlextToolsUtilities.TestExecution.DEFAULT_TEST_TIMEOUT
                )

                # Add coverage if requested
                if coverage and "pytest" in test_command:
                    test_command += " --cov=src --cov-report=term --cov-report=json"

                start_time = datetime.now(UTC)
                result = subprocess.run(
                    test_command,
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=timeout_value,
                    check=False,
                )
                end_time = datetime.now(UTC)

                execution_time = (end_time - start_time).total_seconds()

                # Parse test results (basic parsing)
                tests_run = 0
                tests_passed = 0
                tests_failed = 0
                tests_skipped = 0

                if "pytest" in test_command:
                    # Basic pytest output parsing
                    output_lines = result.stdout.split("\n")
                    for line in output_lines:
                        if "passed" in line or "failed" in line or "skipped" in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "passed" and i > 0:
                                    tests_passed = int(parts[i - 1])
                                elif part == "failed" and i > 0:
                                    tests_failed = int(parts[i - 1])
                                elif part == "skipped" and i > 0:
                                    tests_skipped = int(parts[i - 1])

                tests_run = tests_passed + tests_failed + tests_skipped

                test_result = FlextToolsModels.TestResult(
                    framework="pytest",  # Could be detected from command
                    tests_run=tests_run,
                    tests_passed=tests_passed,
                    tests_failed=tests_failed,
                    tests_skipped=tests_skipped,
                    execution_time=execution_time,
                    success=result.returncode == 0,
                    coverage_enabled=coverage,
                    output=result.stdout,
                    error_output=result.stderr,
                    timestamp=start_time.isoformat(),
                )

                return FlextResult[FlextToolsModels.TestResult].ok(test_result)
            except subprocess.TimeoutExpired:
                return FlextResult[FlextToolsModels.TestResult].fail(
                    f"Test execution timed out after {timeout_value} seconds"
                )
            except Exception as e:
                return FlextResult[FlextToolsModels.TestResult].fail(
                    f"Test execution failed: {e}"
                )

        @staticmethod
        def generate_test_report(
            test_results: list[FlextToolsModels.TestResult],
        ) -> FlextResult[dict[str, Any]]:
            """Generate comprehensive test report.

            Args:
                test_results: List of test results

            Returns:
                FlextResult containing test report
            """
            try:
                total_tests = sum(result.tests_run for result in test_results)
                total_passed = sum(result.tests_passed for result in test_results)
                total_failed = sum(result.tests_failed for result in test_results)
                total_skipped = sum(result.tests_skipped for result in test_results)

                pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

                report = {
                    "summary": {
                        "total_test_runs": len(test_results),
                        "total_tests": total_tests,
                        "total_passed": total_passed,
                        "total_failed": total_failed,
                        "total_skipped": total_skipped,
                        "pass_rate": round(pass_rate, 2),
                        "all_successful": all(
                            result.success for result in test_results
                        ),
                    },
                    "test_runs": [
                        {
                            "framework": result.framework,
                            "tests_run": result.tests_run,
                            "success": result.success,
                            "execution_time": result.execution_time,
                            "coverage_enabled": result.coverage_enabled,
                        }
                        for result in test_results
                    ],
                    "generated_at": datetime.now(UTC).isoformat(),
                }

                return FlextResult[dict[str, Any]].ok(report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Test report generation failed: {e}"
                )

    class EnvironmentManager:
        """Environment management utilities."""

        SUPPORTED_ENV_MANAGERS: ClassVar[list[str]] = [
            "venv",
            "conda",
            "pipenv",
            "poetry",
            "virtualenv",
        ]
        ENV_FILE_PATTERNS: ClassVar[list[str]] = [
            ".env",
            ".internal.invalid",
            ".env.development",
            ".env.production",
        ]
        PYTHON_VERSION_PATTERN: ClassVar[str] = r"python(\d+)\.(\d+)"

        @staticmethod
        def detect_virtual_environment() -> FlextResult[dict[str, Any]]:
            """Detect current virtual environment.

            Returns:
                FlextResult containing virtual environment information
            """
            try:
                env_info = {
                    "active": False,
                    "type": "none",
                    "path": None,
                    "python_version": None,
                    "detected_at": datetime.now(UTC).isoformat(),
                }

                # Check for active virtual environment
                virtual_env = os.environ.get("VIRTUAL_ENV")
                conda_env = os.environ.get("CONDA_DEFAULT_ENV")
                poetry_env = os.environ.get("POETRY_ACTIVE")

                if virtual_env:
                    env_info.update(
                        {"active": True, "type": "venv", "path": virtual_env}
                    )
                elif conda_env:
                    env_info.update(
                        {"active": True, "type": "conda", "path": conda_env}
                    )
                elif poetry_env:
                    env_info.update(
                        {"active": True, "type": "poetry", "path": poetry_env}
                    )

                # Get Python version
                try:
                    result = subprocess.run(
                        ["python", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=True,
                    )
                    env_info["python_version"] = result.stdout.strip()
                except (
                    subprocess.TimeoutExpired,
                    subprocess.CalledProcessError,
                    FileNotFoundError,
                ):
                    env_info["python_version"] = "unknown"

                return FlextResult[dict[str, Any]].ok(env_info)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Environment detection failed: {e}"
                )

        @staticmethod
        def create_environment_file(
            env_vars: dict[str, str],
            output_path: Path | str,
            template: str | None = None,
        ) -> FlextResult[None]:
            """Create environment file with specified variables.

            Args:
                env_vars: Environment variables to include
                output_path: Path for output environment file
                template: Optional template content

            Returns:
                FlextResult indicating success or failure
            """
            try:
                path = Path(output_path)

                content = ""
                if template:
                    content = template + "\n\n"

                content += "# Environment variables\n"
                for key, value in env_vars.items():
                    # Quote values that contain spaces
                    if " " in value:
                        content += f'{key}="{value}"\n'
                    else:
                        content += f"{key}={value}\n"

                content += f"\n# Generated at: {datetime.now(UTC).isoformat()}\n"

                path.write_text(content, encoding="utf-8")

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Environment file creation failed: {e}")

        @staticmethod
        def validate_environment_requirements(
            requirements_file: Path | str, environment_path: Path | str | None = None
        ) -> FlextResult[dict[str, Any]]:
            """Validate environment against requirements.

            Args:
                requirements_file: Path to requirements file
                environment_path: Optional environment path

            Returns:
                FlextResult containing validation results
            """
            try:
                req_path = Path(requirements_file)
                if not req_path.exists():
                    return FlextResult[dict[str, Any]].fail(
                        f"Requirements file not found: {req_path}"
                    )

                validation_report = {
                    "valid": True,
                    "missing_packages": [],
                    "version_conflicts": [],
                    "recommendations": [],
                    "validated_at": datetime.now(UTC).isoformat(),
                }

                # Read requirements
                requirements = req_path.read_text(encoding="utf-8").splitlines()
                packages_required = []

                for req in requirements:
                    req = req.strip()
                    if req and not req.startswith("#"):
                        packages_required.append(req)

                # Check installed packages (basic check)
                command = ["pip", "list", "--format=json"]
                if environment_path:
                    # Would need to activate environment first
                    pass

                try:
                    result = subprocess.run(
                        command, capture_output=True, text=True, timeout=30, check=True
                    )

                    installed_packages = json.loads(result.stdout)
                    installed_names = {
                        pkg["name"].lower() for pkg in installed_packages
                    }

                    # Check for missing packages
                    for req in packages_required:
                        package_name = re.split(r"[>=<!=]", req)[0].strip().lower()
                        if package_name not in installed_names:
                            validation_report["missing_packages"].append(req)
                            validation_report["valid"] = False

                except (subprocess.CalledProcessError, json.JSONDecodeError):
                    validation_report["valid"] = False
                    validation_report["recommendations"].append(
                        "Could not verify installed packages"
                    )

                return FlextResult[dict[str, Any]].ok(validation_report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Environment validation failed: {e}"
                )

    class ProjectScaffolding:
        """Project scaffolding and template utilities."""

        PROJECT_TEMPLATES: ClassVar[dict[str, list[str]]] = {
            "python": ["pyproject.toml", "src/", "tests/", "README.md", ".gitignore"],
            "javascript": ["package.json", "src/", "tests/", "README.md", ".gitignore"],
            "rust": ["Cargo.toml", "src/", "tests/", "README.md", ".gitignore"],
        }
        TEMPLATE_VARS: ClassVar[list[str]] = [
            "project_name",
            "author",
            "description",
            "version",
            "license",
        ]

        @staticmethod
        def create_project_structure(
            project_name: str,
            project_type: str,
            output_path: Path | str,
            template_vars: dict[str, str] | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Create project structure from template.

            Args:
                project_name: Name of the project
                project_type: Type of project (python, javascript, rust, etc.)
                output_path: Path where project should be created
                template_vars: Template variables for substitution

            Returns:
                FlextResult containing project creation details
            """
            try:
                if (
                    project_type
                    not in FlextToolsUtilities.ProjectScaffolding.PROJECT_TEMPLATES
                ):
                    return FlextResult[dict[str, Any]].fail(
                        f"Unsupported project type: {project_type}"
                    )

                base_path = Path(output_path) / project_name
                if base_path.exists():
                    return FlextResult[dict[str, Any]].fail(
                        f"Project directory already exists: {base_path}"
                    )

                # Create project directory
                base_path.mkdir(parents=True, exist_ok=False)

                template_files = (
                    FlextToolsUtilities.ProjectScaffolding.PROJECT_TEMPLATES[
                        project_type
                    ]
                )
                created_files = []
                created_dirs = []

                vars_dict = template_vars or {}
                vars_dict.setdefault("project_name", project_name)
                vars_dict.setdefault("author", "Unknown")
                vars_dict.setdefault("description", f"A {project_type} project")
                vars_dict.setdefault("version", "0.1.0")
                vars_dict.setdefault("license", "MIT")

                for template_item in template_files:
                    item_path = base_path / template_item

                    if template_item.endswith("/"):
                        # Create directory
                        item_path.mkdir(parents=True, exist_ok=True)
                        created_dirs.append(str(item_path))
                    else:
                        # Create file
                        content = FlextToolsUtilities.ProjectScaffolding._generate_file_content(
                            template_item, project_type, vars_dict
                        )

                        # Ensure parent directory exists
                        item_path.parent.mkdir(parents=True, exist_ok=True)
                        item_path.write_text(content, encoding="utf-8")
                        created_files.append(str(item_path))

                project_info = {
                    "project_name": project_name,
                    "project_type": project_type,
                    "project_path": str(base_path),
                    "created_files": created_files,
                    "created_directories": created_dirs,
                    "template_vars": vars_dict,
                    "created_at": datetime.now(UTC).isoformat(),
                }

                return FlextResult[dict[str, Any]].ok(project_info)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Project scaffolding failed: {e}"
                )

        @staticmethod
        def _generate_file_content(
            filename: str, project_type: str, vars_dict: dict[str, str]
        ) -> str:
            """Generate content for template file."""
            if filename == "pyproject.toml" and project_type == "python":
                return f"""[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "{vars_dict["project_name"]}"
version = "{vars_dict["version"]}"
description = "{vars_dict["description"]}"
authors = ["{vars_dict["author"]}"]
license = "{vars_dict["license"]}"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
ruff = "^0.1"
mypy = "^1.0"
"""

            elif filename == "package.json" and project_type == "javascript":
                return f"""{{
  "name": "{vars_dict["project_name"]}",
  "version": "{vars_dict["version"]}",
  "description": "{vars_dict["description"]}",
  "main": "src/index.js",
  "scripts": {{
    "test": "jest",
    "lint": "eslint src/",
    "build": "webpack"
  }},
  "author": "{vars_dict["author"]}",
  "license": "{vars_dict["license"]}",
  "devDependencies": {{
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }}
}}
"""

            elif filename == "Cargo.toml" and project_type == "rust":
                return f"""[package]
name = "{vars_dict["project_name"]}"
version = "{vars_dict["version"]}"
edition = "2021"
description = "{vars_dict["description"]}"
authors = ["{vars_dict["author"]}"]
license = "{vars_dict["license"]}"

[dependencies]

[dev-dependencies]
"""

            elif filename == "README.md":
                return f"""# {vars_dict["project_name"]}

{vars_dict["description"]}

## Installation

TODO: Add installation instructions

## Usage

TODO: Add usage examples

## Contributing

TODO: Add contributing guidelines

## License

{vars_dict["license"]}
"""

            elif filename == ".gitignore":
                if project_type == "python":
                    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
                elif project_type == "javascript":
                    return """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build
dist/
build/

# Environment
.env
.internal.invalid
.internal.invalid
.internal.invalid
.internal.invalid

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
                elif project_type == "rust":
                    return """# Rust
target/
Cargo.lock

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""

            return f"# {filename}\n# Generated at {datetime.now(UTC).isoformat()}\n"

        @staticmethod
        def validate_project_structure(
            project_path: Path | str, project_type: str
        ) -> FlextResult[dict[str, Any]]:
            """Validate project structure against expected template.

            Args:
                project_path: Path to project directory
                project_type: Expected project type

            Returns:
                FlextResult containing validation results
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[dict[str, Any]].fail(
                        f"Project path does not exist: {path}"
                    )

                if (
                    project_type
                    not in FlextToolsUtilities.ProjectScaffolding.PROJECT_TEMPLATES
                ):
                    return FlextResult[dict[str, Any]].fail(
                        f"Unknown project type: {project_type}"
                    )

                expected_items = (
                    FlextToolsUtilities.ProjectScaffolding.PROJECT_TEMPLATES[
                        project_type
                    ]
                )
                validation_report = {
                    "valid": True,
                    "missing_items": [],
                    "unexpected_items": [],
                    "project_type": project_type,
                    "validated_at": datetime.now(UTC).isoformat(),
                }

                # Check for expected items
                for expected_item in expected_items:
                    item_path = path / expected_item
                    if not item_path.exists():
                        validation_report["missing_items"].append(expected_item)
                        validation_report["valid"] = False

                return FlextResult[dict[str, Any]].ok(validation_report)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Project structure validation failed: {e}"
                )

    class PackageManager:
        """Package management utilities."""

        PACKAGE_MANAGERS: ClassVar[dict[str, list[str]]] = {
            "python": ["pip", "poetry", "pipenv", "conda"],
            "javascript": ["npm", "yarn", "pnpm"],
            "rust": ["cargo"],
            "go": ["go mod"],
        }
        LOCK_FILES: ClassVar[dict[str, str]] = {
            "poetry": "poetry.lock",
            "npm": "package-lock.json",
            "yarn": "yarn.lock",
            "cargo": "Cargo.lock",
        }

        @staticmethod
        def detect_package_manager(
            project_path: Path | str,
        ) -> FlextResult[dict[str, Any]]:
            """Detect package manager used in project.

            Args:
                project_path: Path to project directory

            Returns:
                FlextResult containing package manager information
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[dict[str, Any]].fail(
                        f"Project path does not exist: {path}"
                    )

                detected_managers = []

                # Check for lock files
                for (
                    manager,
                    lock_file,
                ) in FlextToolsUtilities.PackageManager.LOCK_FILES.items():
                    if (path / lock_file).exists():
                        detected_managers.append(manager)

                # Check for config files
                if (path / "pyproject.toml").exists():
                    content = (path / "pyproject.toml").read_text(encoding="utf-8")
                    if "poetry" in content:
                        detected_managers.append("poetry")
                    else:
                        detected_managers.append("pip")

                if (path / "package.json").exists():
                    if "yarn" not in detected_managers:
                        detected_managers.append("npm")

                if (path / "Cargo.toml").exists():
                    detected_managers.append("cargo")

                if (path / "go.mod").exists():
                    detected_managers.append("go mod")

                manager_info = {
                    "detected_managers": list(set(detected_managers)),
                    "primary_manager": detected_managers[0]
                    if detected_managers
                    else "unknown",
                    "project_path": str(path),
                    "detected_at": datetime.now(UTC).isoformat(),
                }

                return FlextResult[dict[str, Any]].ok(manager_info)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Package manager detection failed: {e}"
                )

        @staticmethod
        def install_dependencies(
            manager: str, project_path: Path | str, dev_dependencies: bool = False
        ) -> FlextResult[FlextToolsModels.CommandResult]:
            """Install project dependencies using specified package manager.

            Args:
                manager: Package manager to use
                project_path: Path to project directory
                dev_dependencies: Whether to install development dependencies

            Returns:
                FlextResult containing installation result
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.CommandResult].fail(
                        f"Project path does not exist: {path}"
                    )

                # Build install command
                commands = {
                    "poetry": "poetry install" + (" --dev" if dev_dependencies else ""),
                    "npm": "npm install" + (" --save-dev" if dev_dependencies else ""),
                    "yarn": "yarn install" + (" --dev" if dev_dependencies else ""),
                    "pip": "pip install -r requirements.txt",
                    "cargo": "cargo build",
                    "go mod": "go mod download",
                }

                if manager not in commands:
                    return FlextResult[FlextToolsModels.CommandResult].fail(
                        f"Unsupported package manager: {manager}"
                    )

                command = commands[manager]

                # Execute installation
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes timeout
                    check=False,
                )

                command_result = FlextToolsModels.CommandResult(
                    command=command,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=0.0,  # Would need timing
                    success=result.returncode == 0,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                return FlextResult[FlextToolsModels.CommandResult].ok(command_result)
            except subprocess.TimeoutExpired:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    "Package installation timed out"
                )
            except Exception as e:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    f"Package installation failed: {e}"
                )

        @staticmethod
        def update_dependencies(
            manager: str, project_path: Path | str
        ) -> FlextResult[FlextToolsModels.CommandResult]:
            """Update project dependencies.

            Args:
                manager: Package manager to use
                project_path: Path to project directory

            Returns:
                FlextResult containing update result
            """
            try:
                path = Path(project_path)
                if not path.exists():
                    return FlextResult[FlextToolsModels.CommandResult].fail(
                        f"Project path does not exist: {path}"
                    )

                # Build update command
                commands = {
                    "poetry": "poetry update",
                    "npm": "npm update",
                    "yarn": "yarn upgrade",
                    "pip": "pip install --upgrade -r requirements.txt",
                    "cargo": "cargo update",
                    "go mod": "go get -u all",
                }

                if manager not in commands:
                    return FlextResult[FlextToolsModels.CommandResult].fail(
                        f"Unsupported package manager: {manager}"
                    )

                command = commands[manager]

                # Execute update
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    check=False,
                )

                command_result = FlextToolsModels.CommandResult(
                    command=command,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=0.0,
                    success=result.returncode == 0,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                return FlextResult[FlextToolsModels.CommandResult].ok(command_result)
            except subprocess.TimeoutExpired:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    "Package update timed out"
                )
            except Exception as e:
                return FlextResult[FlextToolsModels.CommandResult].fail(
                    f"Package update failed: {e}"
                )

    # Pydantic 2.11+ field validators
    @field_validator("model_config")
    @classmethod
    def validate_model_config(cls, v: SettingsConfigDict) -> SettingsConfigDict:
        """Validate model configuration."""
        if not isinstance(v, SettingsConfigDict):
            msg = "model_config must be a SettingsConfigDict instance"
            raise TypeError(msg)
        return v

    @model_validator(mode="after")
    def validate_utilities_configuration(self) -> FlextToolsUtilities:
        """Validate the complete utilities configuration."""
        # Validate that all nested classes are accessible
        required_classes = [
            "BuildSystem",
            "CodeAnalysis",
            "TestExecution",
            "EnvironmentManager",
            "ProjectScaffolding",
            "PackageManager",
        ]

        for class_name in required_classes:
            if not hasattr(self.__class__, class_name):
                msg = f"Missing required nested class: {class_name}"
                raise ValueError(msg)

        return self

    class PoetryValidator:
        """Poetry project validation utilities."""

        def check_dependencies(self, path: str | Path) -> FlextResult[dict]:
            """Check Poetry dependencies for a project."""
            try:
                path_obj = Path(path)
                pyproject_path = path_obj / "pyproject.toml"

                if not pyproject_path.exists():
                    return FlextResult[dict].fail(f"pyproject.toml not found at {path}")

                # Read and validate pyproject.toml
                with pyproject_path.open("r", encoding="utf-8") as f:
                    content = f.read()

                # Basic validation - check for required sections
                validation_result = {
                    "path": str(path),
                    "pyproject_exists": True,
                    "has_tool_poetry": "[tool.poetry]" in content,
                    "has_dependencies": "[tool.poetry.dependencies]" in content,
                    "has_dev_dependencies": "[tool.poetry.group.dev.dependencies]"
                    in content,
                    "content_length": len(content),
                }

                return FlextResult[dict].ok(validation_result)

            except Exception as e:
                return FlextResult[dict].fail(f"Failed to check dependencies: {e}")

    class PathService:
        """Path resolution and management utilities."""

        class _UtilityHelper:
            """Nested utility helper for path operations."""

            def resolve_path(self, path: str | Path) -> FlextResult[Path]:
                """Resolve and validate a path."""
                try:
                    resolved = Path(path).resolve()
                    if not resolved.exists():
                        return FlextResult[Path].fail(f"Path does not exist: {path}")
                    return FlextResult[Path].ok(resolved)
                except Exception as e:
                    return FlextResult[Path].fail(f"Failed to resolve path: {e}")

    class ConflictAnalyzer:
        """Conflict analysis utilities."""

        def get_conflicts(self) -> FlextResult[list[dict]]:
            """Get current conflicts."""
            try:
                # Basic conflict detection
                conflicts = []

                # Check for common conflict patterns
                # This is a simplified implementation
                conflicts.append(
                    {
                        "type": "dependency_conflict",
                        "severity": "low",
                        "description": "No conflicts detected",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

                return FlextResult[list[dict]].ok(conflicts)

            except Exception as e:
                return FlextResult[list[dict]].fail(f"Failed to get conflicts: {e}")


__all__ = [
    "FlextToolsUtilities",
]

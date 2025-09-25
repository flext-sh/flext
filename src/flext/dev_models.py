"""FLEXT Development Tools Models - Single Responsibility Module.

Enterprise-grade development models using cutting-edge Python 3.13 features and
Pydantic v2 advanced patterns including discriminated unions, generic constraints,
and modern validation for development workflow automation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated, Literal, Self, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.functional_validators import BeforeValidator

from flext.project_types import FlextProjectTypes
from flext.workspace_service import create_workspace_service
from flext_core import (
    FlextModels,
    FlextResult,
    FlextTypes,
)

# Modern type system with generic constraints
T = TypeVar("T", bound=BaseModel)


def validate_project_path(v: str) -> str:
    """Validate project path using workspace service."""
    # Lazy import to avoid circular dependency
    workspace_service = create_workspace_service()
    result: FlextResult[object] = workspace_service.validate_workspace_path(v)
    if result.is_failure:
        raise ValueError(result.error)
    return str(result.value)


ProjectPath = Annotated[str, BeforeValidator(validate_project_path)]


class FlextAdvancedDevModels:
    """Advanced development models using flext-core as SOURCE OF TRUTH."""

    # FLEXT-CORE INTEGRATION: Use BaseModel with flext-core patterns
    class DevOperationContext(BaseModel):
        """Development operation context using Pydantic BaseModel."""

        # Additional dev-specific fields beyond base Config
        operation_id: UUID = Field(
            default_factory=uuid4, description="Operation identifier"
        )
        workspace_root: ProjectPath = Field(..., description="Workspace root path")
        parallel_workers: int = Field(4, ge=1, le=16, description="Parallel workers")

        # Use config from FlextModels.Config (timeout_seconds already exists as timeout_seconds)

    # FLEXT-CORE INTEGRATION: Use FlextModels.Value for immutable operations
    class DevOperation(FlextModels.Value, ABC):
        """Abstract base for all development operations using flext-core Value."""

        operation_id: str = Field(
            default_factory=lambda: f"op_{uuid4().hex[:8]}",
            description="Unique operation identifier",
        )
        context: FlextAdvancedDevModels.DevOperationContext = Field(
            ..., description="Operation context"
        )

        @abstractmethod
        def validate_prerequisites(self: Self) -> FlextResult[None]:
            """Validate operation prerequisites."""

        def validate_business_rules(self: Self) -> FlextResult[None]:
            """Implement required abstract method from FlextModels.Value."""
            return self.validate_prerequisites()

    class TestOperation(DevOperation):
        """Test execution operation with advanced configuration."""

        type: Literal["test"] = "test"
        project_filter: str | None = Field(None, description="Project name filter")
        test_types: list[Literal["unit", "integration", "e2e"]] = Field(
            default=["unit"], description="Test types to execute"
        )
        coverage_enabled: bool = Field(
            default=True, description="Enable coverage reporting"
        )
        coverage_threshold: float = Field(
            default=80.0, ge=0.0, le=100.0, description="Coverage threshold"
        )
        parallel_execution: bool = Field(
            default=True, description="Enable parallel execution"
        )

        @field_validator("test_types")
        @classmethod
        def validate_test_types(cls, v: list[str]) -> list[str]:
            """Validate test types."""
            if not v:
                msg = "At least one test type must be specified"
                raise ValueError(msg)
            return v

        def validate_prerequisites(self: Self) -> FlextResult[None]:
            """Validate test operation prerequisites."""
            # Check if pytest is available
            try:
                # Use full path to avoid subprocess warning
                python_path = shutil.which("python") or "python"
                subprocess.run(
                    [python_path, "-m", "pytest", "--version"],
                    capture_output=True,
                    check=True,
                    timeout=10,
                )
                return FlextResult[None].ok(None)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return FlextResult[None].fail("pytest is not available or not working")

    class LintOperation(DevOperation):
        """Code quality operation with advanced configuration."""

        type: Literal["lint"] = "lint"
        tools: list[Literal["ruff", "mypy", "bandit", "pyright"]] = Field(
            default=["ruff", "mypy"], description="Linting tools to run"
        )
        fix_issues: bool = Field(default=False, description="Automatically fix issues")
        strict_mode: bool = Field(default=True, description="Enable strict mode")

        @model_validator(mode="after")
        def validate_lint_config(self: Self) -> FlextAdvancedDevModels.LintOperation:
            """Validate linting configuration."""
            if "mypy" in self.tools and "pyright" in self.tools:
                msg = "Cannot run both mypy and pyright simultaneously"
                raise ValueError(msg)
            return self

        def validate_prerequisites(self: Self) -> FlextResult[None]:
            """Validate linting prerequisites."""
            missing_tools: list[object] = []
            for tool in self.tools:
                try:
                    subprocess.run(
                        [tool, "--version"], capture_output=True, check=True, timeout=10
                    )
                except (
                    subprocess.CalledProcessError,
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                ):
                    missing_tools.append(tool)

            if missing_tools:
                return FlextResult[None].fail(
                    f"Missing tools: {', '.join(missing_tools)}"
                )
            return FlextResult[None].ok(None)

    class FormatOperation(DevOperation):
        """Code formatting operation."""

        type: Literal["format"] = "format"
        formatters: list[Literal["ruff", "black", "isort", "gofmt"]] = Field(
            default=["ruff"], description="Formatting tools to use"
        )
        check_only: bool = Field(
            default=False, description="Check formatting without changes"
        )

        def validate_prerequisites(self: Self) -> FlextResult[None]:
            """Validate formatting prerequisites."""
            missing_formatters: list[object] = []
            for formatter in self.formatters:
                try:
                    if formatter == "gofmt":
                        subprocess.run(
                            [formatter, "-help"],
                            capture_output=True,
                            check=False,
                            timeout=5,
                        )
                    else:
                        subprocess.run(
                            [formatter, "--version"],
                            capture_output=True,
                            check=True,
                            timeout=10,
                        )
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    missing_formatters.append(formatter)

            if missing_formatters:
                return FlextResult[None].fail(
                    f"Missing formatters: {', '.join(missing_formatters)}"
                )
            return FlextResult[None].ok(None)

    # Discriminated Union for operations
    OperationUnion = Annotated[
        TestOperation | LintOperation | FormatOperation,
        Field(discriminator="type", description="Development operation union"),
    ]

    # FLEXT-CORE INTEGRATION: Use FlextModels.Value for immutable project info
    class ProjectInfo(FlextModels.Value):
        """Project information with type detection using flext-core Value."""

        name: str = Field(..., min_length=1, max_length=100)
        path: ProjectPath = Field(..., description="Project path")
        project_type: FlextTypes.Project.ProjectType = Field(
            ..., description="Detected project type"
        )
        has_tests: bool = Field(default=False, description="Has test directory")
        has_pyproject: bool = Field(default=False, description="Has pyproject.toml")
        has_go_mod: bool = Field(default=False, description="Has go.mod file")
        test_count: int = Field(0, ge=0, description="Number of test files")

        @model_validator(mode="after")
        def validate_project_consistency(self: Self) -> FlextAdvancedDevModels.ProjectInfo:
            """Validate project type consistency."""
            path = Path(self.path)

            # Validate Python projects
            if self.project_type == FlextProjectTypes.ProjectType.PYTHON:
                if not self.has_pyproject and not (path / "setup.py").exists():
                    msg = "Python projects must have pyproject.toml or setup.py"
                    raise ValueError(msg)

            # Validate Go projects
            elif (
                self.project_type == FlextProjectTypes.ProjectType.GO
                and not self.has_go_mod
            ):
                msg = "Go projects must have go.mod file"
                raise ValueError(msg)

            return self

        def validate_business_rules(self: Self) -> FlextResult[None]:
            """Implement required abstract method from FlextModels.Value."""
            try:
                # Project consistency validation handled by model_validator
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Project validation failed: {e}")

    # FLEXT-CORE INTEGRATION: Use FlextModels.Value for immutable result
    class OperationResult(FlextModels.Value):
        """Operation execution result using flext-core Value."""

        operation_id: str = Field(..., description="Operation identifier")
        status: str = Field(..., description="Execution status")
        duration_seconds: float = Field(..., ge=0, description="Execution duration")
        exit_code: int = Field(..., description="Exit code")
        stdout_lines: int = Field(0, ge=0, description="Standard output line count")
        stderr_lines: int = Field(0, ge=0, description="Standard error line count")
        artifacts: dict[str, object] = Field(
            default_factory=dict, description="Operation artifacts"
        )

        @field_validator("duration_seconds")
        @classmethod
        def validate_duration(cls, v: float) -> float:
            """Validate duration is reasonable."""
            max_duration_seconds = 3600  # 1 hour
            if v > max_duration_seconds:
                msg = "Operation duration exceeds reasonable limits"
                raise ValueError(msg)
            return v

        def validate_business_rules(self: Self) -> FlextResult[None]:
            """Implement required abstract method from FlextModels.Value."""
            try:
                # Duration validation handled by field_validator
                if self.exit_code < 0:
                    return FlextResult[None].fail(
                        "Invalid exit code: must be non-negative"
                    )
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(
                    f"Operation result validation failed: {e}"
                )


__all__ = [
    "FlextAdvancedDevModels",
    "FlextProjectTypes",
    "ProjectPath",
]

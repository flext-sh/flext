"""FlextTools types extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes


class FlextToolsTypes(FlextTypes):
    """FlextTools types namespace extending flext-core."""

    class GitConfig(FlextTypes.Dict):
        """Git operation configuration."""

        repo_path: str
        author_name: str
        author_email: str
        dry_run: bool
        temp_path: str | None

    class OptimizationConfig(FlextTypes.Dict):
        """Module optimization configuration."""

        batch_size: int
        dry_run: bool
        verbose: bool
        force: bool
        project_type: str  # "library" or "tool"

    class QualityConfig(FlextTypes.Dict):
        """Quality check configuration."""

        lint_enabled: bool
        type_check_enabled: bool
        coverage_min: int
        strict_mode: bool

    class ValidationConfig(FlextTypes.Dict):
        """Validation configuration."""

        check_structure: bool
        check_dependencies: bool
        check_patterns: bool

    class AnalysisConfig(FlextTypes.Dict):
        """Architecture analysis configuration."""

        check_violations: bool
        check_complexity: bool
        check_imports: bool

    class DependencyConfig(FlextTypes.Dict):
        """Dependency management configuration."""

        sync_enabled: bool
        consolidate_enabled: bool
        validate_enabled: bool

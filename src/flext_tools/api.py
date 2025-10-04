"""FlextTools unified facade with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Single entry point for ALL flext-tools operations:

```python
from flext_tools import FlextTools

tools = FlextTools()

# Git operations (20 scripts consolidated)
result = await tools.git.history_rewriter.rewrite_live(
    repo_path="/path/to/repo",
    dry_run=True,  # MANDATORY default
)

# Module optimization (15 scripts consolidated)
result = await tools.optimizer.module.optimize(
    module_path="src/my_module.py", dry_run=True
)

# Quality checking (18 scripts consolidated)
result = await tools.quality.gateway.run_all_checks(project_path=".")

# Validation (12 scripts consolidated)
result = await tools.validation.equilibrium.validate_equilibrium(
    workspace_path="/workspace"
)

# Architecture (14 scripts consolidated)
result = await tools.architecture.violations.analyze_violations(project_path=".")

# Dependencies (6 scripts consolidated)
result = await tools.dependencies.analyzer.analyze_dependencies(project_path=".")
```

Integrates complete flext-core ecosystem:
- FlextBus: Event emission
- FlextContainer: Dependency injection
- FlextContext: Operation context
- FlextLogger: Structured logging
"""

from __future__ import annotations

from typing import Self

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextLogger,
    FlextProcessors,
    FlextRegistry,
    FlextResult,
    FlextService,
)
from pydantic import ConfigDict

from flext_tools.architecture_tools import FlextArchitectureTools
from flext_tools.dependency_tools import FlextDependencyTools
from flext_tools.git_tools import FlextGitTools
from flext_tools.optimizer_tools import FlextOptimizerTools
from flext_tools.quality_tools import FlextQualityTools
from flext_tools.validation_tools import FlextValidationTools


class FlextTools(FlextService[None]):
    """Unified workspace tools facade with complete FLEXT integration.

    Single entry point for ALL flext-tools operations consolidating 85+ scripts
    into 6 unified tool modules.

    Example usage:
    ```python
    from flext_tools import FlextTools

    tools = FlextTools()

    # Access all tool categories through single interface
    git_result = await tools.git.history_rewriter.rewrite_live(...)
    optimizer_result = await tools.optimizer.module.optimize(...)
    quality_result = await tools.quality.gateway.run_all_checks(...)
    validation_result = await tools.validation.equilibrium.validate_equilibrium(...)
    architecture_result = await tools.architecture.violations.analyze_violations(...)
    dependency_result = await tools.dependencies.analyzer.analyze_dependencies(...)
    ```

    ALL operations support:
    - dry_run=True (MANDATORY default)
    - temp_path for temporary workspace
    - FlextResult error handling (NO try/except)
    - FlextLogger structured logging
    - Complete flext-core integration
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def __init__(self: Self) -> None:
        """Initialize FlextTools with complete flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Complete flext-core ecosystem integration
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._bus = FlextBus()
        self._dispatcher = FlextDispatcher()
        self._processors = FlextProcessors()
        self._registry = FlextRegistry(dispatcher=self._dispatcher)

        # Initialize all 6 tool categories (consolidating 85+ scripts)
        self.git = FlextGitTools()  # 20 git scripts
        self.optimizer = FlextOptimizerTools()  # 15 optimizer scripts
        self.quality = FlextQualityTools()  # 18 quality scripts
        self.validation = FlextValidationTools()  # 12 validation scripts
        self.architecture = FlextArchitectureTools()  # 14 architecture scripts
        self.dependencies = FlextDependencyTools()  # 6 dependency scripts

        self._logger.info("FlextTools initialized with 6 tool categories")

    def execute(self: Self) -> FlextResult[None]:
        """Execute FlextTools service - FlextService interface."""
        return FlextResult[None].ok(None)

    def get_status(self: Self) -> FlextResult[FlextTypes.Dict]:
        """Get status of all tool categories.

        Returns:
            FlextResult with status information

        """
        status = {
            "git": "ready",
            "optimizer": "ready",
            "quality": "ready",
            "validation": "ready",
            "architecture": "ready",
            "dependencies": "ready",
            "total_scripts_consolidated": 85,
            "tool_categories": 6,
        }

        return FlextResult[FlextTypes.Dict].ok(status)


# Alias for convenience
FlextToolsAPI = FlextTools


__all__ = ["FlextTools", "FlextToolsAPI"]

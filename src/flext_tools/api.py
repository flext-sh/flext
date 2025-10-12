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
- FlextCore.Bus: Event emission
- FlextCore.Container: Dependency injection
- FlextCore.Context: Operation context
- FlextCore.Logger: Structured logging
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextCore
from pydantic import ConfigDict

from flext_tools.architecture_tools import FlextArchitectureTools
from flext_tools.dependency_tools import FlextDependencyTools
from flext_tools.git_tools import FlextGitTools
from flext_tools.optimizer_tools import FlextOptimizerTools
from flext_tools.quality_tools import FlextQualityTools
from flext_tools.validation_tools import FlextValidationTools


class FlextTools(FlextCore.Service[None]):
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
    - FlextCore.Result error handling (NO try/except)
    - FlextCore.Logger structured logging
    - Complete flext-core integration
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def __init__(self: Self) -> None:
        """Initialize FlextTools with complete flext-core integration."""
        super().__init__()
        self.logger = FlextCore.Logger(__name__)

        # Complete flext-core ecosystem integration
        self._container = FlextCore.Container.get_global()
        self._context = FlextCore.Context()
        self._bus = FlextCore.Bus()
        self._dispatcher = FlextCore.Dispatcher()
        self._processors = FlextCore.Processors()
        self._registry = FlextCore.Registry(dispatcher=self._dispatcher)

        # Initialize all 6 tool categories (consolidating 85+ scripts)
        self.git = FlextGitTools()  # 20 git scripts
        self.optimizer = FlextOptimizerTools()  # 15 optimizer scripts
        self.quality = FlextQualityTools()  # 18 quality scripts
        self.validation = FlextValidationTools()  # 12 validation scripts
        self.architecture = FlextArchitectureTools()  # 14 architecture scripts
        self.dependencies = FlextDependencyTools()  # 6 dependency scripts

        self.logger.info("FlextTools initialized with 6 tool categories")

    def execute(self: Self) -> FlextCore.Result[None]:
        """Execute FlextTools service - FlextCore.Service interface."""
        return FlextCore.Result[None].ok(None)

    def get_status(self: Self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get status of all tool categories.

        Returns:
            FlextCore.Result with status information

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

        return FlextCore.Result[FlextCore.Types.Dict].ok(status)


# Alias for convenience
FlextToolsAPI = FlextTools


__all__ = ["FlextTools", "FlextToolsAPI"]

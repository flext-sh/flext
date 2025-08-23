"""FLEXT Tools Quality - Enterprise Quality Integration Bridge.

**ARCHITECTURAL DECISION: DELEGATION TO flext-quality**

This module serves as an INTEGRATION BRIDGE to the authoritative flext-quality
service, which provides the complete quality analysis implementation with Django
+ Clean Architecture. This delegation pattern eliminates code duplication and
establishes flext-quality as the single source of truth for quality analysis.

Integration Pattern:
    flext_tools.quality (THIS MODULE) = Gateway/Bridge for workspace integration
    flext-quality (SEPARATE PROJECT) = Authoritative quality analysis service

Key Design Decisions:
    - NO duplication of quality analysis logic (delegated to flext-quality)
    - Workspace integration patterns for FLEXT ecosystem coordination
    - Bridge between workspace tools and dedicated quality service
    - Gateway patterns for CI/CD pipeline integration

Example:
    Quality analysis with proper delegation:

    >>> from flext_tools.quality import QualityBridge
    >>> from pathlib import Path
    >>>
    >>> # Bridge to authoritative flext-quality service
    >>> bridge = QualityBridge(workspace_root=Path("/workspace"))
    >>> result = bridge.delegate_to_quality_service(project_path="flext-api")
    >>>
    >>> # Integration with workspace patterns
    >>> workspace_result = bridge.validate_workspace_quality()
    >>> if workspace_result.success:
    ...     print(f"Workspace quality score: {workspace_result.value['score']}")

Architecture:
    Implements proper delegation patterns to avoid duplication while providing
    workspace-specific integration capabilities for FLEXT ecosystem coordination.

Integration:
    - Delegates ALL quality analysis to flext-quality service
    - Provides workspace integration patterns for ecosystem coordination
    - Bridges workspace tools with dedicated quality analysis service
    - Maintains consistency through proper delegation patterns

DEPRECATION NOTICE:
    Direct quality analysis functionality is deprecated in favor of delegation
    to the authoritative flext-quality service. Use QualityBridge for proper
    integration with the dedicated quality analysis service.

Author: FLEXT Development Team
Version: 2.0.0-bridge
License: MIT

"""

from flext_tools.quality.bridge import QualityBridge
from flext_tools.quality.gateway import QualityGateway  # Legacy compatibility
from flext_tools.quality.lint_fixer import GradualLintFixer  # Legacy compatibility
from flext_tools.quality.mypy_checker import MyPyChecker  # Legacy compatibility

__all__: list[str] = [
    "QualityBridge",  # Primary integration bridge
    # Legacy compatibility exports (deprecated)
    "GradualLintFixer",
    "MyPyChecker",
    "QualityGateway",
]

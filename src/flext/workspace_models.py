"""FLEXT Workspace Models - Single Responsibility Module.

Workspace models consolidated into flext-core for ecosystem consistency.
This module now provides compatibility imports from the centralized FlextModels.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import centralized models from flext-core foundation


class FlextAdvancedWorkspaceModels:
    """Workspace models using centralized flext-core foundation.

    Access models directly through FlextModels namespace:
    - FlextModels.Project
    - FlextModels.WorkspaceContext
    - FlextModels.WorkspaceInfo

    LEGACY ALIASES ELIMINATED - Use flext-core directly.
    """


__all__ = ["FlextAdvancedWorkspaceModels"]

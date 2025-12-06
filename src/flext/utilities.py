"""Utilities for flext package.

This module provides centralized utilities for the flext package,
inheriting from FlextCliUtilities and extending with workspace-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliUtilities

from flext.constants import FlextConstants
from flext.models import FlextModels
from flext.types import FlextTypes


class FlextUtilities(FlextCliUtilities):
    """Centralized utilities for flext package."""

    # Use local domain types/models/constants
    Constants = FlextConstants
    Models = FlextModels
    Types = FlextTypes


# Alias for convenience
u = FlextUtilities

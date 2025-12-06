"""Service base for flext package.

This module provides the base service class for the flext package,
inheriting from FlextCliServiceBase.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_cli import FlextCliServiceBase

from flext.constants import FlextConstants
from flext.models import FlextModels
from flext.types import FlextTypes
from flext.utilities import FlextUtilities


class FlextServiceBase(FlextCliServiceBase):
    """Base service class for flext package."""

    # Use local domain types/models/constants/utilities
    Constants: ClassVar[type[FlextConstants]] = FlextConstants
    Models: ClassVar[type[FlextModels]] = FlextModels
    Types: ClassVar[type[FlextTypes]] = FlextTypes
    Utilities: ClassVar[type[FlextUtilities]] = FlextUtilities


# Alias for convenience
s = FlextServiceBase

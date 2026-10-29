"""Config protocols for flext-workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class FlextRootProtocolsConfig(Protocol):
    """Config protocols for flext-workspace."""


__all__ = ("FlextRootProtocolsConfig",)

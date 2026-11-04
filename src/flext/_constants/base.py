"""Foundational constants definitions for the FLEXT workspace root.

Declares immutable base constants and sentinel definitions composed into
the root constants namespace ``c.Root``.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext.constants.FlextRootConstants`: Composed public constants facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootConstantsBase:
    """Base constant declarations for workspace operations.

    Provides core immutable identifiers and protocol constants required
    at the root workspace boundary.
    """


__all__ = ("FlextRootConstantsBase",)

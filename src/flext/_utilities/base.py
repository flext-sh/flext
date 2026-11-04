"""Foundational utility functions and helpers for the FLEXT workspace root.

Provides shared pure functions, conversion helpers, and common algorithms
composed into the root utility namespace ``u.Root``.

See Also:
    - ADR-001: Railway-Oriented Programming.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext.utilities.FlextRootUtilities`: Composed public utilities facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootUtilitiesBase:
    """Base utility operations and static helper methods.

    Houses general-purpose, reusable pure functions utilized across workspace
    components without creating cross-subproject dependencies.
    """


__all__ = ("FlextRootUtilitiesBase",)

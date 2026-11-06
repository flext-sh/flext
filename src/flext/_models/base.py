"""Base domain model declarations for the FLEXT workspace root.

Provides foundational model classes and mixins composed into the root
domain model namespace ``m.Root``.

See Also:
    - ADR-018: Generator Declarations.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext.models.FlextRootModels`: Composed public models facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextModelsRootBase:
    """Base domain model container for workspace root entities.

    Acts as the root class for domain entities, value objects, and payload
    schemas managed within the workspace boundary.
    """


__all__ = ("FlextModelsRootBase",)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext._models.base import FlextModelsRootBase
    from flext._models.config import FlextModelsRootConfig


__all__: tuple[str, ...] = ("FlextModelsRootBase", "FlextModelsRootConfig")

install_lazy_exports(
    __name__,
    globals(),
    {"FlextModelsRootBase": ".base", "FlextModelsRootConfig": ".config"},
    public_exports=__all__,
    deferred_members={
        "FlextModelsRootBase": (),
        "FlextModelsRootConfig": (
            "PipelinePayload",
            "PipelineStageData",
        ),
    },
)

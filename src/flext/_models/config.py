"""Config models for flext-workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext import t
from flext_infra import m


class FlextModelsRootConfig:
    """Config models for flext-workspace."""

    class PipelinePayload(m.BaseModel):
        """Pipeline payload container."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

        values: t.MutableJsonMapping = m.Field(
            default_factory=dict,
            description="Processed item values carried across pipeline stages.",
        )

    class PipelineStageData(m.BaseModel):
        """Data container for pipeline stage processing."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

        data: FlextModelsRootConfig.PipelinePayload = m.Field(
            description="Payload produced by the preceding pipeline stage.",
        )


__all__ = ("FlextModelsRootConfig",)

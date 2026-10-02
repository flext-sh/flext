"""Config models for flext-workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_infra import m, t


class FlextRootModelsConfig:
    """Config models for flext-workspace."""

    class PipelinePayload(m.BaseModel):
        """Pipeline payload container."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="allow",
        )

        values: t.JsonMapping = m.Field(
            default_factory=dict,
            description="Processed item values carried across pipeline stages.",
        )

    class PipelineStageData(m.BaseModel):
        """Data container for pipeline stage processing."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="allow",
        )

        data: FlextRootModelsConfig.PipelinePayload = m.Field(
            description="Payload produced by the preceding pipeline stage.",
        )


FlextRootModelsConfig.PipelineStageData.model_rebuild()

"""Config models for flext-workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_infra import m, t, u


class FlextRootPipelinePayload(m.BaseModel):
    """Pipeline payload container."""

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    values: t.JsonMapping = u.Field(default_factory=dict)


class FlextRootPipelineStageData(FlextRootPipelinePayload):
    """Data container for pipeline stage processing."""

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    data: FlextRootPipelinePayload = u.Field(default_factory=FlextRootPipelinePayload)


class FlextRootModelsConfig:
    """Config models for flext-workspace."""

    PipelinePayload = FlextRootPipelinePayload
    PipelineStageData = FlextRootPipelineStageData

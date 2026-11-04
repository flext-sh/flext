"""Pipeline execution and stage data models for the FLEXT workspace.

Defines validated data containers, stage payloads, and mutable mappings transferred
across linear and branched execution pipeline steps.

See Also:
    - ADR-001: Railway-Oriented Programming.
    - ADR-018: Generator Declarations.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :class:`flext._models.base.FlextModelsRootBase`: Foundational model declarations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext import t
from flext_infra import m


class FlextModelsRootConfig:
    """Namespace container for pipeline configuration and payload models.

    Groups schemas and data objects governing state exchange between pipeline
    processing components.
    """

    class PipelinePayload(m.BaseModel):
        """Carries state and processed entity values between pipeline stages.

        Enforces strict schema constraints forbidding undeclared fields while
        maintaining a typed mapping of stage results.

        Attributes:
            values: Key-value dictionary of processed items and intermediate outputs.

        """

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(extra="forbid")

        values: t.MutableJsonMapping = m.Field(
            default_factory=dict,
            description="Processed item values carried across pipeline stages.",
        )

    class PipelineStageData(m.BaseModel):
        """Encapsulates input payload for an individual pipeline execution stage.

        Guarantees that stage processors receive strongly-typed and validated
        payload instances from upstream contributors.

        Attributes:
            data: Validated payload container produced by the preceding stage.

        """

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(extra="forbid")

        data: FlextModelsRootConfig.PipelinePayload = m.Field(
            description="Payload produced by the preceding pipeline stage.",
        )


__all__ = ("FlextModelsRootConfig",)

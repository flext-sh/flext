"""Pydantic models for in-memory gRPC data representation with enterprise domain types.

These models provide strong typing and validation for the data used
within the gRPC server, using enterprise domain value objects to replace
primitive types with validated business objects.

ZERO TOLERANCE: No primitive types - all values use domain objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flx_core.domain.business_types import (
    CronExpression,
    ExecutionNumber,
    PluginName,
    RecordCount,
    ScheduleId,
    TimeoutSeconds,
    Timezone,
    Username,
)
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime

    from flx_core.domain.value_objects import (
        Duration,
        ExecutionId,
        ExecutionStatus,
        PipelineId,
        PipelineName,
    )


class PipelineGrpcModel(BaseModel):
    """Enterprise Pydantic model for gRPC Pipeline serialization with validated domain types.

    ZERO TOLERANCE: All fields use domain value objects for type safety and validation.
    Renamed from PipelineModel to avoid conflict with persistence PipelineModel.
    """

    id: PipelineId
    name: PipelineName
    description: str | None = None
    extractor: PluginName
    loader: PluginName
    transform: PluginName | None = None
    schedule: CronExpression | None = None
    is_active: bool = True
    created_by: Username = Username(value="grpc-system")
    created_at: datetime
    updated_at: datetime
    config: dict[str, object] = Field(default_factory=dict)
    timeout: TimeoutSeconds | None = None


class ExecutionModel(BaseModel):
    """Enterprise Pydantic model for in-memory Execution with validated domain types.

    ZERO TOLERANCE: All fields use domain value objects for type safety and validation.
    """

    id: ExecutionId
    pipeline_id: PipelineId
    execution_number: ExecutionNumber
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime | None = None
    triggered_by: Username | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    duration: Duration | None = None
    error_message: str | None = None
    records_processed: RecordCount | None = None


class ScheduleModel(BaseModel):
    """Enterprise Pydantic model for in-memory Schedule with validated domain types.

    ZERO TOLERANCE: All fields use domain value objects for type safety and validation.
    """

    id: ScheduleId
    pipeline_id: PipelineId
    cron_expression: CronExpression
    timezone: Timezone = Timezone(value="UTC")
    is_active: bool = True
    created_by: Username = Username(value="grpc-system")
    created_at: datetime
    updated_at: datetime


# ZERO TOLERANCE CONSOLIDATION: Backward compatibility alias for PipelineModel
# Use PipelineGrpcModel for new code, this is for legacy compatibility only
PipelineModel = PipelineGrpcModel

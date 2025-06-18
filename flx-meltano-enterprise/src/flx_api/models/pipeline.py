"""
Pipeline API models.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PipelineBase(BaseModel):
    """Base pipeline model."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    extractor: str = Field(..., min_length=1, max_length=255)
    loader: str = Field(..., min_length=1, max_length=255)
    transform: Optional[str] = Field(None, max_length=255)
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = Field(None, max_length=100)


class PipelineCreate(PipelineBase):
    """Pipeline creation model."""

    pass


class PipelineUpdate(BaseModel):
    """Pipeline update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    extractor: Optional[str] = Field(None, min_length=1, max_length=255)
    loader: Optional[str] = Field(None, min_length=1, max_length=255)
    transform: Optional[str] = Field(None, max_length=255)
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class PipelineResponse(PipelineBase):
    """Pipeline response model."""

    id: str
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_status: Optional[str] = None
    last_run: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
    }


class RunPipelineRequest(BaseModel):
    """Run pipeline request model."""

    full_refresh: bool = False
    env_vars: Optional[Dict[str, str]] = None


class ExecutionResponse(BaseModel):
    """Execution response model."""

    id: str
    pipeline_id: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    records_processed: Optional[int] = None
    triggered_by: str

    model_config = {
        "from_attributes": True,
    }

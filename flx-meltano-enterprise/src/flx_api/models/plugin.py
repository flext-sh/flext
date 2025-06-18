"""
Plugin API models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PluginInstallRequest(BaseModel):
    """Plugin installation request."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(
        ..., pattern="^(extractor|loader|transformer|orchestrator|utility)$"
    )
    variant: Optional[str] = Field(None, max_length=255)


class PluginResponse(BaseModel):
    """Plugin response model."""

    name: str
    type: str
    variant: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    installed: bool
    installed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
    }

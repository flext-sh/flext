"""
Monitoring API models.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    """Component health status."""

    healthy: bool
    message: str
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""

    healthy: bool
    components: Dict[str, ComponentHealth]
    timestamp: datetime


class SystemStatsResponse(BaseModel):
    """System statistics response."""

    active_pipelines: int
    total_executions: int
    success_rate: float
    uptime_seconds: int
    cpu_usage: float
    memory_usage: float
    active_connections: int

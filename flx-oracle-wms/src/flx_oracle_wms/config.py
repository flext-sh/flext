"""Configuration management for FLX Oracle WMS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from pathlib import Path


class PipelineDefinition(BaseModel):
    """Definition of a single pipeline."""

    name: str = Field(..., description="Pipeline name")
    description: str = Field(..., description="Pipeline description")
    streams: list[str] = Field(..., description="Streams to include in pipeline")
    schedule: str | None = Field(None, description="Cron schedule expression")
    enabled: bool = Field(True, description="Whether pipeline is enabled")
    tap_config_override: dict[str, Any] | None = Field(
        None, description="Override tap configuration for this pipeline"
    )
    target_config_override: dict[str, Any] | None = Field(
        None, description="Override target configuration for this pipeline"
    )


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    enabled: bool = Field(True, description="Enable monitoring")
    metrics_port: int = Field(9090, description="Port for metrics endpoint")
    health_check_interval: int = Field(
        60, description="Health check interval in seconds"
    )
    alert_webhook_url: str | None = Field(None, description="Webhook URL for alerts")
    log_level: str = Field("INFO", description="Logging level")


class PipelineConfig(BaseSettings):
    """Main pipeline configuration."""

    model_config = {"env_prefix": "FLX_WMS_"}

    name: str = Field("Oracle WMS Integration", description="Integration name")
    tap_config_path: Path = Field(..., description="Path to tap configuration")
    target_config_path: Path = Field(..., description="Path to target configuration")
    state_path: Path | None = Field(None, description="Path to state file")
    catalog_path: Path | None = Field(None, description="Path to catalog file")
    pipelines: list[PipelineDefinition] = Field(
        default_factory=list, description="Pipeline definitions"
    )
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)  # type: ignore[arg-type]
    max_parallel_pipelines: int = Field(
        2, description="Maximum parallel pipeline executions"
    )
    retry_count: int = Field(3, description="Number of retries on failure")
    retry_delay: int = Field(60, description="Delay between retries in seconds")


class RuntimeConfig(BaseModel):
    """Runtime configuration for pipeline execution."""

    pipeline_name: str
    tap_config: dict[str, Any]
    target_config: dict[str, Any]
    state: dict[str, Any] | None = None
    catalog: dict[str, Any] | None = None
    dry_run: bool = False
    debug: bool = False

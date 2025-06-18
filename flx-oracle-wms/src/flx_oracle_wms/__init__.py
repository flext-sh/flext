"""FLX Oracle WMS - Unified integration for Oracle Warehouse Management System."""

from __future__ import annotations

from flx_oracle_wms.config import PipelineConfig
from flx_oracle_wms.orchestrator import WMSOrchestrator


__version__ = "1.0.0"
__all__ = ["PipelineConfig", "WMSOrchestrator"]

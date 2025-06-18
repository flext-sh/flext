"""Inventory synchronization pipeline."""

from __future__ import annotations

from typing import Any

from flx_oracle_wms.config import PipelineDefinition


class InventorySyncPipeline:
    """Pre-configured pipeline for inventory synchronization."""

    @staticmethod
    def get_definition() -> PipelineDefinition:
        """Get pipeline definition."""
        return PipelineDefinition(
            name="inventory_sync",
            description="Synchronize inventory data with KPI calculations and alerts",
            streams=[
                "inventory",
                "lots",
                "locations",
                "cycle_counts",
            ],
            schedule="0 */6 * * *",  # Every 6 hours
            enabled=True,
            tap_config_override={},
            target_config_override={
                "enable_kpi_calculation": True,
                "enable_alerts": True,
                "expiry_alert_days": 30,
            },
        )

    @staticmethod
    def get_custom_transformations() -> list[dict[str, Any]]:
        """Get custom transformations for this pipeline."""
        return [
            {
                "name": "enrich_inventory_location",
                "description": "Add location details to inventory records",
                "type": "join",
                "config": {
                    "left_stream": "inventory",
                    "right_stream": "locations",
                    "join_keys": ["location_id"],
                },
            },
            {
                "name": "calculate_inventory_value",
                "description": "Calculate total inventory value",
                "type": "aggregation",
                "config": {
                    "stream": "inventory",
                    "group_by": ["item_id", "location_id"],
                    "aggregations": {
                        "total_quantity": "sum(quantity)",
                        "total_value": "sum(quantity * unit_cost)",
                    },
                },
            },
        ]

    @staticmethod
    def get_alerts_config() -> dict[str, Any]:
        """Get alerts configuration for this pipeline."""
        return {
            "low_stock_threshold": {
                "enabled": True,
                "threshold_type": "percentage",
                "threshold_value": 20,  # 20% of max stock
                "severity": "warning",
                "notification_channels": ["email", "webhook"],
            },
            "expiry_alerts": {
                "enabled": True,
                "days_before_expiry": [90, 60, 30, 7, 1],
                "severity_mapping": {
                    90: "info",
                    60: "warning",
                    30: "high",
                    7: "critical",
                    1: "emergency",
                },
            },
            "cycle_count_variance": {
                "enabled": True,
                "variance_threshold": 5,  # 5% variance
                "consecutive_failures": 3,
                "severity": "high",
            },
        }

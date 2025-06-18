#!/usr/bin/env python3
"""Basic pipeline example for FLX Oracle WMS."""

from pathlib import Path

from flx_oracle_wms import WMSOrchestrator
from flx_oracle_wms.config import PipelineConfig, PipelineDefinition


def create_basic_pipeline() -> None:
    """Create a basic inventory synchronization pipeline."""
    # Define pipeline configuration
    config = PipelineConfig(
        name="Basic WMS Pipeline",
        tap_config_path=Path("./config/tap_config.json"),
        target_config_path=Path("./config/target_config.json"),
        state_path=Path("./state.json"),
        pipelines=[
            PipelineDefinition(
                name="inventory_sync",
                description="Synchronize inventory data with KPI calculation",
                streams=["inventory", "lots", "locations"],
                enabled=True,
                target_config_override={
                    "enable_kpi_calculation": True,
                    "enable_alerts": True,
                    "expiry_alert_days": 30,
                },
            )
        ],
    )

    # Create orchestrator
    orchestrator = WMSOrchestrator(config)

    # Validate configuration
    valid, errors = orchestrator.validate_configuration()
    if not valid:
        for _error in errors:
            pass
        return

    # Run pipeline
    result = orchestrator.run_pipeline("inventory_sync")

    # Display results
    if result["status"] == "success":
        pass


def create_multi_pipeline():
    """Create multiple pipelines for different business areas."""
    return PipelineConfig(
        name="Multi-Pipeline WMS Integration",
        tap_config_path=Path("./config/tap_config.json"),
        target_config_path=Path("./config/target_config.json"),
        state_path=Path("./state.json"),
        pipelines=[
            # Inventory management pipeline
            PipelineDefinition(
                name="inventory_management",
                description="Complete inventory management with alerts",
                streams=["inventory", "lots", "locations", "cycle_counts"],
                schedule="0 */6 * * *",  # Every 6 hours
                enabled=True,
            ),
            # Order processing pipeline
            PipelineDefinition(
                name="order_fulfillment",
                description="Order processing and fulfillment tracking",
                streams=["orders", "order_lines", "shipments", "allocations"],
                schedule="0 * * * *",  # Every hour
                enabled=True,
            ),
            # Warehouse operations pipeline
            PipelineDefinition(
                name="warehouse_operations",
                description="Monitor warehouse productivity",
                streams=["tasks", "workers", "equipment"],
                schedule="0 8,12,16,20 * * *",  # 4 times per day
                enabled=True,
            ),
        ],
    )


def run_all_pipelines_example() -> None:
    """Example of running all pipelines."""
    config = create_multi_pipeline()
    orchestrator = WMSOrchestrator(config)

    results = orchestrator.run_all_pipelines()

    # Display summary
    for result in results:
        if result["status"] == "success":
            pass


if __name__ == "__main__":
    # Example 1: Basic pipeline
    create_basic_pipeline()

    # Example 2: Multiple pipelines
    run_all_pipelines_example()

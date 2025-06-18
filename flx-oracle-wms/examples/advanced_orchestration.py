#!/usr/bin/env python3
"""Advanced orchestration examples for FLX Oracle WMS."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any

from flx_oracle_wms import WMSOrchestrator
from flx_oracle_wms.config import PipelineConfig, PipelineDefinition
from flx_oracle_wms.monitoring import PipelineMonitor


class AdvancedWMSOrchestration:
    """Advanced orchestration patterns for WMS integration."""

    def __init__(self, config_path: str) -> None:
        """Initialize with configuration."""
        self.config = PipelineConfig.parse_file(config_path)
        self.orchestrator = WMSOrchestrator(self.config)
        self.monitor = PipelineMonitor()

    async def run_parallel_pipelines(self) -> None:
        """Run multiple pipelines in parallel with monitoring."""
        # Start monitoring
        start_time = datetime.now()

        # Run pipelines asynchronously
        results = await self.orchestrator.run_all_pipelines_async()

        # Calculate execution time
        (datetime.now() - start_time).total_seconds()

        # Display results

        for result in results:
            if result["status"] == "success":
                pass

    def conditional_pipeline_execution(self) -> None:
        """Execute pipelines based on conditions."""
        # Check current inventory levels
        inventory_status = self.monitor.get_pipeline_status("inventory_sync")

        # Decide which pipeline to run
        if inventory_status.get("last_run"):
            last_run = datetime.fromisoformat(inventory_status["last_run"])
            hours_since_last_run = (datetime.now() - last_run).total_seconds() / 3600

            if hours_since_last_run > 6:
                self.orchestrator.run_pipeline("inventory_sync")

        # Check for critical alerts
        metrics = self.monitor.get_metrics()
        if metrics.get("failed_runs", 0) > 5:
            self._run_diagnostic_pipeline()

    def _run_diagnostic_pipeline(self) -> None:
        """Run a diagnostic pipeline to check system health."""
        # Create a minimal pipeline for diagnostics
        diag_pipeline = PipelineDefinition(
            name="diagnostic",
            description="System health check",
            streams=["system_info"],  # Minimal stream
            enabled=True,
        )

        # Run with special configuration
        runtime_config = self.orchestrator._create_runtime_config(diag_pipeline)
        runtime_config.tap_config["timeout"] = 10  # Quick timeout

        self.orchestrator._execute_pipeline(runtime_config)

    def pipeline_with_retry(self, pipeline_name: str, max_retries: int = 3):
        """Run pipeline with automatic retry on failure."""
        retry_count = 0
        backoff_seconds = 60

        while retry_count < max_retries:

            result = self.orchestrator.run_pipeline(pipeline_name)

            if result["status"] == "success":
                return result

            retry_count += 1
            if retry_count < max_retries:
                asyncio.run(asyncio.sleep(backoff_seconds))
                backoff_seconds *= 2  # Exponential backoff

        return result

    def create_dynamic_pipeline(self, stream_criteria: dict[str, Any]):
        """Create pipeline dynamically based on criteria."""
        # Discover available streams
        import subprocess

        discover_cmd = [
            "tap-oracle-wms",
            "--config",
            str(self.config.tap_config_path),
            "--discover",
        ]

        result = subprocess.run(discover_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            catalog = json.loads(result.stdout)

            # Filter streams based on criteria
            selected_streams = []
            for stream in catalog.get("streams", []):
                stream_name = stream.get("stream")

                # Apply criteria (example: only tables with updates)
                metadata = stream.get("metadata", [{}])[0].get("metadata", {})
                if metadata.get("forced-replication-method") == "INCREMENTAL":
                    selected_streams.append(stream_name)

            # Create dynamic pipeline
            return PipelineDefinition(
                name="dynamic_pipeline",
                description="Dynamically created pipeline",
                streams=selected_streams,
                enabled=True,
            )

        return None

    async def scheduled_execution_demo(self) -> None:
        """Demonstrate scheduled execution patterns."""
        # Define execution schedule
        schedule = {
            "inventory_sync": timedelta(hours=6),
            "order_processing": timedelta(hours=1),
            "warehouse_analytics": timedelta(hours=4),
        }

        # Track last execution times
        last_execution = {}

        # Run for demonstration (normally would be infinite loop)
        for _ in range(3):
            current_time = datetime.now()

            for pipeline_name, interval in schedule.items():
                last_run = last_execution.get(pipeline_name)

                if last_run is None or (current_time - last_run) >= interval:

                    # Run asynchronously
                    await self.orchestrator.run_pipeline_async(pipeline_name)

                    # Update last execution time
                    last_execution[pipeline_name] = current_time

            # Wait before next check (shortened for demo)
            await asyncio.sleep(5)


def monitoring_dashboard_example() -> None:
    """Example of creating a monitoring dashboard."""
    monitor = PipelineMonitor()

    # Get all pipeline statuses
    statuses = monitor.get_all_pipeline_statuses()

    for _status in statuses.values():
        pass

    # Get aggregate metrics
    metrics = monitor.get_metrics()

    if metrics.get("average_duration_seconds"):
        pass


async def main() -> None:
    """Run advanced orchestration examples."""
    # Note: These examples assume configuration files exist
    # In practice, you would create these first

    # Example 1: Parallel execution
    # orchestrator = AdvancedWMSOrchestration("./config/pipeline_config.json")
    # await orchestrator.run_parallel_pipelines()

    # Example 2: Conditional execution
    # orchestrator.conditional_pipeline_execution()

    # Example 3: Retry logic
    # orchestrator.pipeline_with_retry("inventory_sync", max_retries=3)

    # Example 4: Monitoring dashboard
    monitoring_dashboard_example()


if __name__ == "__main__":
    asyncio.run(main())

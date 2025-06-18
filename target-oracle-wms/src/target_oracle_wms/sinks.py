"""Oracle WMS target sinks."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from singer_sdk.sinks import BatchSink

if TYPE_CHECKING:
    from singer_sdk.plugin_base import PluginBase


class WMSBaseSink(BatchSink):
    """Base sink for Oracle WMS data."""

    max_size = 1000  # Max batch size

    def __init__(
        self,
        target: PluginBase,
        stream_name: str,
        schema: dict,
        key_properties: list[str] | None,
    ) -> None:
        """Initialize sink."""
        super().__init__(target, stream_name, schema, key_properties)
        self._business_manager = None
        self._setup_output_path()

    def _setup_output_path(self) -> None:
        """Setup output directory."""
        output_path = Path(self.config.get("output_path", "./output"))
        output_path.mkdir(parents=True, exist_ok=True)
        self.output_path = output_path

    @property
    def business_manager(self) -> Any:
        """Get business logic manager for this sink."""
        if self._business_manager is None:
            self._business_manager = self._create_business_manager()
        return self._business_manager

    def _create_business_manager(self) -> Any:
        """Create business logic manager. Override in subclasses."""
        return None

    def process_batch(self, context: dict) -> None:
        """Process a batch of records."""
        records = context.get("records", [])
        if not records:
            return

        # Transform records if business logic is enabled
        if self.config.get("enable_kpi_calculation", True) and self.business_manager:
            records = self._apply_business_logic(records)

        # Write to configured output
        self._write_batch(records)

        # Update state
        self._update_state(context)

    def _apply_business_logic(self, records: list[dict]) -> list[dict]:
        """Apply business logic transformations. Override in subclasses."""
        return records

    def _write_batch(self, records: list[dict]) -> None:
        """Write batch to output."""
        # Write to file
        if self.config.get("output_format") == "json":
            self._write_json(records)
        elif self.config.get("output_format") == "csv":
            self._write_csv(records)

        # Write to database if configured
        if self.config.get("database_url"):
            self._write_to_database(records)

        # Write to WMS API if configured for updates
        if self.config.get("enable_wms_updates", False):
            self._write_to_wms(records)

    def _write_json(self, records: list[dict]) -> None:
        """Write records to JSON file."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{self.stream_name}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(records, f, indent=2, default=str)

    def _write_csv(self, records: list[dict]) -> None:
        """Write records to CSV file."""
        import csv

        if not records:
            return

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{self.stream_name}_{timestamp}.csv"

        keys = records[0].keys()
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)

    def _write_to_database(self, records: list[dict]) -> None:
        """Write records to database. Override for specific implementation."""

    def _write_to_wms(self, records: list[dict]) -> None:
        """Write records back to WMS API. Override for specific implementation."""

    def _update_state(self, context: dict) -> None:
        """Update state after processing batch."""
        # Implement state management if needed


class InventorySink(WMSBaseSink):
    """Sink for inventory-related streams."""

    def _create_business_manager(self) -> Any:
        """Create inventory business manager."""
        from target_oracle_wms.business.inventory import InventoryManager

        return InventoryManager(self.config)

    def _apply_business_logic(self, records: list[dict]) -> list[dict]:
        """Apply inventory business logic."""
        if not self.business_manager:
            return records

        # Group records by type for processing
        if self.stream_name == "inventory":
            # Calculate KPIs
            if self.config.get("enable_kpi_calculation", True):
                kpis = self.business_manager.calculate_inventory_kpis(records)
                self._write_kpi_report("inventory_kpis", kpis)

            # Generate alerts
            if self.config.get("enable_alerts", True):
                alerts = self.business_manager.identify_lot_expiry_alerts(
                    records,
                    days_ahead=self.config.get("expiry_alert_days", 30),
                )
                if alerts:
                    self._write_alerts("inventory_expiry_alerts", alerts)

        elif self.stream_name == "cycle_counts":
            # Analyze variance
            variance_report = self.business_manager.analyze_cycle_count_variance(
                records
            )
            self._write_kpi_report("cycle_count_variance", variance_report)

        return records

    def _write_kpi_report(self, report_name: str, data: dict) -> None:
        """Write KPI report."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{report_name}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _write_alerts(self, alert_type: str, alerts: list[dict]) -> None:
        """Write alerts to file."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{alert_type}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(alerts, f, indent=2, default=str)


class OrderSink(WMSBaseSink):
    """Sink for order-related streams."""

    def _create_business_manager(self) -> Any:
        """Create order business manager."""
        from target_oracle_wms.business.orders import OrderManager

        return OrderManager(self.config)

    def _apply_business_logic(self, records: list[dict]) -> list[dict]:
        """Apply order business logic."""
        if not self.business_manager:
            return records

        if self.stream_name == "orders":
            # Calculate fulfillment KPIs
            if self.config.get("enable_kpi_calculation", True):
                kpis = self.business_manager.calculate_order_fulfillment_kpis(records)
                self._write_kpi_report("order_fulfillment_kpis", kpis)

            # Identify bottlenecks
            if self.config.get("enable_alerts", True):
                bottlenecks = self.business_manager.identify_order_bottlenecks(records)
                if bottlenecks:
                    self._write_alerts("order_bottlenecks", bottlenecks)

        elif self.stream_name == "allocations":
            # Analyze allocation efficiency
            efficiency_report = self.business_manager.analyze_allocation_efficiency(
                records
            )
            self._write_kpi_report("allocation_efficiency", efficiency_report)

        return records

    def _write_kpi_report(self, report_name: str, data: dict) -> None:
        """Write KPI report."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{report_name}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _write_alerts(self, alert_type: str, alerts: list[dict]) -> None:
        """Write alerts to file."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{alert_type}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(alerts, f, indent=2, default=str)


class WarehouseSink(WMSBaseSink):
    """Sink for warehouse operation streams."""

    def _create_business_manager(self) -> Any:
        """Create warehouse business manager."""
        from target_oracle_wms.business.warehouse import WarehouseManager

        return WarehouseManager(self.config)

    def _apply_business_logic(self, records: list[dict]) -> list[dict]:
        """Apply warehouse business logic."""
        if not self.business_manager:
            return records

        if self.stream_name == "tasks":
            # Calculate task performance
            if self.config.get("enable_kpi_calculation", True):
                metrics = self.business_manager.calculate_task_performance_metrics(
                    records
                )
                self._write_kpi_report("task_performance_metrics", metrics)

        elif self.stream_name == "workers":
            # Analyze worker productivity
            productivity_report = self.business_manager.analyze_worker_productivity(
                records
            )
            self._write_kpi_report("worker_productivity", productivity_report)

        elif self.stream_name == "equipment":
            # Analyze equipment utilization
            utilization_report = self.business_manager.analyze_equipment_utilization(
                records
            )
            self._write_kpi_report("equipment_utilization", utilization_report)

        return records

    def _write_kpi_report(self, report_name: str, data: dict) -> None:
        """Write KPI report."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = self.output_path / f"{report_name}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)


class GenericWMSSink(WMSBaseSink):
    """Generic sink for WMS streams without specialized business logic."""

    def _apply_business_logic(self, records: list[dict]) -> list[dict]:
        """No business logic for generic streams."""
        return records

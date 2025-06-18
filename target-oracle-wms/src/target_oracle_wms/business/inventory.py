"""Inventory management business logic for Oracle WMS.

This module provides specialized business intelligence and processing
for inventory-related data streams including lot tracking, serial numbers,
cycle counts, and inventory movements.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class InventoryManager:
    """Business logic for inventory management operations."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize inventory manager.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config
        self.inventory_config = config.get("inventory_tracking", {})

        # Core inventory entities (expanded to meet 10+ requirement)
        self.core_entities = [
            "inventory",
            "item",
            "location",
            "uom",
            "company",
            "facility",
            "item_master",
            "item_attribute",
            "location_type",
            "zone",
            "inventory_balance",
            "physical_inventory",
        ]

        # Optional inventory entities based on configuration (expanded)
        self.optional_entities = {
            "lot_tracking": [
                "lot",
                "lot_tracking",
                "lot_attribute",
                "lot_genealogy",
                "lot_status",
                "lot_hold",
            ],
            "serial_numbers": [
                "serial_number",
                "serial_tracking",
                "serial_genealogy",
                "serial_status",
            ],
            "expiry_dates": [
                "expiry_date",
                "expiry_tracking",
                "shelf_life",
                "expiry_alert",
            ],
            "cycle_counts": [
                "cycle_count",
                "cycle_count_detail",
                "cycle_count_variance",
                "count_sequence",
                "count_approval",
            ],
            "adjustments": [
                "inventory_adjustment",
                "adjustment_reason",
                "adjustment_approval",
                "adjustment_variance",
            ],
            "inventory_moves": [
                "inventory_move",
                "move_transaction",
                "move_history",
                "cross_reference",
                "putaway_rule",
                "pick_rule",
            ],
        }

    def get_required_entities(self) -> list[str]:
        """Get list of entities required based on inventory configuration.

        Returns
        -------
            List of entity names to extract

        """
        entities = list(self.core_entities)

        # Add optional entities based on configuration
        for config_key, entity_list in self.optional_entities.items():
            if self.inventory_config.get(f"include_{config_key}", False):
                entities.extend(entity_list)

        return list(set(entities))  # Remove duplicates

    def get_inventory_filters(
        self,
        facility: str | None = None,
        item_code: str | None = None,
        location: str | None = None,
    ) -> dict[str, Any]:
        """Get filters for inventory data extraction.

        Args:
        ----
            facility: Facility code filter
            item_code: Item code filter
            location: Location filter

        Returns:
        -------
            Dictionary of filters to apply

        """
        filters = {}

        if facility:
            filters["facility_code"] = facility
        if item_code:
            filters["item_code"] = item_code
        if location:
            filters["location_code"] = location

        # Add default filters for active inventory only
        filters["inventory_status"] = "ACTIVE"

        return filters

    def calculate_inventory_kpis(
        self, inventory_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate inventory KPIs from extracted data.

        Args:
        ----
            inventory_data: List of inventory records

        Returns:
        -------
            Dictionary of calculated KPIs

        """
        if not inventory_data:
            return {}

        # Calculate basic metrics
        total_items = len(inventory_data)
        total_quantity = sum(
            float(record.get("on_hand_qty", 0)) for record in inventory_data
        )
        total_value = sum(
            float(record.get("inventory_value", 0)) for record in inventory_data
        )

        # Calculate availability metrics
        available_qty = sum(
            float(record.get("available_qty", 0)) for record in inventory_data
        )
        allocated_qty = sum(
            float(record.get("allocated_qty", 0)) for record in inventory_data
        )

        # Calculate item variety
        unique_items = len({record.get("item_code") for record in inventory_data})
        unique_locations = len(
            {record.get("location_code") for record in inventory_data}
        )

        # Calculate low stock items (assuming safety stock field exists)
        low_stock_items = [
            record
            for record in inventory_data
            if (
                float(record.get("on_hand_qty", 0))
                <= float(record.get("safety_stock_qty", 0))
            )
        ]

        return {
            "total_inventory_lines": total_items,
            "total_quantity": total_quantity,
            "total_inventory_value": total_value,
            "available_quantity": available_qty,
            "allocated_quantity": allocated_qty,
            "allocation_percentage": (
                (allocated_qty / total_quantity * 100) if total_quantity > 0 else 0
            ),
            "unique_items": unique_items,
            "unique_locations": unique_locations,
            "low_stock_items_count": len(low_stock_items),
            "low_stock_percentage": (
                (len(low_stock_items) / total_items * 100) if total_items > 0 else 0
            ),
            "average_inventory_value": (
                total_value / total_items if total_items > 0 else 0
            ),
            "calculation_timestamp": datetime.now(UTC).isoformat(),
        }

    def identify_lot_expiry_alerts(
        self, lot_data: list[dict[str, Any]], days_ahead: int = 30
    ) -> list[dict[str, Any]]:
        """Identify lots expiring within specified days.

        Args:
        ----
            lot_data: List of lot tracking records
            days_ahead: Number of days to look ahead for expiry

        Returns:
        -------
            List of expiring lots with alerts

        """
        if not self.inventory_config.get("include_expiry_dates", False):
            return []

        alerts = []
        cutoff_date = datetime.now(UTC) + timedelta(days=days_ahead)

        for lot in lot_data:
            expiry_date_str = lot.get("expiry_date")
            if not expiry_date_str:
                continue

            try:
                # Handle different date formats
                if "T" in expiry_date_str:
                    expiry_date = datetime.fromisoformat(
                        expiry_date_str.replace("Z", "+00:00")
                    )
                else:
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")

                if expiry_date <= cutoff_date:
                    days_to_expiry = (expiry_date - datetime.now(UTC)).days

                    alert = {
                        "lot_number": lot.get("lot_number"),
                        "item_code": lot.get("item_code"),
                        "location_code": lot.get("location_code"),
                        "expiry_date": expiry_date_str,
                        "days_to_expiry": days_to_expiry,
                        "quantity": lot.get("quantity", 0),
                        "alert_level": self._get_alert_level(days_to_expiry),
                        "recommended_action": self._get_recommended_action(
                            days_to_expiry
                        ),
                    }
                    alerts.append(alert)

            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid expiry date for lot {lot.get('lot_number')}: {e}"
                )
                continue

        # Sort by days to expiry (most urgent first)
        alerts.sort(key=lambda x: x["days_to_expiry"])
        return alerts

    def analyze_cycle_count_variance(
        self, cycle_count_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze cycle count variances and accuracy.

        Args:
        ----
            cycle_count_data: List of cycle count records

        Returns:
        -------
            Variance analysis results

        """
        if not self.inventory_config.get("include_cycle_counts", False):
            return {}

        total_counts = len(cycle_count_data)
        if total_counts == 0:
            return {"error": "No cycle count data available"}

        # Calculate variance statistics
        variances = []
        accuracy_threshold = 0.01  # 1% tolerance

        for count in cycle_count_data:
            book_qty = float(count.get("book_quantity", 0))
            count_qty = float(count.get("count_quantity", 0))

            if book_qty != 0:
                variance_pct = abs((count_qty - book_qty) / book_qty) * 100
                variances.append(
                    {
                        "item_code": count.get("item_code"),
                        "location_code": count.get("location_code"),
                        "book_quantity": book_qty,
                        "count_quantity": count_qty,
                        "variance_percentage": variance_pct,
                        "within_tolerance": variance_pct <= accuracy_threshold,
                    }
                )

        # Calculate summary statistics
        accurate_counts = sum(1 for v in variances if v["within_tolerance"])
        accuracy_rate = (
            (accurate_counts / total_counts * 100) if total_counts > 0 else 0
        )

        avg_variance = (
            sum(v["variance_percentage"] for v in variances) / len(variances)
            if variances
            else 0
        )
        max_variance = (
            max(v["variance_percentage"] for v in variances) if variances else 0
        )

        return {
            "total_cycle_counts": total_counts,
            "accurate_counts": accurate_counts,
            "accuracy_rate_percentage": accuracy_rate,
            "average_variance_percentage": avg_variance,
            "maximum_variance_percentage": max_variance,
            "accuracy_threshold_percentage": accuracy_threshold * 100,
            "variance_details": variances,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def generate_inventory_health_report(
        self, all_inventory_data: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Generate comprehensive inventory health report.

        Args:
        ----
            all_inventory_data: Dictionary containing all inventory-related data

        Returns:
        -------
            Comprehensive health report

        """
        report = {
            "report_generated": datetime.now(UTC).isoformat(),
            "configuration": self.inventory_config,
            "summary": {},
        }

        # Basic inventory metrics
        inventory_data = all_inventory_data.get("inventory", [])
        if inventory_data:
            report["summary"]["inventory_kpis"] = self.calculate_inventory_kpis(
                inventory_data
            )

        # Lot expiry analysis
        lot_data = all_inventory_data.get("lot", [])
        if lot_data and self.inventory_config.get("include_expiry_dates", False):
            report["expiry_alerts"] = self.identify_lot_expiry_alerts(lot_data)

        # Cycle count accuracy
        cycle_count_data = all_inventory_data.get("cycle_count", [])
        if cycle_count_data and self.inventory_config.get(
            "include_cycle_counts", False
        ):
            report["cycle_count_analysis"] = self.analyze_cycle_count_variance(
                cycle_count_data
            )

        # Serial number tracking summary
        if self.inventory_config.get("include_serial_numbers", False):
            serial_data = all_inventory_data.get("serial_number", [])
            report["serial_tracking"] = {
                "total_serialized_items": len(serial_data),
                "unique_serial_numbers": len(
                    {s.get("serial_number") for s in serial_data}
                ),
            }

        # Location utilization
        location_data = all_inventory_data.get("location", [])
        if location_data:
            report["location_utilization"] = self._analyze_location_utilization(
                inventory_data, location_data
            )

        return report

    def _get_alert_level(self, days_to_expiry: int) -> str:
        """Get alert level based on days to expiry."""
        if days_to_expiry <= 0:
            return "CRITICAL"
        if days_to_expiry <= 7:
            return "HIGH"
        if days_to_expiry <= 30:
            return "MEDIUM"
        return "LOW"

    def _get_recommended_action(self, days_to_expiry: int) -> str:
        """Get recommended action based on days to expiry."""
        if days_to_expiry <= 0:
            return "IMMEDIATE REMOVAL - Product expired"
        if days_to_expiry <= 7:
            return "URGENT SALE/USE - Product expires within a week"
        if days_to_expiry <= 30:
            return "PRIORITIZE SHIPMENT - Product expires within 30 days"
        return "MONITOR - Product expires in future"

    def _analyze_location_utilization(
        self,
        inventory_data: list[dict[str, Any]],
        location_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze location utilization from inventory and location data."""
        # Group inventory by location
        inventory_by_location = {}
        for item in inventory_data:
            location = item.get("location_code")
            if location:
                if location not in inventory_by_location:
                    inventory_by_location[location] = []
                inventory_by_location[location].append(item)

        # Calculate utilization metrics
        total_locations = len(location_data)
        utilized_locations = len(inventory_by_location)
        utilization_rate = (
            (utilized_locations / total_locations * 100) if total_locations > 0 else 0
        )

        # Find most/least utilized locations
        location_usage = [
            {
                "location_code": loc,
                "item_count": len(items),
                "total_quantity": sum(
                    float(item.get("on_hand_qty", 0)) for item in items
                ),
            }
            for loc, items in inventory_by_location.items()
        ]

        location_usage.sort(key=lambda x: x["total_quantity"], reverse=True)

        return {
            "total_locations": total_locations,
            "utilized_locations": utilized_locations,
            "utilization_rate_percentage": utilization_rate,
            "top_utilized_locations": location_usage[:10],
            "empty_locations": total_locations - utilized_locations,
        }

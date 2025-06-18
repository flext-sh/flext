"""Order management business logic for Oracle WMS.

This module provides specialized business intelligence and processing
for order-related data streams including order lifecycle, allocation
efficiency, fulfillment metrics, and shipping performance.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OrderManager:
    """Business logic for order management operations."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize order manager.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config
        self.order_config = config.get("order_management", {})

        # Core order entities (expanded to meet 10+ requirement)
        self.core_entities = [
            "order_header",
            "order_detail",
            "customer",
            "item",
            "order_type",
            "order_priority",
            "customer_master",
            "order_batch",
            "order_attribute",
            "order_reference",
            "ship_to_address",
            "bill_to_address",
        ]

        # Optional order entities based on configuration (expanded)
        self.optional_entities = {
            "order_details": [
                "order_line",
                "order_attribute",
                "order_instruction",
                "order_note",
            ],
            "allocations": [
                "allocation",
                "allocation_detail",
                "allocation_rule",
                "allocation_strategy",
                "allocation_exception",
            ],
            "picks": [
                "pick",
                "pick_detail",
                "pick_list",
                "pick_wave",
                "pick_sequence",
                "pick_exception",
            ],
            "shipments": [
                "shipment",
                "shipment_detail",
                "bill_of_lading",
                "manifest",
                "carrier",
                "tracking_number",
            ],
            "returns": [
                "return_order",
                "return_detail",
                "return_reason",
                "return_authorization",
                "return_disposition",
            ],
            "order_lifecycle": [
                "order_status_history",
                "order_activity_log",
                "order_milestone",
                "order_exception",
                "order_hold",
            ],
        }

    def get_required_entities(self) -> list[str]:
        """Get list of entities required based on order configuration.

        Returns
        -------
            List of entity names to extract

        """
        entities = list(self.core_entities)

        # Add optional entities based on configuration
        for config_key, entity_list in self.optional_entities.items():
            if self.order_config.get(f"include_{config_key}", False):
                entities.extend(entity_list)

        return list(set(entities))  # Remove duplicates

    def get_order_filters(
        self,
        order_status: list[str] | None = None,
        date_range: tuple[str, str] | None = None,
        customer_code: str | None = None,
    ) -> dict[str, Any]:
        """Get filters for order data extraction.

        Args:
        ----
            order_status: List of order statuses to filter by
            date_range: Tuple of (start_date, end_date) for filtering
            customer_code: Customer code filter

        Returns:
        -------
            Dictionary of filters to apply

        """
        filters = {}

        if order_status:
            filters["order_status__in"] = order_status
        if customer_code:
            filters["customer_code"] = customer_code
        if date_range:
            filters["order_date__gte"] = date_range[0]
            filters["order_date__lte"] = date_range[1]

        return filters

    def calculate_order_fulfillment_kpis(
        self,
        order_data: list[dict[str, Any]],
        allocation_data: Optional[list[dict[str, Any]]] = None,
        shipment_data: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Calculate order fulfillment KPIs.

        Args:
        ----
            order_data: List of order records
            allocation_data: List of allocation records
            shipment_data: List of shipment records

        Returns:
        -------
            Dictionary of calculated KPIs

        """
        if not order_data:
            return {}

        total_orders = len(order_data)

        # Calculate basic order metrics
        total_order_value = sum(
            float(order.get("order_value", 0)) for order in order_data
        )
        total_order_lines = sum(int(order.get("line_count", 1)) for order in order_data)

        # Calculate order status distribution
        status_distribution = {}
        for order in order_data:
            status = order.get("order_status", "UNKNOWN")
            status_distribution[status] = status_distribution.get(status, 0) + 1

        # Calculate fulfillment metrics
        fulfilled_orders = [
            order
            for order in order_data
            if order.get("order_status") in ["SHIPPED", "DELIVERED", "COMPLETED"]
        ]
        fulfillment_rate = (
            (len(fulfilled_orders) / total_orders * 100) if total_orders > 0 else 0
        )

        # Calculate cycle time metrics
        cycle_times = []
        for order in order_data:
            order_date = order.get("order_date")
            ship_date = order.get("ship_date")

            if order_date and ship_date:
                try:
                    order_dt = datetime.fromisoformat(order_date.replace("Z", "+00:00"))
                    ship_dt = datetime.fromisoformat(ship_date.replace("Z", "+00:00"))
                    cycle_time = (ship_dt - order_dt).total_seconds() / 3600  # hours
                    cycle_times.append(cycle_time)
                except (ValueError, TypeError):
                    continue

        avg_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0

        # On-time shipment calculation
        on_time_shipments = 0
        total_shipments_with_dates = 0

        for order in order_data:
            requested_date = order.get("requested_ship_date")
            actual_date = order.get("ship_date")

            if requested_date and actual_date:
                total_shipments_with_dates += 1
                try:
                    req_dt = datetime.fromisoformat(
                        requested_date.replace("Z", "+00:00")
                    )
                    act_dt = datetime.fromisoformat(actual_date.replace("Z", "+00:00"))

                    if act_dt <= req_dt:
                        on_time_shipments += 1
                except (ValueError, TypeError):
                    continue

        on_time_rate = (
            (on_time_shipments / total_shipments_with_dates * 100)
            if total_shipments_with_dates > 0
            else 0
        )

        kpis = {
            "total_orders": total_orders,
            "total_order_value": total_order_value,
            "total_order_lines": total_order_lines,
            "average_order_value": (
                total_order_value / total_orders if total_orders > 0 else 0
            ),
            "fulfillment_rate_percentage": fulfillment_rate,
            "average_cycle_time_hours": avg_cycle_time,
            "on_time_shipment_rate_percentage": on_time_rate,
            "status_distribution": status_distribution,
            "calculation_timestamp": datetime.now(UTC).isoformat(),
        }

        # Add allocation metrics if available
        if allocation_data:
            kpis.update(self._calculate_allocation_metrics(order_data, allocation_data))

        return kpis

    def analyze_allocation_efficiency(
        self,
        allocation_data: list[dict[str, Any]],
        inventory_data: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Analyze allocation efficiency and patterns.

        Args:
        ----
            allocation_data: List of allocation records
            inventory_data: List of inventory records for analysis

        Returns:
        -------
            Allocation efficiency analysis

        """
        if not allocation_data:
            return {"error": "No allocation data available"}

        total_allocations = len(allocation_data)

        # Calculate allocation success rate
        successful_allocations = [
            alloc
            for alloc in allocation_data
            if alloc.get("allocation_status") == "ALLOCATED"
        ]
        success_rate = (
            (len(successful_allocations) / total_allocations * 100)
            if total_allocations > 0
            else 0
        )

        # Calculate allocation timing
        allocation_times = []
        for alloc in allocation_data:
            created = alloc.get("create_ts")
            allocated = alloc.get("allocated_ts")

            if created and allocated:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    allocated_dt = datetime.fromisoformat(
                        allocated.replace("Z", "+00:00")
                    )
                    time_to_allocate = (
                        allocated_dt - created_dt
                    ).total_seconds() / 60  # minutes
                    allocation_times.append(time_to_allocate)
                except (ValueError, TypeError):
                    continue

        avg_allocation_time = (
            sum(allocation_times) / len(allocation_times) if allocation_times else 0
        )

        # Analyze allocation patterns by item
        item_allocation_patterns = {}
        for alloc in allocation_data:
            item_code = alloc.get("item_code")
            if item_code:
                if item_code not in item_allocation_patterns:
                    item_allocation_patterns[item_code] = {
                        "total_requests": 0,
                        "successful_allocations": 0,
                        "total_quantity_requested": 0,
                        "total_quantity_allocated": 0,
                    }

                pattern = item_allocation_patterns[item_code]
                pattern["total_requests"] += 1
                pattern["total_quantity_requested"] += float(
                    alloc.get("requested_qty", 0)
                )

                if alloc.get("allocation_status") == "ALLOCATED":
                    pattern["successful_allocations"] += 1
                    pattern["total_quantity_allocated"] += float(
                        alloc.get("allocated_qty", 0)
                    )

        # Calculate fill rates for items
        for item_code, pattern in item_allocation_patterns.items():
            if pattern["total_requests"] > 0:
                pattern["success_rate"] = (
                    pattern["successful_allocations"] / pattern["total_requests"]
                ) * 100
            if pattern["total_quantity_requested"] > 0:
                pattern["fill_rate"] = (
                    pattern["total_quantity_allocated"]
                    / pattern["total_quantity_requested"]
                ) * 100

        # Identify bottleneck items (low success rate)
        bottleneck_items = [
            {
                "item_code": item,
                "success_rate": data["success_rate"],
                "fill_rate": data.get("fill_rate", 0),
            }
            for item, data in item_allocation_patterns.items()
            if data.get("success_rate", 0) < 90  # Less than 90% success rate
        ]
        bottleneck_items.sort(key=lambda x: x["success_rate"])

        return {
            "total_allocations": total_allocations,
            "successful_allocations": len(successful_allocations),
            "allocation_success_rate_percentage": success_rate,
            "average_allocation_time_minutes": avg_allocation_time,
            "bottleneck_items": bottleneck_items[:10],  # Top 10 bottlenecks
            "item_patterns_count": len(item_allocation_patterns),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def identify_order_bottlenecks(
        self,
        order_data: list[dict[str, Any]],
        allocation_data: Optional[list[dict[str, Any]]] = None,
        pick_data: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """Identify bottlenecks in order processing.

        Args:
        ----
            order_data: List of order records
            allocation_data: List of allocation records
            pick_data: List of pick records

        Returns:
        -------
            List of identified bottlenecks with recommendations

        """
        bottlenecks = []

        # Analyze order aging (orders stuck in status for too long)
        current_time = datetime.now(UTC)
        for order in order_data:
            order_status = order.get("order_status")
            status_date = order.get("status_date") or order.get("order_date")

            if status_date:
                try:
                    status_dt = datetime.fromisoformat(
                        status_date.replace("Z", "+00:00")
                    )
                    days_in_status = (current_time - status_dt).days

                    # Define thresholds for different statuses
                    thresholds = {
                        "RELEASED": 1,  # Should be allocated within 1 day
                        "ALLOCATED": 2,  # Should be picked within 2 days
                        "PICKED": 1,  # Should be shipped within 1 day
                        "STAGED": 0.5,  # Should be shipped within 12 hours
                    }

                    threshold = thresholds.get(order_status, 3)  # Default 3 days

                    if days_in_status > threshold:
                        bottlenecks.append(
                            {
                                "type": "ORDER_AGING",
                                "order_number": order.get("order_number"),
                                "order_status": order_status,
                                "days_in_status": days_in_status,
                                "threshold_days": threshold,
                                "severity": (
                                    "HIGH"
                                    if days_in_status > threshold * 2
                                    else "MEDIUM"
                                ),
                                "recommendation": (
                                    f"Review {order_status.lower()} process for order "
                                    f"{order.get('order_number')}"
                                ),
                            }
                        )

                except (ValueError, TypeError):
                    continue

        # Analyze allocation bottlenecks
        if allocation_data:
            failed_allocations = [
                alloc
                for alloc in allocation_data
                if alloc.get("allocation_status") in ["FAILED", "PARTIAL"]
            ]

            if len(failed_allocations) > 0:
                total_allocations = len(allocation_data)
                failure_rate = len(failed_allocations) / total_allocations * 100

                if failure_rate > 10:  # More than 10% failure rate
                    bottlenecks.append(
                        {
                            "type": "ALLOCATION_FAILURE",
                            "failure_count": len(failed_allocations),
                            "total_allocations": total_allocations,
                            "failure_rate_percentage": failure_rate,
                            "severity": ("HIGH" if failure_rate > 20 else "MEDIUM"),
                            "recommendation": "Review inventory availability and allocation rules",
                        }
                    )

        # Analyze picking bottlenecks
        if pick_data:
            slow_picks = []
            for pick in pick_data:
                assigned_date = pick.get("assigned_date")
                completed_date = pick.get("completed_date")

                if assigned_date and completed_date:
                    try:
                        assigned_dt = datetime.fromisoformat(
                            assigned_date.replace("Z", "+00:00")
                        )
                        completed_dt = datetime.fromisoformat(
                            completed_date.replace("Z", "+00:00")
                        )
                        pick_time_hours = (
                            completed_dt - assigned_dt
                        ).total_seconds() / 3600

                        if pick_time_hours > 24:  # Picks taking more than 24 hours
                            slow_picks.append(
                                {
                                    "pick_id": pick.get("pick_id"),
                                    "pick_time_hours": pick_time_hours,
                                    "worker_id": pick.get("assigned_user"),
                                }
                            )

                    except (ValueError, TypeError):
                        continue

            if len(slow_picks) > 0:
                avg_slow_pick_time = sum(
                    p["pick_time_hours"] for p in slow_picks
                ) / len(slow_picks)

                bottlenecks.append(
                    {
                        "type": "SLOW_PICKING",
                        "slow_pick_count": len(slow_picks),
                        "average_slow_pick_time_hours": avg_slow_pick_time,
                        "severity": "MEDIUM",
                        "recommendation": "Review pick productivity and worker assignments",
                        "affected_picks": slow_picks[:5],  # Top 5 slowest picks
                    }
                )

        # Sort bottlenecks by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        bottlenecks.sort(key=lambda x: severity_order.get(x.get("severity", "LOW"), 2))

        return bottlenecks

    def generate_order_performance_report(
        self, all_order_data: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Generate comprehensive order performance report.

        Args:
        ----
            all_order_data: Dictionary containing all order-related data

        Returns:
        -------
            Comprehensive performance report

        """
        report = {
            "report_generated": datetime.now(UTC).isoformat(),
            "configuration": self.order_config,
            "summary": {},
        }

        # Basic order metrics
        order_data = all_order_data.get("order_header", [])
        allocation_data = all_order_data.get("allocation", [])
        shipment_data = all_order_data.get("shipment", [])
        pick_data = all_order_data.get("pick", [])

        if order_data:
            report["summary"]["fulfillment_kpis"] = (
                self.calculate_order_fulfillment_kpis(
                    order_data, allocation_data, shipment_data
                )
            )

        # Allocation efficiency analysis
        if allocation_data:
            inventory_data = all_order_data.get("inventory", [])
            report["allocation_analysis"] = self.analyze_allocation_efficiency(
                allocation_data, inventory_data
            )

        # Bottleneck identification
        bottlenecks = self.identify_order_bottlenecks(
            order_data, allocation_data, pick_data
        )
        if bottlenecks:
            report["bottlenecks"] = {
                "total_bottlenecks": len(bottlenecks),
                "high_severity_count": len(
                    [b for b in bottlenecks if b.get("severity") == "HIGH"]
                ),
                "bottleneck_details": bottlenecks,
            }

        # Customer performance analysis
        if order_data:
            report["customer_analysis"] = self._analyze_customer_performance(order_data)

        # Daily/weekly trends
        if order_data:
            report["trend_analysis"] = self._analyze_order_trends(order_data)

        return report

    def _calculate_allocation_metrics(
        self,
        order_data: list[dict[str, Any]],
        allocation_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate allocation-specific metrics."""
        total_order_lines = sum(int(order.get("line_count", 1)) for order in order_data)
        allocated_lines = len(
            [
                alloc
                for alloc in allocation_data
                if alloc.get("allocation_status") == "ALLOCATED"
            ]
        )

        allocation_coverage = (
            (allocated_lines / total_order_lines * 100) if total_order_lines > 0 else 0
        )

        return {
            "total_order_lines": total_order_lines,
            "allocated_lines": allocated_lines,
            "allocation_coverage_percentage": allocation_coverage,
        }

    def _analyze_customer_performance(
        self, order_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze performance by customer."""
        customer_metrics = {}

        for order in order_data:
            customer = order.get("customer_code")
            if not customer:
                continue

            if customer not in customer_metrics:
                customer_metrics[customer] = {
                    "order_count": 0,
                    "total_value": 0,
                    "on_time_orders": 0,
                    "total_orders_with_dates": 0,
                }

            metrics = customer_metrics[customer]
            metrics["order_count"] += 1
            metrics["total_value"] += float(order.get("order_value", 0))

            # Check on-time performance
            requested_date = order.get("requested_ship_date")
            actual_date = order.get("ship_date")

            if requested_date and actual_date:
                metrics["total_orders_with_dates"] += 1
                try:
                    req_dt = datetime.fromisoformat(
                        requested_date.replace("Z", "+00:00")
                    )
                    act_dt = datetime.fromisoformat(actual_date.replace("Z", "+00:00"))

                    if act_dt <= req_dt:
                        metrics["on_time_orders"] += 1
                except (ValueError, TypeError):
                    pass

        # Calculate customer performance scores
        for customer, metrics in customer_metrics.items():
            if metrics["total_orders_with_dates"] > 0:
                metrics["on_time_rate"] = (
                    metrics["on_time_orders"] / metrics["total_orders_with_dates"]
                ) * 100
            metrics["average_order_value"] = (
                metrics["total_value"] / metrics["order_count"]
            )

        # Get top customers by value and performance
        top_customers_by_value = sorted(
            customer_metrics.items(),
            key=lambda x: x[1]["total_value"],
            reverse=True,
        )[:10]

        return {
            "total_customers": len(customer_metrics),
            "top_customers_by_value": [
                {"customer": k, **v} for k, v in top_customers_by_value
            ],
        }

    def _analyze_order_trends(self, order_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze order trends over time."""
        daily_metrics = {}

        for order in order_data:
            order_date = order.get("order_date")
            if not order_date:
                continue

            try:
                order_dt = datetime.fromisoformat(order_date.replace("Z", "+00:00"))
                date_key = order_dt.strftime("%Y-%m-%d")

                if date_key not in daily_metrics:
                    daily_metrics[date_key] = {
                        "order_count": 0,
                        "total_value": 0,
                    }

                daily_metrics[date_key]["order_count"] += 1
                daily_metrics[date_key]["total_value"] += float(
                    order.get("order_value", 0)
                )

            except (ValueError, TypeError):
                continue

        # Calculate daily averages
        if daily_metrics:
            avg_daily_orders = sum(
                m["order_count"] for m in daily_metrics.values()
            ) / len(daily_metrics)
            avg_daily_value = sum(
                m["total_value"] for m in daily_metrics.values()
            ) / len(daily_metrics)
        else:
            avg_daily_orders = 0
            avg_daily_value = 0

        return {
            "analysis_period_days": len(daily_metrics),
            "average_daily_orders": avg_daily_orders,
            "average_daily_value": avg_daily_value,
            "daily_breakdown": daily_metrics,
        }

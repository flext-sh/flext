"""Warehouse operations business logic for Oracle WMS.

This module provides specialized business intelligence and processing
for warehouse operations including task management, productivity analysis,
equipment utilization, and labor performance tracking.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional


logger = logging.getLogger(__name__)


class WarehouseManager:
    """Business logic for warehouse operations management."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize warehouse manager.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config
        self.warehouse_config = config.get("warehouse_operations", {})

        # Core warehouse entities (expanded to meet 10+ requirement)
        self.core_entities = [
            "task",
            "location",
            "user_",
            "equipment",
            "work_order",
            "task_type",
            "resource",
            "shift",
            "team",
            "zone",
            "work_assignment",
            "performance_standard",
        ]

        # Optional warehouse entities based on configuration (expanded)
        self.optional_entities = {
            "tasks": [
                "task_detail",
                "task_history",
                "task_performance",
                "task_exception",
                "task_instruction",
                "task_sequence",
            ],
            "labor_tracking": [
                "labor_activity",
                "labor_performance",
                "productivity_metrics",
                "time_clock",
                "labor_standard",
                "incentive_pay",
            ],
            "equipment": [
                "equipment_status",
                "equipment_maintenance",
                "equipment_utilization",
                "equipment_type",
                "maintenance_schedule",
                "equipment_location",
            ],
            "dock_management": [
                "dock_appointment",
                "dock_schedule",
                "trailer_status",
                "dock_door",
                "yard_management",
                "truck_arrival",
            ],
            "wave_management": [
                "wave",
                "wave_detail",
                "wave_performance",
                "wave_template",
                "wave_rule",
                "wave_release",
            ],
            "productivity": [
                "work_measurement",
                "performance_targets",
                "productivity_reports",
                "efficiency_report",
                "quality_metrics",
                "safety_incident",
            ],
        }

    def get_required_entities(self) -> list[str]:
        """Get list of entities required based on warehouse configuration.

        Returns
        -------
            List of entity names to extract

        """
        entities = list(self.core_entities)

        # Add optional entities based on configuration
        for config_key, entity_list in self.optional_entities.items():
            if self.warehouse_config.get(f"include_{config_key}", False):
                entities.extend(entity_list)

        return list(set(entities))  # Remove duplicates

    def get_warehouse_filters(
        self,
        task_type: str | None = None,
        worker_id: str | None = None,
        equipment_type: str | None = None,
        zone: str | None = None,
    ) -> dict[str, Any]:
        """Get filters for warehouse data extraction.

        Args:
        ----
            task_type: Task type filter (pick, put, replenish, etc.)
            worker_id: Worker/user ID filter
            equipment_type: Equipment type filter
            zone: Zone filter

        Returns:
        -------
            Dictionary of filters to apply

        """
        filters = {}

        if task_type and task_type != "all":
            filters["task_type"] = task_type
        if worker_id:
            filters["assigned_user"] = worker_id
        if equipment_type:
            filters["equipment_type"] = equipment_type
        if zone:
            filters["zone_code"] = zone

        # Default filter for active tasks only
        filters["task_status__in"] = ",".join(["ASSIGNED", "IN_PROGRESS", "COMPLETED"])

        return filters

    def calculate_task_performance_metrics(
        self, task_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate task performance and productivity metrics.

        Args:
        ----
            task_data: List of task records

        Returns:
        -------
            Dictionary of calculated metrics

        """
        if not task_data:
            return {}

        total_tasks = len(task_data)

        # Task status distribution
        status_distribution: dict[str, int] = {}
        for task in task_data:
            status = task.get("task_status", "UNKNOWN")
            status_distribution[status] = status_distribution.get(status, 0) + 1

        # Task type distribution
        type_distribution: dict[str, int] = {}
        for task in task_data:
            task_type = task.get("task_type", "UNKNOWN")
            type_distribution[task_type] = type_distribution.get(task_type, 0) + 1

        # Calculate completion metrics
        completed_tasks = [
            task for task in task_data if task.get("task_status") == "COMPLETED"
        ]
        completion_rate = (
            (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        )

        # Calculate timing metrics
        task_durations = []
        overdue_tasks = []
        current_time = datetime.now(UTC)

        for task in task_data:
            # Task duration calculation
            start_time = task.get("start_time") or task.get("assigned_time")
            end_time = task.get("end_time") or task.get("completed_time")

            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    duration_hours = (end_dt - start_dt).total_seconds() / 3600
                    task_durations.append(duration_hours)
                except (ValueError, TypeError):
                    continue

            # Overdue task identification
            due_date = task.get("due_date") or task.get("target_completion_time")
            if due_date and task.get("task_status") not in [
                "COMPLETED",
                "CANCELLED",
            ]:
                try:
                    due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    if current_time > due_dt:
                        hours_overdue = (current_time - due_dt).total_seconds() / 3600
                        overdue_tasks.append(
                            {
                                "task_id": task.get("task_id"),
                                "task_type": task.get("task_type"),
                                "assigned_user": task.get("assigned_user"),
                                "hours_overdue": hours_overdue,
                            }
                        )
                except (ValueError, TypeError):
                    continue

        # Calculate productivity metrics
        avg_task_duration = (
            sum(task_durations) / len(task_durations) if task_durations else 0
        )
        tasks_per_hour = 1 / avg_task_duration if avg_task_duration > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "completion_rate_percentage": completion_rate,
            "average_task_duration_hours": avg_task_duration,
            "tasks_per_hour": tasks_per_hour,
            "overdue_tasks_count": len(overdue_tasks),
            "overdue_tasks": overdue_tasks[:10],  # Top 10 overdue tasks
            "status_distribution": status_distribution,
            "type_distribution": type_distribution,
            "calculation_timestamp": datetime.now(UTC).isoformat(),
        }

    def analyze_worker_productivity(
        self,
        task_data: list[dict[str, Any]],
        labor_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Analyze worker productivity and performance.

        Args:
        ----
            task_data: List of task records
            labor_data: List of labor tracking records

        Returns:
        -------
            Worker productivity analysis

        """
        if not task_data:
            return {"error": "No task data available"}

        # Group tasks by worker
        worker_performance = {}

        for task in task_data:
            worker_id = task.get("assigned_user")
            if not worker_id:
                continue

            if worker_id not in worker_performance:
                worker_performance[worker_id] = {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "total_duration_hours": 0,
                    "task_types": {},
                    "overdue_tasks": 0,
                }

            worker = worker_performance[worker_id]
            worker["total_tasks"] += 1

            # Track task completion
            if task.get("task_status") == "COMPLETED":
                worker["completed_tasks"] += 1

            # Track task duration
            start_time = task.get("start_time") or task.get("assigned_time")
            end_time = task.get("end_time") or task.get("completed_time")

            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    duration_hours = (end_dt - start_dt).total_seconds() / 3600
                    worker["total_duration_hours"] += duration_hours
                except (ValueError, TypeError):
                    pass

            # Track task types
            task_type = task.get("task_type", "UNKNOWN")
            worker["task_types"][task_type] = worker["task_types"].get(task_type, 0) + 1

            # Track overdue tasks
            due_date = task.get("due_date")
            if due_date and task.get("task_status") not in [
                "COMPLETED",
                "CANCELLED",
            ]:
                try:
                    due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    if datetime.now(UTC) > due_dt:
                        worker["overdue_tasks"] += 1
                except (ValueError, TypeError):
                    pass

        # Calculate productivity metrics for each worker
        for worker_id, performance in worker_performance.items():
            if performance["total_tasks"] > 0:
                performance["completion_rate"] = (
                    performance["completed_tasks"] / performance["total_tasks"]
                ) * 100

            if performance["total_duration_hours"] > 0:
                performance["tasks_per_hour"] = (
                    performance["completed_tasks"] / performance["total_duration_hours"]
                )
                performance["average_task_duration"] = (
                    performance["total_duration_hours"] / performance["completed_tasks"]
                    if performance["completed_tasks"] > 0
                    else 0
                )

            performance["overdue_rate"] = (
                (performance["overdue_tasks"] / performance["total_tasks"] * 100)
                if performance["total_tasks"] > 0
                else 0
            )

        # Rank workers by productivity
        worker_rankings = []
        for worker_id, performance in worker_performance.items():
            score = (
                performance.get("completion_rate", 0) * 0.4
                + min(performance.get("tasks_per_hour", 0) * 10, 100)
                * 0.4  # Cap at 10 tasks/hour
                + max(0, 100 - performance.get("overdue_rate", 0))
                * 0.2  # Penalty for overdue
            )

            worker_rankings.append(
                {
                    "worker_id": worker_id,
                    "productivity_score": score,
                    "completion_rate": performance.get("completion_rate", 0),
                    "tasks_per_hour": performance.get("tasks_per_hour", 0),
                    "overdue_rate": performance.get("overdue_rate", 0),
                    "total_tasks": performance["total_tasks"],
                }
            )

        worker_rankings.sort(key=lambda x: x["productivity_score"], reverse=True)

        return {
            "total_workers": len(worker_performance),
            "worker_performance_details": worker_performance,
            "worker_rankings": worker_rankings,
            "top_performers": worker_rankings[:5],
            "improvement_needed": [
                w for w in worker_rankings if w["productivity_score"] < 60
            ],
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def analyze_equipment_utilization(
        self,
        equipment_data: list[dict[str, Any]],
        equipment_status_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Analyze equipment utilization and performance.

        Args:
        ----
            equipment_data: List of equipment records
            equipment_status_data: List of equipment status records

        Returns:
        -------
            Equipment utilization analysis

        """
        if not equipment_data:
            return {"error": "No equipment data available"}

        total_equipment = len(equipment_data)

        # Equipment type distribution
        type_distribution = {}
        for equipment in equipment_data:
            eq_type = equipment.get("equipment_type", "UNKNOWN")
            type_distribution[eq_type] = type_distribution.get(eq_type, 0) + 1

        # Equipment status analysis
        status_distribution = {}
        available_equipment = 0

        for equipment in equipment_data:
            status = equipment.get("status", "UNKNOWN")
            status_distribution[status] = status_distribution.get(status, 0) + 1

            if status in ["AVAILABLE", "IDLE", "READY"]:
                available_equipment += 1

        utilization_rate = (
            (total_equipment - available_equipment) / total_equipment * 100
            if total_equipment > 0
            else 0
        )

        # Downtime analysis if status data is available
        downtime_analysis = {}
        equipment_downtime = {}
        if equipment_status_data:
            downtime_events = [
                status
                for status in equipment_status_data
                if status.get("status")
                in ["MAINTENANCE", "BREAKDOWN", "OUT_OF_SERVICE"]
            ]

            # Calculate downtime by equipment
            for event in downtime_events:
                eq_id = event.get("equipment_id")
                if eq_id:
                    if eq_id not in equipment_downtime:
                        equipment_downtime[eq_id] = {
                            "downtime_events": 0,
                            "total_downtime_hours": 0,
                        }

                    equipment_downtime[eq_id]["downtime_events"] += 1

                    # Calculate downtime duration if start/end times available
                    start_time = event.get("status_start_time")
                    end_time = event.get("status_end_time")

                    if start_time and end_time:
                        try:
                            start_dt = datetime.fromisoformat(
                                start_time.replace("Z", "+00:00")
                            )
                            end_dt = datetime.fromisoformat(
                                end_time.replace("Z", "+00:00")
                            )
                            downtime_hours = (end_dt - start_dt).total_seconds() / 3600
                            equipment_downtime[eq_id]["total_downtime_hours"] += (
                                downtime_hours
                            )
                        except (ValueError, TypeError):
                            pass

            # Calculate average downtime
            if equipment_downtime:
                total_downtime_hours = sum(
                    eq["total_downtime_hours"] for eq in equipment_downtime.values()
                )
                avg_downtime_per_equipment = total_downtime_hours / len(
                    equipment_downtime
                )

                downtime_analysis = {
                    "total_downtime_events": len(downtime_events),
                    "equipment_with_downtime": len(equipment_downtime),
                    "total_downtime_hours": total_downtime_hours,
                    "average_downtime_per_equipment_hours": avg_downtime_per_equipment,
                    "equipment_downtime_details": equipment_downtime,
                }

        # Identify high-maintenance equipment
        high_maintenance_equipment = []
        if equipment_downtime:
            for eq_id, downtime in equipment_downtime.items():
                if downtime["downtime_events"] > 5:  # More than 5 downtime events
                    high_maintenance_equipment.append(
                        {
                            "equipment_id": eq_id,
                            "downtime_events": downtime["downtime_events"],
                            "total_downtime_hours": downtime["total_downtime_hours"],
                        }
                    )

        high_maintenance_equipment.sort(
            key=lambda x: x["downtime_events"], reverse=True
        )

        return {
            "total_equipment": total_equipment,
            "available_equipment": available_equipment,
            "utilization_rate_percentage": utilization_rate,
            "type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "downtime_analysis": downtime_analysis,
            "high_maintenance_equipment": high_maintenance_equipment[:10],
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def identify_warehouse_bottlenecks(
        self,
        task_data: list[dict[str, Any]],
        equipment_data: Optional[list[dict[str, Any]]] = None,
        location_data: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """Identify operational bottlenecks in warehouse operations.

        Args:
        ----
            task_data: List of task records
            equipment_data: List of equipment records
            location_data: List of location records

        Returns:
        -------
            List of identified bottlenecks

        """
        bottlenecks = []

        # Task bottlenecks - areas with high task congestion
        if task_data:
            location_task_count = {}
            overdue_by_location = {}

            for task in task_data:
                location = task.get("location_code") or task.get("from_location_code")
                if location:
                    location_task_count[location] = (
                        location_task_count.get(location, 0) + 1
                    )

                    # Check if task is overdue
                    due_date = task.get("due_date")
                    if due_date and task.get("task_status") not in [
                        "COMPLETED",
                        "CANCELLED",
                    ]:
                        try:
                            due_dt = datetime.fromisoformat(
                                due_date.replace("Z", "+00:00")
                            )
                            if datetime.now(UTC) > due_dt:
                                overdue_by_location[location] = (
                                    overdue_by_location.get(location, 0) + 1
                                )
                        except (ValueError, TypeError):
                            pass

            # Identify high-congestion locations
            if location_task_count:
                avg_tasks_per_location = sum(location_task_count.values()) / len(
                    location_task_count
                )
                high_congestion_threshold = avg_tasks_per_location * 2

                for location, task_count in location_task_count.items():
                    if task_count > high_congestion_threshold:
                        overdue_count = overdue_by_location.get(location, 0)
                        overdue_rate = (
                            (overdue_count / task_count * 100) if task_count > 0 else 0
                        )

                        bottlenecks.append(
                            {
                                "type": "LOCATION_CONGESTION",
                                "location_code": location,
                                "task_count": task_count,
                                "overdue_tasks": overdue_count,
                                "overdue_rate_percentage": overdue_rate,
                                "severity": ("HIGH" if overdue_rate > 20 else "MEDIUM"),
                                "recommendation": f"Review task allocation and worker assignment for location {location}",
                            }
                        )

        # Equipment bottlenecks
        if equipment_data:
            unavailable_equipment = [
                eq
                for eq in equipment_data
                if eq.get("status") not in ["AVAILABLE", "IDLE", "READY"]
            ]

            if len(unavailable_equipment) > 0:
                total_equipment = len(equipment_data)
                unavailability_rate = len(unavailable_equipment) / total_equipment * 100

                if unavailability_rate > 30:  # More than 30% equipment unavailable
                    bottlenecks.append(
                        {
                            "type": "EQUIPMENT_UNAVAILABILITY",
                            "total_equipment": total_equipment,
                            "unavailable_equipment": len(unavailable_equipment),
                            "unavailability_rate_percentage": unavailability_rate,
                            "severity": (
                                "HIGH" if unavailability_rate > 50 else "MEDIUM"
                            ),
                            "recommendation": (
                                "Review equipment maintenance schedules and allocation"
                            ),
                            "unavailable_equipment_list": [
                                eq.get("equipment_id")
                                for eq in unavailable_equipment[:10]
                            ],
                        }
                    )

        # Worker productivity bottlenecks
        if task_data:
            worker_task_counts = {}
            worker_completion_rates = {}

            for task in task_data:
                worker = task.get("assigned_user")
                if worker:
                    if worker not in worker_task_counts:
                        worker_task_counts[worker] = {
                            "total": 0,
                            "completed": 0,
                        }

                    worker_task_counts[worker]["total"] += 1
                    if task.get("task_status") == "COMPLETED":
                        worker_task_counts[worker]["completed"] += 1

            # Calculate completion rates
            for worker, counts in worker_task_counts.items():
                if counts["total"] > 0:
                    completion_rate = (counts["completed"] / counts["total"]) * 100
                    worker_completion_rates[worker] = completion_rate

            # Identify low-performing workers
            low_performers = [
                {"worker_id": worker, "completion_rate": rate}
                for worker, rate in worker_completion_rates.items()
                if rate < 70  # Less than 70% completion rate
            ]

            if len(low_performers) > 0:
                bottlenecks.append(
                    {
                        "type": "LOW_WORKER_PRODUCTIVITY",
                        "low_performing_workers": len(low_performers),
                        "workers": low_performers[:5],  # Top 5 lowest performers
                        "severity": "MEDIUM",
                        "recommendation": (
                            "Provide additional training or review task assignments "
                            "for underperforming workers"
                        ),
                    }
                )

        # Sort bottlenecks by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        bottlenecks.sort(key=lambda x: severity_order.get(x.get("severity", "LOW"), 2))

        return bottlenecks

    def generate_warehouse_operations_report(
        self, all_warehouse_data: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Generate comprehensive warehouse operations report.

        Args:
        ----
            all_warehouse_data: Dictionary containing all warehouse-related data

        Returns:
        -------
            Comprehensive operations report

        """
        report = {
            "report_generated": datetime.now(UTC).isoformat(),
            "configuration": self.warehouse_config,
            "summary": {},
        }

        # Task performance analysis
        task_data = all_warehouse_data.get("task", [])
        if task_data:
            report["summary"]["task_performance"] = (
                self.calculate_task_performance_metrics(task_data)
            )

        # Worker productivity analysis
        labor_data = all_warehouse_data.get("labor_activity", [])
        if task_data:
            report["worker_productivity"] = self.analyze_worker_productivity(
                task_data, labor_data
            )

        # Equipment utilization analysis
        equipment_data = all_warehouse_data.get("equipment", [])
        equipment_status_data = all_warehouse_data.get("equipment_status", [])
        if equipment_data:
            report["equipment_utilization"] = self.analyze_equipment_utilization(
                equipment_data, equipment_status_data
            )

        # Bottleneck identification
        location_data = all_warehouse_data.get("location", [])
        bottlenecks = self.identify_warehouse_bottlenecks(
            task_data, equipment_data, location_data
        )
        if bottlenecks:
            report["bottlenecks"] = {
                "total_bottlenecks": len(bottlenecks),
                "high_severity_count": len(
                    [b for b in bottlenecks if b.get("severity") == "HIGH"]
                ),
                "bottleneck_details": bottlenecks,
            }

        # Zone performance analysis
        if task_data and location_data:
            report["zone_performance"] = self._analyze_zone_performance(
                task_data, location_data
            )

        # Shift performance analysis
        if task_data:
            report["shift_analysis"] = self._analyze_shift_performance(task_data)

        return report

    def _analyze_zone_performance(
        self,
        task_data: list[dict[str, Any]],
        location_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze performance by warehouse zone."""
        zone_performance = {}

        # Create location to zone mapping
        location_zone_map = {}
        for location in location_data:
            location_code = location.get("location_code")
            zone = location.get("zone_code") or location.get("area_code")
            if location_code and zone:
                location_zone_map[location_code] = zone

        # Analyze tasks by zone
        for task in task_data:
            location = task.get("location_code") or task.get("from_location_code")
            zone = location_zone_map.get(location) if location else None

            if zone:
                if zone not in zone_performance:
                    zone_performance[zone] = {
                        "total_tasks": 0,
                        "completed_tasks": 0,
                        "total_duration_hours": 0,
                    }

                zone_perf = zone_performance[zone]
                zone_perf["total_tasks"] += 1

                if task.get("task_status") == "COMPLETED":
                    zone_perf["completed_tasks"] += 1

                # Calculate task duration
                start_time = task.get("start_time")
                end_time = task.get("end_time")

                if start_time and end_time:
                    try:
                        start_dt = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                        duration_hours = (end_dt - start_dt).total_seconds() / 3600
                        zone_perf["total_duration_hours"] += duration_hours
                    except (ValueError, TypeError):
                        pass

        # Calculate zone metrics
        for zone, performance in zone_performance.items():
            if performance["total_tasks"] > 0:
                performance["completion_rate"] = (
                    performance["completed_tasks"] / performance["total_tasks"]
                ) * 100

            if (
                performance["completed_tasks"] > 0
                and performance["total_duration_hours"] > 0
            ):
                performance["tasks_per_hour"] = (
                    performance["completed_tasks"] / performance["total_duration_hours"]
                )

        return {
            "total_zones_analyzed": len(zone_performance),
            "zone_performance_details": zone_performance,
        }

    def _analyze_shift_performance(
        self, task_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze performance by work shift."""
        shift_performance = {
            "day_shift": {"tasks": 0, "completed": 0, "total_duration": 0},
            "evening_shift": {"tasks": 0, "completed": 0, "total_duration": 0},
            "night_shift": {"tasks": 0, "completed": 0, "total_duration": 0},
        }

        for task in task_data:
            start_time = task.get("start_time") or task.get("assigned_time")
            if not start_time:
                continue

            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                hour = start_dt.hour

                # Determine shift based on hour
                if 6 <= hour < 14:
                    shift = "day_shift"
                elif 14 <= hour < 22:
                    shift = "evening_shift"
                else:
                    shift = "night_shift"

                shift_perf = shift_performance[shift]
                shift_perf["tasks"] += 1

                if task.get("task_status") == "COMPLETED":
                    shift_perf["completed"] += 1

                # Calculate duration
                end_time = task.get("end_time") or task.get("completed_time")
                if end_time:
                    try:
                        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                        duration_hours = (end_dt - start_dt).total_seconds() / 3600
                        shift_perf["total_duration"] += duration_hours
                    except (ValueError, TypeError):
                        pass

            except (ValueError, TypeError):
                continue

        # Calculate shift productivity metrics
        for shift, performance in shift_performance.items():
            if performance["tasks"] > 0:
                performance["completion_rate"] = (
                    performance["completed"] / performance["tasks"]
                ) * 100

            if performance["completed"] > 0 and performance["total_duration"] > 0:
                performance["tasks_per_hour"] = (
                    performance["completed"] / performance["total_duration"]
                )

        return shift_performance

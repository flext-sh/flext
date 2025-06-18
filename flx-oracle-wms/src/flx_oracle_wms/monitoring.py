"""Monitoring and metrics for FLX Oracle WMS pipelines."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from prometheus_client import Counter, Gauge, Histogram, generate_latest


logger = structlog.get_logger()


class PipelineMonitor:
    """Monitor pipeline executions and collect metrics."""

    def __init__(self, metrics_dir: Path = Path("./metrics")) -> None:
        """Initialize monitor."""
        self.metrics_dir = metrics_dir
        self.metrics_dir.mkdir(exist_ok=True)

        # Prometheus metrics
        self.pipeline_runs_total = Counter(
            "flx_wms_pipeline_runs_total",
            "Total number of pipeline runs",
            ["pipeline", "status"],
        )

        self.pipeline_duration_seconds = Histogram(
            "flx_wms_pipeline_duration_seconds",
            "Pipeline execution duration in seconds",
            ["pipeline"],
        )

        self.records_processed_total = Counter(
            "flx_wms_records_processed_total",
            "Total number of records processed",
            ["pipeline", "operation"],
        )

        self.pipeline_last_run = Gauge(
            "flx_wms_pipeline_last_run_timestamp",
            "Timestamp of last pipeline run",
            ["pipeline"],
        )

        self.pipeline_errors_total = Counter(
            "flx_wms_pipeline_errors_total",
            "Total number of pipeline errors",
            ["pipeline", "error_type"],
        )

    def record_pipeline_start(self, pipeline_name: str) -> None:
        """Record pipeline start."""
        self.pipeline_last_run.labels(pipeline=pipeline_name).set_to_current_time()
        self._save_event(
            {
                "event": "pipeline_start",
                "pipeline": pipeline_name,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def record_pipeline_success(
        self,
        pipeline_name: str,
        duration_seconds: float,
        records_extracted: int,
        records_loaded: int,
    ) -> None:
        """Record successful pipeline execution."""
        self.pipeline_runs_total.labels(pipeline=pipeline_name, status="success").inc()
        self.pipeline_duration_seconds.labels(pipeline=pipeline_name).observe(
            duration_seconds
        )
        self.records_processed_total.labels(
            pipeline=pipeline_name, operation="extract"
        ).inc(records_extracted)
        self.records_processed_total.labels(
            pipeline=pipeline_name, operation="load"
        ).inc(records_loaded)

        self._save_event(
            {
                "event": "pipeline_success",
                "pipeline": pipeline_name,
                "duration_seconds": duration_seconds,
                "records_extracted": records_extracted,
                "records_loaded": records_loaded,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def record_pipeline_failure(self, pipeline_name: str, error: str) -> None:
        """Record pipeline failure."""
        self.pipeline_runs_total.labels(pipeline=pipeline_name, status="failure").inc()
        self.pipeline_errors_total.labels(
            pipeline=pipeline_name, error_type=self._classify_error(error)
        ).inc()

        self._save_event(
            {
                "event": "pipeline_failure",
                "pipeline": pipeline_name,
                "error": error,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def get_pipeline_status(self, pipeline_name: str) -> dict[str, Any]:
        """Get current status of a pipeline."""
        events = self._load_pipeline_events(pipeline_name)

        if not events:
            return {
                "status": "never_run",
                "last_run": None,
                "last_success": None,
                "last_failure": None,
                "total_runs": 0,
                "success_rate": 0.0,
            }

        last_event = events[-1]
        last_success = next(
            (e for e in reversed(events) if e.get("event") == "pipeline_success"),
            None,
        )
        last_failure = next(
            (e for e in reversed(events) if e.get("event") == "pipeline_failure"),
            None,
        )

        total_runs = sum(
            1
            for e in events
            if e.get("event") in ["pipeline_success", "pipeline_failure"]
        )
        success_runs = sum(1 for e in events if e.get("event") == "pipeline_success")

        return {
            "status": (
                "running" if last_event.get("event") == "pipeline_start" else "idle"
            ),
            "last_run": last_event.get("timestamp"),
            "last_success": (last_success.get("timestamp") if last_success else None),
            "last_failure": (last_failure.get("timestamp") if last_failure else None),
            "total_runs": total_runs,
            "success_rate": (success_runs / total_runs if total_runs > 0 else 0.0),
        }

    def get_all_pipeline_statuses(self) -> dict[str, dict[str, Any]]:
        """Get status of all pipelines."""
        statuses = {}

        # Find all pipeline event files
        for event_file in self.metrics_dir.glob("pipeline_*.json"):
            pipeline_name = event_file.stem.replace("pipeline_", "")
            statuses[pipeline_name] = self.get_pipeline_status(pipeline_name)

        return statuses

    def get_metrics(self) -> dict[str, Any]:
        """Get aggregated metrics."""
        all_events = []

        # Load all events
        for event_file in self.metrics_dir.glob("pipeline_*.json"):
            events = self._load_events_from_file(event_file)
            all_events.extend(events)

        # Calculate metrics
        total_runs = sum(
            1
            for e in all_events
            if e.get("event") in ["pipeline_success", "pipeline_failure"]
        )
        successful_runs = sum(
            1 for e in all_events if e.get("event") == "pipeline_success"
        )
        failed_runs = sum(1 for e in all_events if e.get("event") == "pipeline_failure")

        total_records_extracted = sum(
            e.get("records_extracted", 0)
            for e in all_events
            if e.get("event") == "pipeline_success"
        )
        total_records_loaded = sum(
            e.get("records_loaded", 0)
            for e in all_events
            if e.get("event") == "pipeline_success"
        )

        avg_duration = None
        durations = [
            e.get("duration_seconds")
            for e in all_events
            if e.get("event") == "pipeline_success"
            and e.get("duration_seconds") is not None
        ]
        if durations:
            avg_duration = sum(d for d in durations if d is not None) / len(durations)

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": (successful_runs / total_runs if total_runs > 0 else 0.0),
            "total_records_extracted": total_records_extracted,
            "total_records_loaded": total_records_loaded,
            "average_duration_seconds": avg_duration,
        }

    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest()

    def _save_event(self, event: dict[str, Any]) -> None:
        """Save an event to file."""
        pipeline_name = event.get("pipeline", "unknown")
        event_file = self.metrics_dir / f"pipeline_{pipeline_name}.json"

        # Load existing events
        events = self._load_events_from_file(event_file)

        # Add new event
        events.append(event)

        # Keep only last 1000 events
        if len(events) > 1000:
            events = events[-1000:]

        # Save back
        event_file.write_text(json.dumps(events, indent=2))

    def _load_pipeline_events(self, pipeline_name: str) -> list[dict[str, Any]]:
        """Load events for a specific pipeline."""
        event_file = self.metrics_dir / f"pipeline_{pipeline_name}.json"
        return self._load_events_from_file(event_file)

    def _load_events_from_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Load events from a file."""
        if not file_path.exists():
            return []

        try:
            return json.loads(file_path.read_text())
        except (OSError, json.JSONDecodeError):
            logger.error("Failed to load events", file=str(file_path))
            return []

    def _classify_error(self, error: str) -> str:
        """Classify error type from error message."""
        error_lower = error.lower()

        if "connection" in error_lower or "timeout" in error_lower:
            return "connection"
        if "authentication" in error_lower or "unauthorized" in error_lower:
            return "authentication"
        if "not found" in error_lower or "404" in error_lower:
            return "not_found"
        if "validation" in error_lower or "invalid" in error_lower:
            return "validation"
        return "other"

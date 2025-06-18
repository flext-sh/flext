"""Monitoring service for Oracle OIC."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import structlog

log = structlog.get_logger()


class MonitoringService:
    """Provides monitoring capabilities for Oracle OIC."""

    def __init__(self, base_url: str, auth_config: dict) -> None:
        """Initialize the monitoring service."""
        self.base_url = base_url
        self.auth_config = auth_config
        self._client = None
        self._access_token = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if not self._client:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self._get_auth_headers(),
                timeout=60.0,
            )
        return self._client

    def _get_auth_headers(self) -> dict:
        """Get authentication headers."""
        if not self._access_token:
            self._refresh_token()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }

    def _refresh_token(self) -> None:
        """Refresh OAuth2 access token."""
        with httpx.Client() as client:
            response = client.post(
                self.auth_config["oauth_token_url"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.auth_config["oauth_client_id"],
                    "client_secret": self.auth_config["oauth_client_secret"],
                    "scope": f"{self.base_url}urn:opc:resource:consumer::all",
                },
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]

    def check_health(self, detailed: bool = False) -> dict:
        """Check OIC instance health."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
        }

        # Check API health
        try:
            response = self.client.get("/ic/api/integration/v1/integrations?limit=1")
            if response.status_code == 200:
                health_status["components"]["api"] = "healthy"
            else:
                health_status["components"]["api"] = "unhealthy"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["api"] = "error"
            health_status["status"] = "unhealthy"
            log.error("API health check failed", error=str(e))

        if detailed:
            # Check additional components
            health_status.update(self._detailed_health_check())

        return health_status

    def _detailed_health_check(self) -> dict:
        """Perform detailed health checks."""
        return {
            "connections": self._check_connections_health(),
            "integrations": self._check_integrations_health(),
            "execution": self._check_execution_health(),
        }

    def _check_connections_health(self) -> dict:
        """Check connections health."""
        try:
            response = self.client.get("/ic/api/integration/v1/connections?limit=100")
            if response.status_code == 200:
                connections = response.json().get("items", [])
                active = sum(1 for c in connections if c.get("status") == "ACTIVE")
                total = len(connections)
                return {
                    "status": "healthy" if active > 0 else "warning",
                    "active": active,
                    "total": total,
                }
        except Exception as e:
            log.error("Failed to check connections health", error=str(e))
            return {"status": "error", "error": str(e)}

    def _check_integrations_health(self) -> dict:
        """Check integrations health."""
        try:
            response = self.client.get("/ic/api/integration/v1/integrations?limit=100")
            if response.status_code == 200:
                integrations = response.json().get("items", [])
                active = sum(1 for i in integrations if i.get("status") == "ACTIVE")
                configured = sum(
                    1 for i in integrations if i.get("status") == "CONFIGURED"
                )
                total = len(integrations)
                return {
                    "status": "healthy" if active > 0 else "warning",
                    "active": active,
                    "configured": configured,
                    "total": total,
                }
        except Exception as e:
            log.error("Failed to check integrations health", error=str(e))
            return {"status": "error", "error": str(e)}

    def _check_execution_health(self) -> dict:
        """Check execution health."""
        try:
            # Get recent execution instances
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)

            params = {
                "startdate": start_time.isoformat(),
                "enddate": end_time.isoformat(),
                "limit": 100,
            }

            response = self.client.get(
                "/ic/api/integration/v1/monitoring/instances",
                params=params,
            )

            if response.status_code == 200:
                instances = response.json().get("items", [])
                successful = sum(1 for i in instances if i.get("status") == "COMPLETED")
                failed = sum(1 for i in instances if i.get("status") == "FAILED")
                in_progress = sum(
                    1 for i in instances if i.get("status") == "IN_PROGRESS"
                )

                return {
                    "status": "healthy" if failed < successful else "warning",
                    "successful": successful,
                    "failed": failed,
                    "in_progress": in_progress,
                    "window": "1h",
                }
        except Exception as e:
            log.error("Failed to check execution health", error=str(e))
            return {"status": "error", "error": str(e)}

    def get_performance_metrics(self, window_hours: int = 24) -> dict:
        """Get performance metrics for the specified time window."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=window_hours)

        metrics = {
            "window": f"{window_hours}h",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        # Get execution metrics
        try:
            params = {
                "startdate": start_time.isoformat(),
                "enddate": end_time.isoformat(),
                "limit": 1000,
            }

            response = self.client.get(
                "/ic/api/integration/v1/monitoring/instances",
                params=params,
            )

            if response.status_code == 200:
                instances = response.json().get("items", [])

                # Calculate metrics
                total_executions = len(instances)
                successful = sum(1 for i in instances if i.get("status") == "COMPLETED")
                failed = sum(1 for i in instances if i.get("status") == "FAILED")

                # Calculate average duration for completed instances
                durations = [
                    instance["duration"]
                    for instance in instances
                    if instance.get("status") == "COMPLETED"
                    and instance.get("duration")
                ]

                metrics["executions"] = {
                    "total": total_executions,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (
                        (successful / total_executions * 100)
                        if total_executions > 0
                        else 0
                    ),
                    "avg_duration_ms": (
                        sum(durations) / len(durations) if durations else 0
                    ),
                }

                # Get throughput by hour
                metrics["throughput"] = self._calculate_throughput(
                    instances, window_hours
                )

        except Exception as e:
            log.error("Failed to get performance metrics", error=str(e))
            metrics["error"] = str(e)

        return metrics

    def _calculate_throughput(self, instances: list[dict], window_hours: int) -> dict:
        """Calculate throughput metrics."""
        # Group by hour
        hourly_counts = {}

        for instance in instances:
            if start_time := instance.get("startTime"):
                hour_key = start_time[:13]  # YYYY-MM-DDTHH
                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

        if hourly_counts:
            return {
                "avg_per_hour": sum(hourly_counts.values()) / len(hourly_counts),
                "max_per_hour": max(hourly_counts.values()),
                "min_per_hour": min(hourly_counts.values()),
            }
        return {
            "avg_per_hour": 0,
            "max_per_hour": 0,
            "min_per_hour": 0,
        }

    def analyze_errors(
        self,
        window_hours: int = 24,
        integration_id: str | None = None,
    ) -> dict:
        """Analyze error patterns in the specified time window."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=window_hours)

        error_analysis = {
            "window": f"{window_hours}h",
            "integration_filter": integration_id,
            "patterns": {},
            "top_errors": [],
        }

        try:
            params = {
                "startdate": start_time.isoformat(),
                "enddate": end_time.isoformat(),
                "status": "FAILED",
                "limit": 500,
            }

            if integration_id:
                params["integrationId"] = integration_id

            response = self.client.get(
                "/ic/api/integration/v1/monitoring/instances",
                params=params,
            )

            if response.status_code == 200:
                failed_instances = response.json().get("items", [])

                # Analyze error patterns
                error_counts = {}
                integration_errors = {}

                for instance in failed_instances:
                    error_msg = instance.get("errorMessage", "Unknown error")
                    error_counts[error_msg] = error_counts.get(error_msg, 0) + 1

                    int_id = instance.get("integrationId")
                    if int_id:
                        if int_id not in integration_errors:
                            integration_errors[int_id] = []
                        integration_errors[int_id].append(error_msg)

                # Get top errors
                sorted_errors = sorted(
                    error_counts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]

                error_analysis["top_errors"] = [
                    {"error": error, "count": count} for error, count in sorted_errors
                ]

                error_analysis["patterns"] = {
                    "total_errors": len(failed_instances),
                    "unique_errors": len(error_counts),
                    "affected_integrations": len(integration_errors),
                }

        except Exception as e:
            log.error("Failed to analyze errors", error=str(e))
            error_analysis["error"] = str(e)

        return error_analysis

    def get_usage_analytics(self, window_days: int = 7) -> dict:
        """Get usage analytics for the specified time window."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=window_days)

        analytics = {
            "window": f"{window_days}d",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        try:
            # Get execution count by integration
            params = {
                "startdate": start_time.isoformat(),
                "enddate": end_time.isoformat(),
                "limit": 10000,
            }

            response = self.client.get(
                "/ic/api/integration/v1/monitoring/instances",
                params=params,
            )

            if response.status_code == 200:
                instances = response.json().get("items", [])

                # Analyze usage by integration
                integration_usage = {}
                daily_usage = {}

                for instance in instances:
                    # Count by integration
                    int_id = instance.get("integrationId")
                    if int_id:
                        integration_usage[int_id] = integration_usage.get(int_id, 0) + 1

                    # Count by day
                    if start_time := instance.get("startTime"):
                        day_key = start_time[:10]  # YYYY-MM-DD
                        daily_usage[day_key] = daily_usage.get(day_key, 0) + 1

                # Sort integrations by usage
                sorted_integrations = sorted(
                    integration_usage.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:20]

                analytics["top_integrations"] = [
                    {"integration": int_id, "executions": count}
                    for int_id, count in sorted_integrations
                ]

                analytics["daily_trend"] = [
                    {"date": date, "executions": count}
                    for date, count in sorted(daily_usage.items())
                ]

                analytics["summary"] = {
                    "total_executions": len(instances),
                    "unique_integrations": len(integration_usage),
                    "avg_daily_executions": (
                        len(instances) / window_days if window_days > 0 else 0
                    ),
                }

        except Exception as e:
            log.error("Failed to get usage analytics", error=str(e))
            analytics["error"] = str(e)

        return analytics

    def __del__(self) -> None:
        """Clean up resources."""
        if self._client:
            self._client.close()

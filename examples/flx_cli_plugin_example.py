#!/usr/bin/env python3
"""Example of how to create and register plugins for the FLX CLI.

This example demonstrates the declarative plugin system that allows
commands to be automatically exposed via CLI, REST API, and web interface.

Architecture:
    - Plugin commands are registered declaratively using decorators
    - Commands are automatically available via multiple interfaces
    - Dependency injection is supported for command bus integration
    - Type-safe command handling with middleware support

Usage:
    1. Run this script to register the example plugins
    2. Use: flx database backup /path/to/backup
    3. Use: flx health_check
    4. Use: flx monitoring list_metrics
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import secrets
import time
import uuid
from typing import Any

# Import the plugin registration decorators
from flx.adapters.inbound.fire_cli import register_command, register_command_group


# Example 1: Command Group Plugin (Database operations)
@register_command_group("database")
class DatabaseCommands:
    """Database management commands plugin.

    This plugin provides database backup, restore, and maintenance operations.
    All commands in this group are available as: flx database <command>
    """

    def __init__(self, command_bus=None) -> None:
        """Initialize with optional command bus injection."""
        self.command_bus = command_bus
        self.connection_pool = "mock_connection_pool"

    async def backup(self, path: str, compress: bool = True) -> dict[str, Any]:
        """Create a database backup.

        Args:
            path: Path where to save the backup
            compress: Whether to compress the backup (default: True)

        Returns:
            Dictionary with backup status and metadata
        """
        # Simulate async backup operation
        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "backup_path": path,
            "compressed": compress,
            "size_mb": 150.5,
            "tables_backed_up": 25,
            "timestamp": "2025-06-12T15:30:00Z",
        }

    async def restore(
        self, backup_path: str, target_db: str = "main"
    ) -> dict[str, Any]:
        """Restore database from backup.

        Args:
            backup_path: Path to the backup file
            target_db: Target database name (default: main)

        Returns:
            Dictionary with restore status
        """
        await asyncio.sleep(0.2)

        return {
            "status": "success",
            "restored_from": backup_path,
            "target_database": target_db,
            "tables_restored": 25,
            "records_restored": 10450,
        }

    def list_tables(self) -> dict[str, Any]:
        """List all database tables."""
        return {
            "tables": [
                {"name": "users", "rows": 1250, "size_mb": 5.2},
                {"name": "orders", "rows": 3400, "size_mb": 12.8},
                {"name": "products", "rows": 850, "size_mb": 3.1},
            ],
            "total_tables": 3,
            "total_size_mb": 21.1,
        }

    async def maintenance(self, operation: str = "analyze") -> dict[str, Any]:
        """Run database maintenance operations.

        Args:
            operation: Type of maintenance (analyze, vacuum, reindex)
        """
        operations = {
            "analyze": "Analyzing table statistics",
            "vacuum": "Reclaiming disk space",
            "reindex": "Rebuilding indexes",
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        await asyncio.sleep(0.3)

        return {
            "status": "completed",
            "operation": operation,
            "description": operations[operation],
            "duration_seconds": 0.3,
            "space_reclaimed_mb": 5.7 if operation == "vacuum" else 0,
        }


# Example 2: Command Group with Command Bus Integration
@register_command_group("monitoring")
class MonitoringCommands:
    """System monitoring commands plugin.

    This plugin provides system monitoring and metrics collection.
    Commands are available as: flx monitoring <command>
    """

    def __init__(self, command_bus) -> None:
        """Initialize with command bus for integration."""
        self.command_bus = command_bus
        self.metrics_store = {
            "cpu_usage": 25.5,
            "memory_usage": 512.0,
            "disk_usage": 85.2,
            "network_io": 1024.0,
        }

    def list_metrics(self) -> dict[str, Any]:
        """List all available system metrics."""
        return {
            "metrics": list(self.metrics_store.keys()),
            "total_metrics": len(self.metrics_store),
            "collection_interval": "30s",
        }

    def get_metric(self, metric_name: str) -> dict[str, Any]:
        """Get current value of a specific metric.

        Args:
            metric_name: Name of the metric to retrieve
        """
        if metric_name not in self.metrics_store:
            return {"error": f"Metric '{metric_name}' not found"}

        return {
            "metric": metric_name,
            "value": self.metrics_store[metric_name],
            "timestamp": "2025-06-12T15:30:00Z",
            "unit": "percent" if "usage" in metric_name else "bytes",
        }

    async def collect_all(self) -> dict[str, Any]:
        """Collect all system metrics."""
        # Simulate async collection from various sources
        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "metrics": self.metrics_store,
            "collection_time": "2025-06-12T15:30:00Z",
            "collection_duration_ms": 100,
        }


# Example 3: Standalone Command Plugin
@register_command("health-check")
async def health_check() -> dict[str, Any]:
    """Comprehensive system health check.

    This standalone command performs a full system health assessment.
    Available as: flx health_check
    """
    # Simulate health checks
    await asyncio.sleep(0.2)

    checks = [
        {"name": "database", "status": "healthy", "latency_ms": 5},
        {"name": "cache", "status": "healthy", "latency_ms": 2},
        {"name": "api", "status": "healthy", "latency_ms": 15},
        {"name": "disk_space", "status": "warning", "usage_percent": 85},
    ]

    overall_status = (
        "warning" if any(
            c["status"] == "warning" for c in checks) else "healthy")

    return {
        "overall_status": overall_status,
        "checks": checks,
        "total_checks": len(checks),
        "healthy_checks": len([c for c in checks if c["status"] == "healthy"]),
        "warning_checks": len([c for c in checks if c["status"] == "warning"]),
        "failed_checks": len([c for c in checks if c["status"] == "failed"]),
    }


# Example 4: Plugin with Async/Sync Mixed Commands
@register_command_group("utilities")
class UtilityCommands:
    """Utility commands for common operations."""

    def uuid(self, count: int = 1) -> dict[str, Any]:
        """Generate UUIDs.

        Args:
            count: Number of UUIDs to generate (default: 1)
        """
        uuids = [str(uuid.uuid4()) for _ in range(count)]

        return {"uuids": uuids, "count": count, "format": "uuid4"}

    async def hash_password(self, password: str) -> dict[str, Any]:
        """Hash a password securely.

        Args:
            password: Password to hash
        """
        # Simulate async hashing operation
        await asyncio.sleep(0.1)

        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000)

        return {
            "hashed_password": hashed.hex(),
            "salt": salt,
            "algorithm": "pbkdf2_hmac_sha256",
            "iterations": 100000,
        }

    def timestamp(self, format_type: str = "iso") -> dict[str, Any]:
        """Get current timestamp in various formats.

        Args:
            format_type: Format type (iso, unix, readable)
        """
        now = datetime.datetime.now()

        formats = {
            "iso": now.isoformat(),
            "unix": int(time.time()),
            "readable": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return {
            "timestamp": formats.get(format_type, formats["iso"]),
            "format": format_type,
            "timezone": "UTC",
        }


def main() -> None:
    """Demonstrate plugin registration and usage."""

    # The plugins are automatically registered when this module is imported


if __name__ == "__main__":
    main()

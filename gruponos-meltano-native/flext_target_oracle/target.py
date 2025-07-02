"""Advanced Oracle target with SQLAlchemy and performance optimizations."""

from __future__ import annotations

import asyncio
import logging
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from singer_sdk import typing as th
from singer_sdk.sinks import SQLSink
from singer_sdk.target_base import Target

try:
    from flext_target_oracle.sinks import OracleSink
except ImportError:
    from sinks import OracleSink


class TargetOracle(Target):
    """Advanced Oracle target with SQLAlchemy and performance features."""

    name = "flext-target-oracle"

    # Performance configuration
    config_jsonschema = th.PropertiesList(
        # Connection settings
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="Oracle database host"
        ),
        th.Property(
            "port",
            th.StringType,
            default="1521",
            description="Oracle database port"
        ),
        th.Property(
            "database",
            th.StringType,
            description="Oracle database SID or service name"
        ),
        th.Property(
            "service_name",
            th.StringType,
            description="Oracle service name (preferred over SID)"
        ),
        th.Property(
            "username",
            th.StringType,
            required=True,
            description="Oracle username"
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            secret=True,
            description="Oracle password"
        ),
        th.Property(
            "schema",
            th.StringType,
            description="Oracle schema name"
        ),

        # Protocol settings for Autonomous Database
        th.Property(
            "protocol",
            th.StringType,
            default="tcp",
            description="Connection protocol (tcp/tcps for Autonomous DB)"
        ),
        th.Property(
            "wallet_location",
            th.StringType,
            description="Oracle wallet location for TCPS connections"
        ),

        # Performance settings
        th.Property(
            "batch_size",
            th.IntegerType,
            default=5000,
            description="Number of records to batch before inserting"
        ),
        th.Property(
            "max_workers",
            th.IntegerType,
            default=4,
            description="Maximum number of worker threads for parallel processing"
        ),
        th.Property(
            "pool_size",
            th.IntegerType,
            default=10,
            description="SQLAlchemy connection pool size"
        ),
        th.Property(
            "pool_recycle",
            th.IntegerType,
            default=3600,
            description="Connection pool recycle time in seconds"
        ),
        th.Property(
            "pool_pre_ping",
            th.BooleanType,
            default=True,
            description="Enable connection pool pre-ping validation"
        ),

        # Table management
        th.Property(
            "table_prefix",
            th.StringType,
            default="",
            description="Prefix for table names"
        ),
        th.Property(
            "table_suffix",
            th.StringType,
            default="",
            description="Suffix for table names"
        ),
        th.Property(
            "add_record_metadata",
            th.BooleanType,
            default=True,
            description="Add _loaded_at and other metadata columns"
        ),
        th.Property(
            "hard_delete",
            th.BooleanType,
            default=False,
            description="Hard delete records (vs soft delete)"
        ),

        # Data processing options
        th.Property(
            "validate_records",
            th.BooleanType,
            default=True,
            description="Validate records against schema before insert"
        ),
        th.Property(
            "default_target_schema",
            th.StringType,
            description="Default schema for new tables"
        ),
        th.Property(
            "denest_properties",
            th.BooleanType,
            default=False,
            description="Denest JSON properties into columns"
        ),
        th.Property(
            "max_varchar_length",
            th.IntegerType,
            default=4000,
            description="Maximum VARCHAR2 length before using CLOB"
        ),

        # Advanced performance features
        th.Property(
            "use_bulk_insert",
            th.BooleanType,
            default=True,
            description="Use Oracle bulk insert operations"
        ),
        th.Property(
            "parallel_degree",
            th.IntegerType,
            default=4,
            description="Oracle parallel processing degree"
        ),
        th.Property(
            "commit_frequency",
            th.IntegerType,
            default=1000,
            description="Commit every N records for large batches"
        ),
        th.Property(
            "use_merge_upsert",
            th.BooleanType,
            default=False,
            description="Use MERGE statements for upserts instead of INSERT"
        ),

        # Monitoring and debugging
        th.Property(
            "enable_performance_metrics",
            th.BooleanType,
            default=True,
            description="Enable detailed performance metrics logging"
        ),
        th.Property(
            "log_sql_statements",
            th.BooleanType,
            default=False,
            description="Log SQL statements (debug mode)"
        ),
        th.Property(
            "connection_timeout",
            th.IntegerType,
            default=60,
            description="Database connection timeout in seconds"
        ),

        # Error handling
        th.Property(
            "max_retries",
            th.IntegerType,
            default=3,
            description="Maximum retry attempts for failed operations"
        ),
        th.Property(
            "retry_delay",
            th.NumberType,
            default=1.0,
            description="Delay between retry attempts in seconds"
        ),
        th.Property(
            "ignore_duplicate_keys",
            th.BooleanType,
            default=True,
            description="Ignore duplicate key errors during insert"
        )
    ).to_dict()

    default_sink_class = OracleSink

    def __init__(self, *args, **kwargs):
        """Initialize the Oracle target with performance monitoring."""
        super().__init__(*args, **kwargs)

        # Performance metrics
        self._metrics = {
            'records_processed': 0,
            'records_failed': 0,
            'batches_processed': 0,
            'total_processing_time': 0.0,
            'connection_errors': 0,
            'retry_attempts': 0
        }

        # Thread safety
        self._metrics_lock = threading.Lock()

        # Worker pool for parallel processing
        max_workers = self.config.get("max_workers", 4)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        self.logger.info(
            f"Initialized {self.name} with max_workers={max_workers}, "
            f"batch_size={self.config.get('batch_size', 5000)}"
        )

    def get_sink_class(self, stream_name: str) -> type[OracleSink]:
        """Return the sink class for the given stream."""
        return OracleSink

    def update_metrics(self, metric_name: str, value: int | float = 1) -> None:
        """Thread-safe metrics update."""
        with self._metrics_lock:
            if metric_name in self._metrics:
                self._metrics[metric_name] += value
            else:
                self._metrics[metric_name] = value

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        with self._metrics_lock:
            return self._metrics.copy()

    def log_performance_summary(self) -> None:
        """Log comprehensive performance summary."""
        metrics = self.get_metrics()

        self.logger.info("=== ORACLE TARGET PERFORMANCE SUMMARY ===")
        self.logger.info(f"Records processed: {metrics['records_processed']:,}")
        self.logger.info(f"Records failed: {metrics['records_failed']:,}")
        self.logger.info(f"Batches processed: {metrics['batches_processed']:,}")
        self.logger.info(f"Total processing time: {metrics['total_processing_time']:.2f}s")
        self.logger.info(f"Connection errors: {metrics['connection_errors']:,}")
        self.logger.info(f"Retry attempts: {metrics['retry_attempts']:,}")

        if metrics['records_processed'] > 0:
            avg_time = metrics['total_processing_time'] / metrics['records_processed']
            throughput = metrics['records_processed'] / metrics['total_processing_time'] if metrics['total_processing_time'] > 0 else 0
            self.logger.info(f"Average time per record: {avg_time*1000:.2f}ms")
            self.logger.info(f"Throughput: {throughput:.2f} records/second")

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=True)

            if hasattr(self, 'config') and hasattr(self, '_metrics_lock') and self.config.get("enable_performance_metrics"):
                self.log_performance_summary()
        except Exception:
            # Ignore cleanup errors
            pass


if __name__ == "__main__":
    TargetOracle.cli()

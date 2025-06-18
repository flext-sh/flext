"""Advanced pipeline orchestrator for FLX Oracle WMS with full functionality.

This module implements all advanced orchestration features:
- Dynamic pipeline configuration
- Parallel execution with resource management
- State management and checkpointing
- Error recovery and retry logic
- Performance optimization
- Real-time monitoring and alerting
- Data quality validation
- Incremental extraction
- Schedule-based execution
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import tempfile
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import croniter
import structlog
from pydantic import BaseModel

from flx_oracle_wms.config import PipelineConfig, PipelineDefinition, RuntimeConfig
from flx_oracle_wms.monitoring import AlertManager, MetricsCollector, PipelineMonitor


logger = structlog.get_logger()


class PipelineState(BaseModel):
    """Pipeline execution state."""

    pipeline_name: str
    status: str  # running, completed, failed, paused
    start_time: datetime
    end_time: datetime | None = None
    records_extracted: int = 0
    records_loaded: int = 0
    errors: list[str] = []
    checkpoints: dict[str, Any] = {}
    retry_count: int = 0


class ExecutionContext(BaseModel):
    """Execution context for a pipeline run."""

    run_id: str
    pipeline_name: str
    start_time: datetime
    runtime_config: RuntimeConfig
    state: PipelineState | None = None
    metrics: dict[str, Any] = {}


class ResourceManager:
    """Manage system resources for pipeline execution."""

    def __init__(self, max_memory_mb: int = 4096, max_cpu_percent: int = 80) -> None:
        """Initialize resource manager.

        Args:
        ----
            max_memory_mb: Maximum memory usage in MB
            max_cpu_percent: Maximum CPU usage percentage

        """
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self._active_pipelines = {}
        self._resource_lock = asyncio.Lock()

    async def acquire_resources(
        self, pipeline_name: str, estimated_memory_mb: int = 512
    ) -> bool:
        """Acquire resources for pipeline execution.

        Args:
        ----
            pipeline_name: Pipeline name
            estimated_memory_mb: Estimated memory requirement

        Returns:
        -------
            True if resources acquired

        """
        async with self._resource_lock:
            current_usage = sum(self._active_pipelines.values())

            if current_usage + estimated_memory_mb > self.max_memory_mb:
                logger.warning(
                    "Insufficient memory for pipeline",
                    pipeline=pipeline_name,
                    required=estimated_memory_mb,
                    available=self.max_memory_mb - current_usage,
                )
                return False

            self._active_pipelines[pipeline_name] = estimated_memory_mb
            return True

    async def release_resources(self, pipeline_name: str) -> None:
        """Release resources after pipeline execution."""
        async with self._resource_lock:
            self._active_pipelines.pop(pipeline_name, None)

    def get_resource_usage(self) -> dict[str, Any]:
        """Get current resource usage."""
        return {
            "active_pipelines": len(self._active_pipelines),
            "memory_used_mb": sum(self._active_pipelines.values()),
            "memory_available_mb": self.max_memory_mb
            - sum(self._active_pipelines.values()),
            "pipelines": dict(self._active_pipelines),
        }


class StateManager:
    """Manage pipeline state and checkpoints."""

    def __init__(self, state_dir: Path) -> None:
        """Initialize state manager.

        Args:
        ----
            state_dir: Directory for state files

        """
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, pipeline_name: str, state: dict[str, Any]) -> None:
        """Save pipeline state."""
        state_file = self.state_dir / f"{pipeline_name}_state.json"

        # Create backup before overwriting
        if state_file.exists():
            backup_file = self.state_dir / f"{pipeline_name}_state.json.bak"
            state_file.rename(backup_file)

        try:
            state_file.write_text(json.dumps(state, indent=2, default=str))
        except Exception:
            # Restore backup on failure
            if backup_file.exists():
                backup_file.rename(state_file)
            raise

    def load_state(self, pipeline_name: str) -> dict[str, Any] | None:
        """Load pipeline state."""
        state_file = self.state_dir / f"{pipeline_name}_state.json"

        if not state_file.exists():
            return None

        try:
            return json.loads(state_file.read_text())
        except Exception as e:
            logger.error(f"Failed to load state for {pipeline_name}: {e}")
            return None

    def save_checkpoint(
        self, pipeline_name: str, checkpoint_name: str, data: dict[str, Any]
    ) -> None:
        """Save a checkpoint during pipeline execution."""
        checkpoint_file = (
            self.state_dir / f"{pipeline_name}_checkpoint_{checkpoint_name}.json"
        )
        checkpoint_file.write_text(json.dumps(data, indent=2, default=str))

    def load_checkpoint(
        self, pipeline_name: str, checkpoint_name: str
    ) -> dict[str, Any] | None:
        """Load a checkpoint."""
        checkpoint_file = (
            self.state_dir / f"{pipeline_name}_checkpoint_{checkpoint_name}.json"
        )

        if not checkpoint_file.exists():
            return None

        try:
            return json.loads(checkpoint_file.read_text())
        except Exception as e:
            logger.error(
                f"Failed to load checkpoint {checkpoint_name} for {pipeline_name}: {e}"
            )
            return None

    def clear_checkpoints(self, pipeline_name: str) -> None:
        """Clear all checkpoints for a pipeline."""
        for checkpoint_file in self.state_dir.glob(
            f"{pipeline_name}_checkpoint_*.json"
        ):
            checkpoint_file.unlink()


class DataQualityValidator:
    """Validate data quality during pipeline execution."""

    def __init__(self, rules: dict[str, Any]) -> None:
        """Initialize validator.

        Args:
        ----
            rules: Validation rules configuration

        """
        self.rules = rules
        self._validation_results = defaultdict(list)

    def validate_records(
        self, stream_name: str, records: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate a batch of records.

        Args:
        ----
            stream_name: Stream name
            records: Records to validate

        Returns:
        -------
            Validation results

        """
        results = {
            "stream": stream_name,
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "errors": [],
        }

        stream_rules = self.rules.get(stream_name, {})

        for i, record in enumerate(records):
            errors = self._validate_record(record, stream_rules)

            if errors:
                results["invalid_records"] += 1
                results["errors"].append({"record_index": i, "errors": errors})
            else:
                results["valid_records"] += 1

        self._validation_results[stream_name].append(results)
        return results

    def _validate_record(
        self, record: dict[str, Any], rules: dict[str, Any]
    ) -> list[str]:
        """Validate a single record."""
        # Required fields
        errors = [
            f"Missing required field: {field}"
            for field in rules.get("required_fields", [])
            if field not in record or record[field] is None
        ]

        # Field types
        for field, expected_type in rules.get("field_types", {}).items():
            if field in record and record[field] is not None:
                actual_type = type(record[field]).__name__
                if actual_type != expected_type:
                    errors.append(
                        f"Invalid type for {field}: expected {expected_type}, got {actual_type}"
                    )

        # Custom validations
        if "custom_validators" in rules:
            for validator_name, validator_func in rules["custom_validators"].items():
                try:
                    if not validator_func(record):
                        errors.append(f"Custom validation failed: {validator_name}")
                except Exception as e:
                    errors.append(f"Validation error in {validator_name}: {e!s}")

        return errors

    def get_validation_summary(self) -> dict[str, Any]:
        """Get validation summary."""
        summary = {
            "streams": {},
            "total_records": 0,
            "total_valid": 0,
            "total_invalid": 0,
        }

        for stream, results_list in self._validation_results.items():
            stream_summary = {
                "total_records": sum(r["total_records"] for r in results_list),
                "valid_records": sum(r["valid_records"] for r in results_list),
                "invalid_records": sum(r["invalid_records"] for r in results_list),
                "validation_runs": len(results_list),
            }

            summary["streams"][stream] = stream_summary
            summary["total_records"] += stream_summary["total_records"]
            summary["total_valid"] += stream_summary["valid_records"]
            summary["total_invalid"] += stream_summary["invalid_records"]

        return summary


class WMSAdvancedOrchestrator:
    """Advanced orchestrator with full functionality."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize advanced orchestrator.

        Args:
        ----
            config: Pipeline configuration

        """
        self.config = config
        self._setup_logging()

        # Initialize components
        self.monitor = PipelineMonitor() if config.monitoring.enabled else None
        self.metrics = MetricsCollector() if config.monitoring.enabled else None
        self.alerts = AlertManager() if config.monitoring.alert_enabled else None

        self.resource_manager = ResourceManager(
            max_memory_mb=config.resource_limits.max_memory_mb,
            max_cpu_percent=config.resource_limits.max_cpu_percent,
        )

        self.state_manager = StateManager(Path(config.state_dir or "./state"))

        self.data_validator = (
            DataQualityValidator(config.data_quality_rules or {})
            if config.validate_data
            else None
        )

        # Execution tracking
        self._active_executions: dict[str, ExecutionContext] = {}
        self._execution_history: list[ExecutionContext] = []
        self._scheduler_task: asyncio.Task | None = None

    def _setup_logging(self) -> None:
        """Setup structured logging."""
        processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if self.config.log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    async def start(self) -> None:
        """Start the orchestrator."""
        logger.info("Starting WMS Advanced Orchestrator")

        # Start monitoring
        if self.monitor:
            await self.monitor.start()

        # Start scheduler if schedules are defined
        if any(p.schedule for p in self.config.pipelines):
            self._scheduler_task = asyncio.create_task(self._schedule_runner())

        logger.info("Orchestrator started successfully")

    async def stop(self) -> None:
        """Stop the orchestrator."""
        logger.info("Stopping WMS Advanced Orchestrator")

        # Cancel scheduler
        if self._scheduler_task:
            self._scheduler_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._scheduler_task

        # Wait for active executions
        if self._active_executions:
            logger.info(f"Waiting for {len(self._active_executions)} active pipelines")
            await asyncio.gather(
                *[ctx.state for ctx in self._active_executions.values()],
                return_exceptions=True,
            )

        # Stop monitoring
        if self.monitor:
            await self.monitor.stop()

        logger.info("Orchestrator stopped")

    async def run_pipeline(
        self, pipeline_name: str, force: bool = False, checkpoint: str | None = None
    ) -> dict[str, Any]:
        """Run a pipeline with advanced features.

        Args:
        ----
            pipeline_name: Pipeline to run
            force: Force run even if recently executed
            checkpoint: Resume from checkpoint

        Returns:
        -------
            Execution results

        """
        pipeline = self._get_pipeline(pipeline_name)
        if not pipeline:
            return {"status": "error", "error": f"Pipeline '{pipeline_name}' not found"}

        if not pipeline.enabled and not force:
            return {"status": "skipped", "reason": "Pipeline is disabled"}

        # Check if already running
        if pipeline_name in self._active_executions:
            return {
                "status": "error",
                "error": f"Pipeline '{pipeline_name}' is already running",
            }

        # Create execution context
        run_id = f"{pipeline_name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        runtime_config = self._create_runtime_config(pipeline, checkpoint)

        context = ExecutionContext(
            run_id=run_id,
            pipeline_name=pipeline_name,
            start_time=datetime.now(UTC),
            runtime_config=runtime_config,
        )

        # Acquire resources
        estimated_memory = pipeline.resource_requirements.get("memory_mb", 512)
        if not await self.resource_manager.acquire_resources(
            pipeline_name, estimated_memory
        ):
            return {"status": "error", "error": "Insufficient resources available"}

        try:
            # Track execution
            self._active_executions[pipeline_name] = context

            # Execute pipeline
            result = await self._execute_pipeline_async(context)

            # Save execution history
            context.end_time = datetime.now(UTC)
            self._execution_history.append(context)

            return result

        finally:
            # Release resources
            await self.resource_manager.release_resources(pipeline_name)
            self._active_executions.pop(pipeline_name, None)

    async def _execute_pipeline_async(
        self, context: ExecutionContext
    ) -> dict[str, Any]:
        """Execute pipeline asynchronously with full error handling."""
        logger.info(
            "Starting pipeline execution",
            pipeline=context.pipeline_name,
            run_id=context.run_id,
        )

        # Initialize state
        state = PipelineState(
            pipeline_name=context.pipeline_name,
            status="running",
            start_time=context.start_time,
        )
        context.state = state

        try:
            # Record start
            if self.monitor:
                self.monitor.record_pipeline_start(context.pipeline_name)

            # Load previous state if resuming
            if context.runtime_config.state:
                logger.info(
                    "Resuming from previous state", pipeline=context.pipeline_name
                )

            # Execute with retry logic
            max_retries = self.config.retry_policy.max_retries
            retry_delay = self.config.retry_policy.initial_delay

            for attempt in range(max_retries + 1):
                try:
                    result = await self._run_pipeline_process(context)

                    # Validate data quality if enabled
                    if self.data_validator and result.get("records"):
                        validation_results = self.data_validator.validate_records(
                            context.pipeline_name, result["records"]
                        )

                        if validation_results["invalid_records"] > 0:
                            logger.warning(
                                "Data quality issues detected",
                                pipeline=context.pipeline_name,
                                invalid_records=validation_results["invalid_records"],
                            )

                            if self.alerts:
                                await self.alerts.send_alert(
                                    "data_quality",
                                    f"Pipeline {context.pipeline_name} has {validation_results['invalid_records']} invalid records",
                                )

                    # Success
                    state.status = "completed"
                    state.end_time = datetime.now(UTC)
                    state.records_extracted = result.get("records_extracted", 0)
                    state.records_loaded = result.get("records_loaded", 0)

                    # Save final state
                    self.state_manager.save_state(
                        context.pipeline_name, result.get("state", {})
                    )

                    # Clear checkpoints on success
                    self.state_manager.clear_checkpoints(context.pipeline_name)

                    # Record success
                    if self.monitor:
                        duration = (state.end_time - state.start_time).total_seconds()
                        self.monitor.record_pipeline_success(
                            context.pipeline_name,
                            duration,
                            state.records_extracted,
                            state.records_loaded,
                        )

                    logger.info(
                        "Pipeline completed successfully",
                        pipeline=context.pipeline_name,
                        duration=duration,
                        records_extracted=state.records_extracted,
                        records_loaded=state.records_loaded,
                    )

                    return {
                        "status": "success",
                        "pipeline": context.pipeline_name,
                        "run_id": context.run_id,
                        "duration": duration,
                        "records_extracted": state.records_extracted,
                        "records_loaded": state.records_loaded,
                        "state": result.get("state"),
                    }

                except Exception as e:
                    state.retry_count = attempt + 1
                    state.errors.append(str(e))

                    if attempt < max_retries:
                        logger.warning(
                            f"Pipeline failed, retrying in {retry_delay}s",
                            pipeline=context.pipeline_name,
                            attempt=attempt + 1,
                            error=str(e),
                        )

                        # Save checkpoint for retry
                        self.state_manager.save_checkpoint(
                            context.pipeline_name,
                            f"retry_{attempt}",
                            {
                                "error": str(e),
                                "state": context.runtime_config.state,
                                "timestamp": datetime.now(UTC).isoformat(),
                            },
                        )

                        await asyncio.sleep(retry_delay)
                        retry_delay *= self.config.retry_policy.backoff_factor
                    else:
                        raise

        except Exception as e:
            # Pipeline failed
            state.status = "failed"
            state.end_time = datetime.now(UTC)
            state.errors.append(str(e))

            # Record failure
            if self.monitor:
                self.monitor.record_pipeline_failure(context.pipeline_name, str(e))

            # Send alert
            if self.alerts:
                await self.alerts.send_alert(
                    "pipeline_failure",
                    f"Pipeline {context.pipeline_name} failed: {e!s}",
                )

            logger.error(
                "Pipeline failed",
                pipeline=context.pipeline_name,
                error=str(e),
                retry_count=state.retry_count,
            )

            return {
                "status": "error",
                "pipeline": context.pipeline_name,
                "run_id": context.run_id,
                "error": str(e),
                "errors": state.errors,
                "retry_count": state.retry_count,
            }

    async def _run_pipeline_process(self, context: ExecutionContext) -> dict[str, Any]:
        """Run the actual pipeline process."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write config files
            tap_config_file = tmpdir_path / "tap_config.json"
            tap_config_file.write_text(json.dumps(context.runtime_config.tap_config))

            target_config_file = tmpdir_path / "target_config.json"
            target_config_file.write_text(
                json.dumps(context.runtime_config.target_config)
            )

            # Write state if provided
            state_file = None
            if context.runtime_config.state:
                state_file = tmpdir_path / "state.json"
                state_file.write_text(json.dumps(context.runtime_config.state))

            # Write catalog if provided
            catalog_file = None
            if context.runtime_config.catalog:
                catalog_file = tmpdir_path / "catalog.json"
                catalog_file.write_text(json.dumps(context.runtime_config.catalog))

            # Build commands
            tap_cmd = ["tap-oracle-wms", "--config", str(tap_config_file)]
            if state_file:
                tap_cmd.extend(["--state", str(state_file)])
            if catalog_file:
                tap_cmd.extend(["--catalog", str(catalog_file)])

            target_cmd = ["target-oracle-wms", "--config", str(target_config_file)]

            # Add monitoring flags if enabled
            if self.config.monitoring.enabled:
                tap_cmd.append("--metrics")
                target_cmd.append("--metrics")

            # Execute pipeline asynchronously
            tap_proc = await asyncio.create_subprocess_exec(
                *tap_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            target_proc = await asyncio.create_subprocess_exec(
                *target_cmd,
                stdin=tap_proc.stdout,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Monitor execution
            start_time = time.time()

            # Read outputs concurrently
            tap_stderr_task = asyncio.create_task(tap_proc.stderr.read())
            target_stdout_task = asyncio.create_task(target_proc.stdout.read())
            target_stderr_task = asyncio.create_task(target_proc.stderr.read())

            # Wait for processes
            tap_returncode = await tap_proc.wait()
            target_returncode = await target_proc.wait()

            # Get outputs
            tap_stderr = (await tap_stderr_task).decode()
            target_stdout = (await target_stdout_task).decode()
            target_stderr = (await target_stderr_task).decode()

            # Check for errors
            if tap_returncode != 0:
                msg = f"Tap failed: {tap_stderr}"
                raise RuntimeError(msg)

            if target_returncode != 0:
                msg = f"Target failed: {target_stderr}"
                raise RuntimeError(msg)

            # Parse results
            result = self._parse_execution_results(target_stdout)

            # Add execution metrics
            result["execution_time"] = time.time() - start_time

            # Collect metrics if available
            if self.metrics:
                metrics_file = tmpdir_path / "metrics.json"
                if metrics_file.exists():
                    result["metrics"] = json.loads(metrics_file.read_text())

            return result

    def _parse_execution_results(self, output: str) -> dict[str, Any]:
        """Parse execution results from output."""
        result = {
            "records_extracted": 0,
            "records_loaded": 0,
            "state": None,
            "records": [],
        }

        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                msg = json.loads(line)

                if msg.get("type") == "STATE":
                    result["state"] = msg.get("value", {})
                elif msg.get("type") == "RECORD":
                    result["records_extracted"] += 1
                    result["records_loaded"] += 1
                    # Optionally collect records for validation
                    if self.data_validator:
                        result["records"].append(msg.get("record", {}))
                elif msg.get("type") == "METRIC":
                    # Handle metric messages
                    if "metrics" not in result:
                        result["metrics"] = {}
                    result["metrics"].update(msg.get("value", {}))

            except json.JSONDecodeError:
                # Not a Singer message
                pass

        return result

    async def _schedule_runner(self) -> None:
        """Run scheduled pipelines."""
        logger.info("Starting pipeline scheduler")

        while True:
            try:
                now = datetime.now(UTC)

                for pipeline in self.config.pipelines:
                    if not pipeline.schedule or not pipeline.enabled:
                        continue

                    # Check if it's time to run
                    cron = croniter.croniter(pipeline.schedule, now)
                    next_run = cron.get_next(datetime)

                    # Check last run time
                    last_run = self._get_last_run_time(pipeline.name)

                    if last_run is None or next_run <= now:
                        logger.info(
                            f"Scheduled pipeline {pipeline.name} triggered",
                            schedule=pipeline.schedule,
                        )

                        # Run pipeline
                        asyncio.create_task(self.run_pipeline(pipeline.name))

                # Sleep until next minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    def _get_last_run_time(self, pipeline_name: str) -> datetime | None:
        """Get last run time for a pipeline."""
        for execution in reversed(self._execution_history):
            if execution.pipeline_name == pipeline_name and execution.end_time:
                return execution.end_time
        return None

    def _get_pipeline(self, pipeline_name: str) -> PipelineDefinition | None:
        """Get pipeline definition by name."""
        for pipeline in self.config.pipelines:
            if pipeline.name == pipeline_name:
                return pipeline
        return None

    def _create_runtime_config(
        self, pipeline: PipelineDefinition, checkpoint: str | None = None
    ) -> RuntimeConfig:
        """Create runtime configuration."""
        # Load base configs
        tap_config = json.loads(self.config.tap_config_path.read_text())
        target_config = json.loads(self.config.target_config_path.read_text())

        # Apply overrides
        if pipeline.tap_config_override:
            tap_config.update(pipeline.tap_config_override)
        if pipeline.target_config_override:
            target_config.update(pipeline.target_config_override)

        # Load state
        state = None
        if checkpoint:
            # Load from checkpoint
            state = self.state_manager.load_checkpoint(pipeline.name, checkpoint)
        else:
            # Load regular state
            state = self.state_manager.load_state(pipeline.name)

        # Load and filter catalog
        catalog = None
        if self.config.catalog_path and self.config.catalog_path.exists():
            catalog = json.loads(self.config.catalog_path.read_text())
            if pipeline.streams:
                catalog = self._filter_catalog_streams(catalog, pipeline.streams)

        return RuntimeConfig(
            pipeline_name=pipeline.name,
            tap_config=tap_config,
            target_config=target_config,
            state=state,
            catalog=catalog,
        )

    def _filter_catalog_streams(
        self, catalog: dict[str, Any], streams: list[str]
    ) -> dict[str, Any]:
        """Filter catalog to include only specified streams."""
        filtered = catalog.copy()
        filtered["streams"] = [
            stream
            for stream in catalog.get("streams", [])
            if stream.get("stream") in streams or stream.get("tap_stream_id") in streams
        ]
        return filtered

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        return {
            "active_pipelines": list(self._active_executions.keys()),
            "execution_history": [
                {
                    "pipeline": ex.pipeline_name,
                    "run_id": ex.run_id,
                    "start_time": ex.start_time.isoformat(),
                    "end_time": ex.end_time.isoformat() if ex.end_time else None,
                    "status": ex.state.status if ex.state else "unknown",
                }
                for ex in self._execution_history[-10:]  # Last 10 executions
            ],
            "resource_usage": self.resource_manager.get_resource_usage(),
            "monitoring": {
                "enabled": self.monitor is not None,
                "metrics": self.metrics.get_summary() if self.metrics else None,
            },
        }

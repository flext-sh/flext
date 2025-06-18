"""Pipeline orchestrator for FLX Oracle WMS."""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from flx_oracle_wms.config import PipelineConfig, PipelineDefinition, RuntimeConfig
from flx_oracle_wms.monitoring import PipelineMonitor

logger = structlog.get_logger()


class WMSOrchestrator:
    """Orchestrates tap and target execution for WMS pipelines."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize orchestrator."""
        self.config = config
        self.monitor = PipelineMonitor() if config.monitoring.enabled else None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup structured logging."""
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def run_pipeline(self, pipeline_name: str | None = None) -> dict[str, Any]:
        """Run a pipeline synchronously."""
        pipeline = self._get_pipeline(pipeline_name)
        if not pipeline:
            return {
                "status": "error",
                "error": f"Pipeline '{pipeline_name}' not found",
            }

        if not pipeline.enabled:
            return {"status": "skipped", "reason": "Pipeline is disabled"}

        runtime_config = self._create_runtime_config(pipeline)

        logger.info("Starting pipeline", pipeline=pipeline.name)
        start_time = datetime.now(UTC)

        try:
            # Record pipeline start
            if self.monitor:
                self.monitor.record_pipeline_start(pipeline.name)

            # Execute pipeline
            result = self._execute_pipeline(runtime_config)

            # Record success
            if self.monitor:
                duration = (datetime.now(UTC) - start_time).total_seconds()
                self.monitor.record_pipeline_success(
                    pipeline.name,
                    duration,
                    result.get("records_extracted", 0),
                    result.get("records_loaded", 0),
                )

            logger.info("Pipeline completed", pipeline=pipeline.name, result=result)
            return {
                "status": "success",
                "pipeline": pipeline.name,
                **result,
            }

        except Exception as e:
            # Record failure
            if self.monitor:
                self.monitor.record_pipeline_failure(pipeline.name, str(e))

            logger.error("Pipeline failed", pipeline=pipeline.name, error=str(e))
            return {
                "status": "error",
                "pipeline": pipeline.name,
                "error": str(e),
            }

    async def run_pipeline_async(
        self, pipeline_name: str | None = None
    ) -> dict[str, Any]:
        """Run a pipeline asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_pipeline, pipeline_name)

    def run_all_pipelines(self) -> list[dict[str, Any]]:
        """Run all enabled pipelines."""
        results = []

        for pipeline in self.config.pipelines:
            if pipeline.enabled:
                result = self.run_pipeline(pipeline.name)
                results.append(result)

        return results

    async def run_all_pipelines_async(self) -> list[dict[str, Any]]:
        """Run all enabled pipelines asynchronously with parallelism control."""
        semaphore = asyncio.Semaphore(self.config.max_parallel_pipelines)

        async def run_with_semaphore(pipeline_name: str) -> dict[str, Any]:
            async with semaphore:
                return await self.run_pipeline_async(pipeline_name)

        tasks = [
            run_with_semaphore(pipeline.name)
            for pipeline in self.config.pipelines
            if pipeline.enabled
        ]

        return await asyncio.gather(*tasks)

    def _get_pipeline(self, pipeline_name: str | None) -> PipelineDefinition | None:
        """Get pipeline definition by name."""
        if not pipeline_name and len(self.config.pipelines) == 1:
            return self.config.pipelines[0]

        for pipeline in self.config.pipelines:
            if pipeline.name == pipeline_name:
                return pipeline

        return None

    def _create_runtime_config(self, pipeline: PipelineDefinition) -> RuntimeConfig:
        """Create runtime configuration for pipeline."""
        # Load base configurations
        tap_config = json.loads(self.config.tap_config_path.read_text())
        target_config = json.loads(self.config.target_config_path.read_text())

        # Apply overrides
        if pipeline.tap_config_override:
            tap_config.update(pipeline.tap_config_override)
        if pipeline.target_config_override:
            target_config.update(pipeline.target_config_override)

        # Load state if exists
        state = None
        if self.config.state_path and self.config.state_path.exists():
            state = json.loads(self.config.state_path.read_text())

        # Load catalog and filter streams
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
        filtered_catalog = catalog.copy()
        filtered_catalog["streams"] = [
            stream
            for stream in catalog.get("streams", [])
            if stream.get("stream") in streams or stream.get("tap_stream_id") in streams
        ]
        return filtered_catalog

    def _execute_pipeline(self, config: RuntimeConfig) -> dict[str, Any]:
        """Execute the pipeline using tap and target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write temporary config files
            tap_config_file = tmpdir_path / "tap_config.json"
            tap_config_file.write_text(json.dumps(config.tap_config))

            target_config_file = tmpdir_path / "target_config.json"
            target_config_file.write_text(json.dumps(config.target_config))

            # Write state if provided
            state_file = None
            if config.state:
                state_file = tmpdir_path / "state.json"
                state_file.write_text(json.dumps(config.state))

            # Write catalog if provided
            catalog_file = None
            if config.catalog:
                catalog_file = tmpdir_path / "catalog.json"
                catalog_file.write_text(json.dumps(config.catalog))

            # Build commands
            tap_cmd = ["tap-oracle-wms", "--config", str(tap_config_file)]
            if state_file:
                tap_cmd.extend(["--state", str(state_file)])
            if catalog_file:
                tap_cmd.extend(["--catalog", str(catalog_file)])

            target_cmd = [
                "target-oracle-wms",
                "--config",
                str(target_config_file),
            ]

            # Execute pipeline
            logger.debug("Executing tap command", cmd=tap_cmd)

            # Run tap and pipe to target
            tap_process = subprocess.Popen(
                tap_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            target_process = subprocess.Popen(
                target_cmd,
                stdin=tap_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Allow tap to receive SIGPIPE if target exits
            if tap_process.stdout:
                tap_process.stdout.close()

            # Wait for completion
            tap_stderr = tap_process.stderr.read() if tap_process.stderr else ""
            target_stdout, target_stderr = target_process.communicate()

            tap_process.wait()

            # Check for errors
            if tap_process.returncode != 0:
                msg = f"Tap failed: {tap_stderr}"
                raise RuntimeError(msg)

            if target_process.returncode != 0:
                msg = f"Target failed: {target_stderr}"
                raise RuntimeError(msg)

            # Parse results
            result = self._parse_execution_results(target_stdout)

            # Save new state if present
            if result.get("state") and self.config.state_path:
                self.config.state_path.write_text(json.dumps(result["state"]))

            return result

    def _parse_execution_results(self, output: str) -> dict[str, Any]:
        """Parse execution results from target output."""
        result = {
            "records_extracted": 0,
            "records_loaded": 0,
            "state": None,
        }

        # Parse Singer messages from output
        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                msg = json.loads(line)

                if msg.get("type") == "STATE":
                    result["state"] = msg.get("value", {})
                elif msg.get("type") == "RECORD":
                    result["records_extracted"] = (result["records_extracted"] or 0) + 1
                    result["records_loaded"] = (result["records_loaded"] or 0) + 1

            except json.JSONDecodeError:
                # Not a Singer message, skip
                pass

        return result

    def validate_configuration(self) -> tuple[bool, list[str]]:
        """Validate the configuration."""
        errors = []

        # Check config files exist
        if not self.config.tap_config_path.exists():
            errors.append(f"Tap config not found: {self.config.tap_config_path}")

        if not self.config.target_config_path.exists():
            errors.append(f"Target config not found: {self.config.target_config_path}")

        # Check catalog if specified
        if self.config.catalog_path and not self.config.catalog_path.exists():
            errors.append(f"Catalog not found: {self.config.catalog_path}")

        # Validate pipeline definitions
        pipeline_names = [p.name for p in self.config.pipelines]
        if len(pipeline_names) != len(set(pipeline_names)):
            errors.append("Duplicate pipeline names found")

        # Check tap and target are installed
        try:
            subprocess.run(
                ["tap-oracle-wms", "--version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("tap-oracle-wms is not installed or not in PATH")

        try:
            subprocess.run(
                ["target-oracle-wms", "--version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("target-oracle-wms is not installed or not in PATH")

        return len(errors) == 0, errors

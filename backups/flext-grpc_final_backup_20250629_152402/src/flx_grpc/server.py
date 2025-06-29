"""gRPC server implementation for FLX platform.

Implements the FLX service defined in the protocol buffer definitions,
providing the main API for interacting with the platform.
"""

# gRPC service methods follow protobuf PascalCase convention

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from collections import namedtuple
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, TypeVar

import grpc
import jwt
import meltano
import psutil
import structlog
from flx_core.config.domain_config import get_config, get_domain_constants
from flx_core.domain.business_types import (
    CronExpression,
    ExecutionNumber,
    PluginName,
    Username,
)

# Domain imports
from flx_core.domain.value_objects import (
    Duration,
    ExecutionId,
    ExecutionStatus,
    PipelineId,
    PipelineName,
)
from flx_core.engine.meltano_wrapper import PipelineConfig, PluginFilter
from flx_core.engine.meltano_wrapper import RefreshMode as EngineRefreshMode
from flx_meltano.event_bridge import MeltanoEventBridge

# ZERO TOLERANCE CONSOLIDATION - Use specific imports to avoid circular dependencies
from flx_meltano.job_manager import FlxMeltanoJobManager
from flx_meltano.orchestrator import FlxMeltanoOrchestrator
from flx_meltano.project_manager import FlxMeltanoProjectManager
from flx_meltano.state_manager import FlxMeltanoStateManager
from flx_meltano_enterprise.__version__ import __version__
from google.protobuf import empty_pb2

from flx_grpc.converters import datetime_to_timestamp, dict_to_struct, struct_to_dict
from flx_grpc.models import ExecutionModel, PipelineModel, ScheduleModel
from flx_grpc.proto import flx_pb2, flx_pb2_grpc

# ZERO TOLERANCE: Python 3.13 - Use collections.namedtuple for better performance
MeltanoState = namedtuple(
    "MeltanoState",
    [
        "state_id",
        "state_data",
        "version",
        "updated_at",
        "backend",
    ],
    defaults=[None, None, None],
)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from flx_core.application.application import FlxApplication
    from flx_core.config import Settings
    from flx_core.domain.advanced_types import ConfigurationDict
    from flx_core.engine.meltano_wrapper import MeltanoEngine
    from flx_core.events.event_bus import DomainEvent, HybridEventBus
    from flx_observability.health import HealthChecker
    from flx_observability.metrics import MetricsCollector

    from flx_grpc.types import ServicerContext


logger = structlog.get_logger()


# Generic converter types
T = TypeVar("T", contravariant=True)
P = TypeVar("P", covariant=True)


class EntityToProtobufConverter[T, P]:
    """Protocol for converting entities to protobuf messages."""

    def convert(self, entity: T) -> P:
        """Convert entity to protobuf message."""
        error_msg = (
            f"EntityToProtobufConverter.convert() must be implemented by concrete classes. "
            f"Entity type: {type(entity).__name__}"
        )
        raise TypeError(error_msg)


class PipelineConverter:
    """Pipeline-specific converter for protobuf serialization.

    Converts Pipeline domain entities to protobuf messages for gRPC
    communication, handling data type transformations and field mapping
    between domain models and protocol buffer definitions.

    Features:
        - Pipeline metadata serialization to protobuf format
        - Type-safe field mapping with validation
        - Nested object conversion for complex pipeline configurations
        - Error handling for missing or invalid pipeline data

    """

    @staticmethod
    def from_model(p: PipelineModel) -> flx_pb2.Pipeline:
        """Convert pipeline model to protobuf."""
        pb_pipeline = flx_pb2.Pipeline(
            id=str(p.id),
            name=str(p.name),
            description=p.description,
            extractor=str(p.extractor),
            loader=str(p.loader),
            transform=str(p.transform) if p.transform else None,
            schedule=str(p.schedule) if p.schedule else None,
            is_active=p.is_active,
            created_by=str(p.created_by),
            created_at=datetime_to_timestamp(p.created_at),
            updated_at=datetime_to_timestamp(p.updated_at),
        )

        if p.config:
            pb_pipeline.config.CopyFrom(dict_to_struct(p.config))

        return pb_pipeline


class FlxGrpcServer(flx_pb2_grpc.FlxServiceServicer):
    """gRPC server implementation for FLX service."""

    def __init__(self, app: FlxApplication) -> None:
        """Initialize gRPC server with DI container."""
        self.app = app
        self.logger = logger.bind(component="grpc_server")

        # Resolve dependencies from the application container
        self.event_bus: HybridEventBus = self.app.get_hybrid_event_bus()
        self.meltano_engine: MeltanoEngine = self.app.get_meltano_engine()
        self.health_checker: HealthChecker = self.app.get_health_checker()
        self.metrics: MetricsCollector = self.app.get_metrics_collector()
        self.settings: Settings = self.app.get_settings()

        # In-memory storage with Pydantic models
        self._pipelines: dict[str, PipelineModel] = {}
        self._executions: dict[str, ExecutionModel] = {}
        self._schedules: dict[str, ScheduleModel] = {}

        # Initialize Meltano orchestration components
        self._meltano_project_manager = FlxMeltanoProjectManager(
            project_root=self.settings.meltano.project_root,
        )
        self._meltano_event_bridge = MeltanoEventBridge(
            flx_event_bus=self.event_bus,
        )
        self._meltano_state_manager = FlxMeltanoStateManager(
            event_bus=self.event_bus,
        )
        self._meltano_orchestrator = FlxMeltanoOrchestrator(
            project_manager=self._meltano_project_manager,
            state_manager=self._meltano_state_manager,
            event_bus=self.event_bus,
        )
        self._meltano_job_manager = FlxMeltanoJobManager(
            event_bus=self.event_bus,
        )

    async def GetSystemStats(
        self, _request: empty_pb2.Empty, _context: ServicerContext
    ) -> flx_pb2.SystemStats:
        """Get system statistics for monitoring and dashboard display.

        Retrieves current system performance metrics, pipeline statistics,
        and resource utilization data for enterprise monitoring.

        Returns:
        -------
            SystemStats: System performance and pipeline statistics.

        Note:
        ----
            Provides monitoring patterns with proper metrics collection.

        """
        self.logger.debug("Getting system stats")

        # In a real implementation, this data would come from a dedicated stats service
        # that subscribes to domain events. For now, we calculate it here.
        active_pipelines = len(
            [p for p in self._pipelines.values() if p.is_active],
        )
        total_executions = len(self._executions)
        success_count = len(
            [e for e in self._executions.values() if str(e.status) == "success"],
        )
        success_rate = (
            (
                success_count
                / total_executions
                * get_domain_constants().PERCENTAGE_COMPLETE
            )
            if total_executions > 0
            else 0.0
        )

        # ZERO TOLERANCE - Use domain configuration instead of hardcoded constants
        config = get_config()
        cpu_usage = psutil.cpu_percent(
            interval=config.business.CPU_MONITORING_INTERVAL_SECONDS,
        )
        memory = psutil.virtual_memory()

        return flx_pb2.SystemStats(
            active_pipelines=active_pipelines,
            total_executions=total_executions,
            success_rate=success_rate,
            uptime_seconds=0,  # This should be handled by a monitoring service
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            active_connections=0,  # This should be handled by a monitoring service
        )

    async def HealthCheck(
        self, _request: empty_pb2.Empty, _context: ServicerContext
    ) -> flx_pb2.HealthStatus:
        """Perform comprehensive health check across all system components.

        Executes health checks on database, external services, and system resources
        to determine overall system health status.

        Returns:
        -------
            HealthStatus: Overall system health with component-level details.

        Note:
        ----
            Provides health monitoring with detailed component status.

        """
        self.logger.debug("Performing health check")

        # Run health checks
        checks = await self.health_checker.run_checks()
        overall_status = await self.health_checker.get_overall_status()

        # Convert to protobuf
        components: dict[str, flx_pb2.ComponentHealth] = {}
        # Import HealthStatus dynamically to avoid circular import
        from flx_observability.health import HealthStatus as HealthStatusEnum

        for check in checks:
            components[check.name] = flx_pb2.ComponentHealth(
                name=check.name,
                healthy=check.status == HealthStatusEnum.HEALTHY,
                message=check.message or "",
                metadata={k: str(v) for k, v in (check.metadata or {}).items()},
            )

        return flx_pb2.HealthStatus(
            healthy=overall_status == HealthStatusEnum.HEALTHY,
            components=components,
            timestamp=datetime_to_timestamp(datetime.now(UTC)),
        )

    async def GetSystemInfo(
        self, _request: empty_pb2.Empty, _context: ServicerContext
    ) -> flx_pb2.SystemInfo:
        """Get comprehensive system information and configuration details.

        Retrieves system version, environment configuration, feature flags,
        and platform capabilities for system diagnostics.

        Returns:
        -------
            SystemInfo: Complete system information and feature availability.

        Note:
        ----
            Provides system introspection for debugging and support.

        """
        return flx_pb2.SystemInfo(
            version=__version__,
            environment=self.settings.environment,
            python_version=sys.version,
            meltano_version=meltano.__version__,
            features={
                "multi_tenancy": "true",
                "circuit_breaker": str(self.settings.meltano.circuit_breaker_enabled),
                "rate_limiting": "true",
                "tracing": "true",
            },
        )

    async def ListPipelines(
        self, request: flx_pb2.ListPipelinesRequest, _context: ServicerContext
    ) -> flx_pb2.ListPipelinesResponse:
        """List all pipelines."""
        self.logger.info(
            "Listing pipelines",
            filter=request.filter,
            sort_by=request.sort_by,
        )

        pipelines = list(self._pipelines.values())

        if request.filter:
            pipelines = [
                p for p in pipelines if request.filter.lower() in str(p.name).lower()
            ]

        # Filter by active status if field exists and is set
        is_active_filter = getattr(request, "is_active", None)
        if is_active_filter is not None:
            pipelines = [p for p in pipelines if p.is_active == is_active_filter]

        # Sort pipelines if sorting is requested
        sort_by = getattr(request, "sort_by", None)
        if sort_by:
            sort_direction = getattr(request, "sort_direction", None)
            reverse = sort_direction == getattr(flx_pb2, "DESC", 1)  # Default DESC=1
            pipelines.sort(key=lambda p: str(getattr(p, sort_by, "")), reverse=reverse)

        # Pagination
        start = request.offset
        end = start + request.limit if request.limit > 0 else None
        paginated_pipelines = pipelines[start:end]

        return flx_pb2.ListPipelinesResponse(
            pipelines=[PipelineConverter.from_model(p) for p in paginated_pipelines],
            total=len(pipelines),
            limit=request.limit,
            offset=request.offset,
        )

    async def GetPipeline(
        self, request: flx_pb2.GetPipelineRequest, _context: ServicerContext
    ) -> flx_pb2.Pipeline:
        """Get a single pipeline by ID."""
        self.logger.info("Getting pipeline", pipeline_id=request.id)

        pipeline = self._pipelines.get(request.id)
        if not pipeline:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Pipeline not found")
            return flx_pb2.Pipeline()

        return PipelineConverter.from_model(pipeline)

    async def CreatePipeline(
        self, request: flx_pb2.CreatePipelineRequest, _context: ServicerContext
    ) -> flx_pb2.Pipeline:
        """Create a new pipeline."""
        self.logger.info("Creating pipeline", name=request.name)

        if not request.name:
            _context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            _context.set_details("Pipeline name cannot be empty")
            return flx_pb2.Pipeline()

        pipeline_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        pipeline = PipelineModel(
            id=PipelineId(value=pipeline_id),
            name=PipelineName(value=request.name),
            description=request.description,
            extractor=PluginName(value=request.extractor),
            loader=PluginName(value=request.loader),
            transform=(
                PluginName(value=request.transform) if request.transform else None
            ),
            schedule=(
                CronExpression(value=request.schedule) if request.schedule else None
            ),
            is_active=getattr(request, "is_active", True),
            created_at=now,
            updated_at=now,
            config=struct_to_dict(request.config),
        )

        self._pipelines[pipeline_id] = pipeline

        # Publish domain event
        await self.event_bus.publish(
            "pipeline.created",
            {
                "pipeline_id": pipeline.id,
                "name": pipeline.name,
                "user": self._get_user_from_context(_context),
            },
        )

        self.logger.info("Pipeline created", pipeline_id=pipeline.id)
        return PipelineConverter.from_model(pipeline)

    async def UpdatePipeline(
        self, request: flx_pb2.UpdatePipelineRequest, _context: ServicerContext
    ) -> flx_pb2.Pipeline:
        """Update an existing pipeline."""
        self.logger.info("Updating pipeline", pipeline_id=request.id)

        pipeline = self._pipelines.get(request.id)
        if not pipeline:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Pipeline not found")
            return flx_pb2.Pipeline()

        # Create a dictionary of updates
        update_data = {
            "name": request.name,
            "description": request.description,
            "extractor": request.extractor,
            "loader": request.loader,
            "transform": request.transform,
            "schedule": request.schedule,
            "is_active": request.is_active,
            "config": struct_to_dict(request.config),
        }

        # Filter out fields that were not set in the request
        update_fields = {k: v for k, v in update_data.items() if request.HasField(k)}

        if update_fields:
            updated_pipeline = pipeline.model_copy(update=update_fields)
            updated_pipeline.updated_at = datetime.now(UTC)
            self._pipelines[request.id] = updated_pipeline
        else:
            updated_pipeline = pipeline

        # Publish domain event
        await self.event_bus.publish(
            "pipeline.updated",
            {
                "pipeline_id": updated_pipeline.id,
                "changes": list(update_fields.keys()),
                "user": self._get_user_from_context(_context),
            },
        )

        self.logger.info("Pipeline updated", pipeline_id=updated_pipeline.id)
        return PipelineConverter.from_model(updated_pipeline)

    async def DeletePipeline(
        self, request: flx_pb2.DeletePipelineRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Delete a pipeline from the system."""
        self.logger.info("Deleting pipeline", pipeline_id=request.id)

        pipeline = self._pipelines.get(request.id)
        if not pipeline:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Pipeline not found")
            return empty_pb2.Empty()

        # Delete pipeline
        self._pipelines.pop(request.id)

        # Publish domain event
        await self.event_bus.publish(
            "pipeline.deleted",
            {
                "pipeline_id": request.id,
                "name": pipeline.name,
            },
        )

        return empty_pb2.Empty()

    async def RunPipeline(
        self, request: flx_pb2.RunPipelineRequest, _context: ServicerContext
    ) -> flx_pb2.Execution:
        """Run a pipeline by ID."""
        self.logger.info("Running pipeline", pipeline_id=request.pipeline_id)

        pipeline = self._pipelines.get(request.pipeline_id)
        if not pipeline:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Pipeline not found")
            return flx_pb2.Execution()

        if not pipeline.is_active:
            _context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            _context.set_details("Pipeline is not active")
            return flx_pb2.Execution()

        execution_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        from flx_core.domain.value_objects import ExecutionStatus

        execution = ExecutionModel(
            id=ExecutionId(value=execution_id),
            pipeline_id=PipelineId(value=request.pipeline_id),
            execution_number=ExecutionNumber(value=len(self._executions) + 1),
            status=ExecutionStatus(value="running"),
            started_at=now,
            triggered_by=Username(value=self._get_user_from_context(_context)),
        )
        self._executions[execution_id] = execution

        # Run pipeline in background
        env_vars: dict[str, str] = {}
        if request.env_vars:
            env_vars.update(request.env_vars)

        # Convert boolean to enum - use EngineRefreshMode for MeltanoEngine
        refresh_mode = (
            EngineRefreshMode.FULL
            if request.full_refresh
            else EngineRefreshMode.INCREMENTAL
        )

        asyncio.create_task(
            self._run_pipeline_async(
                execution_id=execution_id,
                pipeline=pipeline,
                refresh_mode=refresh_mode,
                env_vars=env_vars,
            ),
        )

        # Publish domain event
        await self.event_bus.publish(
            "pipeline.execution.started",
            {
                "execution_id": execution.id,
                "pipeline_id": execution.pipeline_id,
                "user": execution.triggered_by,
            },
        )

        self.logger.info("Pipeline execution started", execution_id=execution.id)
        return self._convert_execution_to_pb(execution)

    async def _run_pipeline_async(
        self,
        execution_id: str,
        pipeline: PipelineModel,
        refresh_mode: EngineRefreshMode,
        env_vars: dict[str, str],
    ) -> None:
        """Execute the pipeline asynchronously."""
        try:
            # Create PipelineConfig object for the MeltanoEngine call
            pipeline_config = PipelineConfig(
                extractor=str(pipeline.extractor),
                loader=str(pipeline.loader),
                transform=str(pipeline.transform) if pipeline.transform else None,
                refresh_mode=refresh_mode,
                env=env_vars,
            )
            result = await self.meltano_engine.run_pipeline(pipeline_config)

            execution = self._executions.get(execution_id)
            if execution:
                status_value = "success" if result.get("success", False) else "failed"
                execution.status = ExecutionStatus(value=status_value)
                execution.finished_at = datetime.now(UTC)
                if execution.started_at:
                    duration_seconds = int(
                        (execution.finished_at - execution.started_at).total_seconds(),
                    )
                    execution.duration = Duration(seconds=duration_seconds)
                error_result = result.get("error_message")
                execution.error_message = (
                    str(error_result) if error_result is not None else None
                )

                # Publish domain event
                await self.event_bus.publish(
                    "pipeline.execution.completed",
                    {
                        "execution_id": execution.id,
                        "pipeline_id": execution.pipeline_id,
                        "status": execution.status,
                        "duration": (
                            execution.duration.seconds if execution.duration else 0
                        ),
                    },
                )
        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception(
                "Pipeline execution failed",
                execution_id=execution_id,
                error=e,
            )
            execution = self._executions.get(execution_id)
            if execution:
                execution.status = ExecutionStatus(value="failed")
                execution.finished_at = datetime.now(UTC)
                if execution.started_at:
                    raw_duration = (
                        execution.finished_at - execution.started_at
                    ).total_seconds()
                    execution.duration = Duration(seconds=int(raw_duration))
                execution.error_message = str(e)

                await self.event_bus.publish(
                    "pipeline.execution.completed",
                    {
                        "execution_id": execution.id,
                        "pipeline_id": execution.pipeline_id,
                        "status": "failed",
                        "error": str(e),
                    },
                )

    async def GetExecution(
        self, request: flx_pb2.GetExecutionRequest, _context: ServicerContext
    ) -> flx_pb2.Execution:
        """Get a single execution by ID."""
        self.logger.info("Getting execution", execution_id=request.id)

        execution = self._executions.get(request.id)
        if not execution:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Execution not found")
            return flx_pb2.Execution()

        return self._convert_execution_to_pb(execution)

    def _convert_execution_to_pb(self, e: ExecutionModel) -> flx_pb2.Execution:
        """Convert execution model to protobuf."""
        status_map = {
            "running": flx_pb2.STATUS_RUNNING,
            "success": flx_pb2.STATUS_SUCCESS,
            "failed": flx_pb2.STATUS_FAILED,
        }

        execution = flx_pb2.Execution(
            id=str(e.id),
            pipeline_id=str(e.pipeline_id),
            status=status_map.get(str(e.status), flx_pb2.STATUS_UNSPECIFIED),
            started_at=datetime_to_timestamp(e.started_at),
            triggered_by=str(e.triggered_by) if e.triggered_by else "",
            metadata=e.metadata,
        )

        if e.finished_at:
            execution.finished_at.CopyFrom(datetime_to_timestamp(e.finished_at))

        if e.duration is not None:
            execution.duration_seconds = e.duration.seconds

        if e.error_message:
            execution.error_message = e.error_message

        if e.records_processed is not None:
            execution.records_processed = int(e.records_processed)

        return execution

    async def ListExecutions(
        self, request: flx_pb2.ListExecutionsRequest, _context: ServicerContext
    ) -> flx_pb2.ListExecutionsResponse:
        """List pipeline executions with filtering and pagination."""
        self.logger.info("Listing executions", pipeline_id=request.pipeline_id)

        executions = list(self._executions.values())

        if request.pipeline_id:
            executions = [
                e for e in executions if str(e.pipeline_id) == request.pipeline_id
            ]

        # Additional filtering can be implemented as needed

        # Sort by started_at descending
        executions.sort(key=lambda e: getattr(e, "started_at", 0), reverse=True)

        # Paginate
        total = len(executions)
        start = request.offset
        end = start + request.limit if request.limit > 0 else None
        paginated_executions = executions[start:end]

        # Convert to protobuf
        pb_executions = [self._convert_execution_to_pb(e) for e in paginated_executions]

        return flx_pb2.ListExecutionsResponse(
            executions=pb_executions,
            total=total,
            limit=request.limit,
            offset=request.offset,
        )

    async def CancelExecution(
        self, request: flx_pb2.CancelExecutionRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Cancel a running execution."""
        self.logger.info("Canceling execution", execution_id=request.id)

        execution = self._executions.get(request.id)
        if not execution:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details("Execution not found")
            return empty_pb2.Empty()

        if str(execution.status) != "running":
            _context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            _context.set_details("Execution is not running")
            return empty_pb2.Empty()

        # In a real system, this would send a signal to the running process
        # For this demo, we just update the status
        execution.status = ExecutionStatus(value="failed")
        execution.error_message = "Canceled by user"
        execution.finished_at = datetime.now(UTC)

        await self.event_bus.publish(
            "pipeline.execution.completed",
            {
                "execution_id": execution.id,
                "pipeline_id": execution.pipeline_id,
                "status": execution.status,
                "error": execution.error_message,
            },
        )

        return empty_pb2.Empty()

    async def StreamExecution(
        self, request: flx_pb2.StreamExecutionRequest, _context: ServicerContext
    ) -> AsyncGenerator[flx_pb2.ExecutionUpdate]:
        """Stream real-time execution updates for monitoring."""
        if request.execution_id not in self._executions:
            _context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Execution {request.execution_id} not found",
            )

        # Subscribe to execution events
        execution_complete = asyncio.Event()
        updates_queue: asyncio.Queue[flx_pb2.ExecutionUpdate] = asyncio.Queue()

        async def handle_event(event: DomainEvent) -> None:
            """Handle and process execution events for streaming."""
            event_data = event.get_event_data()
            if event_data.get("execution_id") == request.execution_id:
                update = flx_pb2.ExecutionUpdate(
                    execution_id=request.execution_id,
                    type=event.event_type,
                    message=json.dumps(event_data),
                    timestamp=datetime_to_timestamp(event.occurred_at),
                )

                await updates_queue.put(update)

                if event.event_type == "pipeline.execution.completed":
                    execution_complete.set()

        # Subscribe to events - fix type annotations for async handlers
        self.event_bus.subscribe("pipeline.output", handle_event)  # type: ignore[arg-type]
        self.event_bus.subscribe("pipeline.execution.completed", handle_event)  # type: ignore[arg-type]

        try:
            # Stream updates
            while not execution_complete.is_set():
                try:
                    # Use domain configuration for streaming timeout - with strict validation
                    get_config = __import__(
                        "flx_core.config.domain_config",
                        fromlist=["get_config"],
                    ).get_config
                    config = get_config()
                    update = await asyncio.wait_for(
                        updates_queue.get(),
                        timeout=config.monitoring.heartbeat_interval_seconds
                        / config.business.HEARTBEAT_TIMEOUT_DIVISOR,  # ZERO TOLERANCE: Use domain config
                    )
                    yield update
                except TimeoutError:
                    # Send heartbeat
                    yield flx_pb2.ExecutionUpdate(
                        execution_id=request.execution_id,
                        type="heartbeat",
                        message="",
                        timestamp=datetime_to_timestamp(datetime.now(UTC)),
                    )
        finally:
            # Unsubscribe - fix type annotations for async handlers
            self.event_bus.unsubscribe("pipeline.output", handle_event)  # type: ignore[arg-type]
            self.event_bus.unsubscribe("pipeline.execution.completed", handle_event)  # type: ignore[arg-type]

    async def ListPlugins(
        self, request: flx_pb2.ListPluginsRequest, _context: ServicerContext
    ) -> flx_pb2.ListPluginsResponse:
        """List available Meltano plugins for pipeline configuration."""
        plugin_type = None
        if request.type != flx_pb2.PLUGIN_TYPE_UNSPECIFIED:
            type_map = {
                flx_pb2.PLUGIN_TYPE_EXTRACTOR: "extractors",
                flx_pb2.PLUGIN_TYPE_LOADER: "loaders",
                flx_pb2.PLUGIN_TYPE_TRANSFORMER: "transformers",
                flx_pb2.PLUGIN_TYPE_ORCHESTRATOR: "orchestrators",
                flx_pb2.PLUGIN_TYPE_UTILITY: "utilities",
            }
        plugin_type = type_map.get(request.type)

        # Convert installed_only to PluginFilter
        plugin_filter = (
            PluginFilter.INSTALLED_ONLY
            if request.installed_only
            else PluginFilter.ALL_PLUGINS
        )

        # Get plugins from Meltano
        plugins = await self.meltano_engine.list_plugins(
            plugin_type=plugin_type,
            plugin_filter=plugin_filter,
        )

        # Convert to protobuf with proper type conversion
        pb_plugins: list[flx_pb2.Plugin] = []
        for plugin_data in plugins:
            # Extract and convert values with proper type handling
            name_value = plugin_data.get("name", "")
            type_value = plugin_data.get("type", "")
            variant_value = plugin_data.get("variant", "")
            version_value = plugin_data.get("version", "")
            description_value = plugin_data.get("description", "")
            installed_value = plugin_data.get("installed", False)
            config_raw: object = plugin_data.get("config", {})
            (config_raw if isinstance(config_raw, dict) else {})

            pb_plugin = flx_pb2.Plugin(
                name=str(name_value) if name_value is not None else "",
                type=flx_pb2.PluginType(
                    self._map_plugin_type_to_protobuf(
                        str(type_value) if type_value is not None else "",
                    ),
                ),
                variant=str(variant_value) if variant_value is not None else "",
                version=str(version_value) if version_value is not None else "",
                description=(
                    str(description_value) if description_value is not None else ""
                ),
                installed=(
                    bool(installed_value) if installed_value is not None else False
                ),
            )

            # Skip config - Plugin protobuf doesn't have config field

            # Add settings if available
            settings_raw = plugin_data.get("settings", {})
            settings_value: dict[str, object] = (
                settings_raw if isinstance(settings_raw, dict) else {}
            )
            if isinstance(settings_value, dict) and settings_value:
                pb_plugin.settings.CopyFrom(dict_to_struct(settings_value))

            pb_plugins.append(pb_plugin)

        return flx_pb2.ListPluginsResponse(
            plugins=pb_plugins,
            total=len(pb_plugins),
        )

    async def InstallPlugin(
        self, request: flx_pb2.InstallPluginRequest, _context: ServicerContext
    ) -> flx_pb2.Plugin:
        """Install a Meltano plugin for pipeline use."""
        type_map = {
            flx_pb2.PLUGIN_TYPE_EXTRACTOR: "extractors",
            flx_pb2.PLUGIN_TYPE_LOADER: "loaders",
            flx_pb2.PLUGIN_TYPE_TRANSFORMER: "transformers",
            flx_pb2.PLUGIN_TYPE_ORCHESTRATOR: "orchestrators",
            flx_pb2.PLUGIN_TYPE_UTILITY: "utilities",
        }

        plugin_type = type_map.get(request.type, "extractors")

        # Install with Meltano
        success = await self.meltano_engine.add_plugin(
            plugin_type=plugin_type,
            plugin_name=str(request.name),
            variant=request.variant or None,
        )

        if not success:
            _context.abort(grpc.StatusCode.INTERNAL, "Failed to install plugin")

        # Return plugin info
        return flx_pb2.Plugin(
            name=request.name,
            type=request.type,
            variant=request.variant,
            installed=True,
        )

    async def UninstallPlugin(
        self, request: flx_pb2.UninstallPluginRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Uninstall a Meltano plugin from the system."""
        type_map = {
            flx_pb2.PLUGIN_TYPE_EXTRACTOR: "extractors",
            flx_pb2.PLUGIN_TYPE_LOADER: "loaders",
            flx_pb2.PLUGIN_TYPE_TRANSFORMER: "transformers",
            flx_pb2.PLUGIN_TYPE_ORCHESTRATOR: "orchestrators",
            flx_pb2.PLUGIN_TYPE_UTILITY: "utilities",
        }

        plugin_type = type_map.get(request.type, "extractors")

        # Remove with Meltano
        success = await self.meltano_engine.remove_plugin(
            plugin_type=plugin_type,
            plugin_name=str(request.name),
        )

        if not success:
            _context.abort(grpc.StatusCode.INTERNAL, "Failed to uninstall plugin")

        return empty_pb2.Empty()

    async def GetState(
        self, request: flx_pb2.GetStateRequest, _context: ServicerContext
    ) -> flx_pb2.State:
        """Retrieve pipeline execution state for incremental processing."""
        state_data = await self.meltano_engine.get_state(request.id)

        return flx_pb2.State(
            id=request.id,
            data=dict_to_struct(dict(state_data)),
            updated_at=datetime_to_timestamp(datetime.now(UTC)),
        )

    async def SetState(
        self, request: flx_pb2.SetStateRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Update pipeline execution state for incremental processing."""
        raw_state_data = struct_to_dict(request.data)
        # Convert to ConfigurationDict type expected by MeltanoEngine
        state_data: ConfigurationDict = {
            k: v
            for k, v in raw_state_data.items()
            if isinstance(v, str | int | bool | float | list) or v is None
        }

        success = await self.meltano_engine.set_state(request.id, state_data)

        if not success:
            _context.abort(grpc.StatusCode.INTERNAL, "Failed to set state")

        return empty_pb2.Empty()

    async def ClearState(
        self, request: flx_pb2.ClearStateRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Clear pipeline execution state for fresh processing."""
        success = await self.meltano_engine.clear_state(request.id)

        if not success:
            _context.abort(grpc.StatusCode.INTERNAL, "Failed to clear state")

        return empty_pb2.Empty()

    # === MELTANO ORCHESTRATION METHODS ===

    async def InitializeMeltanoProject(
        self,
        request: flx_pb2.InitializeMeltanoProjectRequest,
        _context: ServicerContext,
    ) -> flx_pb2.MeltanoProject:
        """Initialize a new Meltano project."""
        self.logger.info(
            "Initializing Meltano project",
            project_name=request.project_name,
            environment=request.environment,
        )

        try:
            # Use MeltanoEngine to initialize project
            await self.meltano_engine.initialize()

            # Create project info
            project_info = {
                "name": request.project_name,
                "environment": request.environment,
                "root": str(self.meltano_engine.project_root),
                "active_environment": {"name": request.environment},
            }

            return flx_pb2.MeltanoProject(
                name=str(project_info["name"]),
                environment=str(project_info["environment"]),
                project_root=str(project_info["root"]),
                is_initialized=True,
                created_at=datetime_to_timestamp(datetime.now(UTC)),
                updated_at=datetime_to_timestamp(datetime.now(UTC)),
            )
        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to initialize Meltano project", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to initialize project: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoProject()

    async def LoadMeltanoProject(
        self, request: flx_pb2.LoadMeltanoProjectRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoProject:
        """Load an existing Meltano project."""
        self.logger.info(
            "Loading Meltano project",
            project_name=request.project_name,
            environment=request.environment,
        )

        try:
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
                environment=request.environment,
            )

            # Extract project attributes with pythonic access patterns
            project_name = getattr(project, "name", request.project_name)

            try:
                environment_name = project.environment.name
            except AttributeError:
                environment_name = (
                    request.environment
                )  # Fallback if no environment or no name

            project_root = str(getattr(project, "root", project.root))

            return flx_pb2.MeltanoProject(
                name=project_name,
                environment=environment_name,
                project_root=project_root,
                is_initialized=True,
                created_at=datetime_to_timestamp(datetime.now(UTC)),
                updated_at=datetime_to_timestamp(datetime.now(UTC)),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to load Meltano project", error=str(e))
            _context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Failed to load project: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoProject()

    async def RunMeltanoPipeline(
        self, request: flx_pb2.RunMeltanoPipelineRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoExecution:
        """Execute a Meltano pipeline with enterprise orchestration."""
        self.logger.info(
            "Running Meltano pipeline",
            project_name=request.project_name,
            environment=request.environment,
        )

        try:
            # Convert execution mode
            execution_mode_map = {
                flx_pb2.MELTANO_EXECUTION_MODE_SYNC: "sync",
                flx_pb2.MELTANO_EXECUTION_MODE_ASYNC: "async",
            }
            execution_mode = execution_mode_map.get(request.execution_mode, "async")

            # Convert pipeline definition
            pipeline_definition = struct_to_dict(request.pipeline_definition)

            # Import OrchestrationMode
            from flx_meltano.orchestrator import OrchestrationMode

            # Convert execution mode to enum
            orchestration_mode = (
                OrchestrationMode.SYNC
                if execution_mode == "sync"
                else OrchestrationMode.ASYNC
            )

            result = await self._meltano_orchestrator.run_pipeline(
                project_name=request.project_name,
                pipeline_definition=pipeline_definition,
                environment=request.environment,
                execution_mode=orchestration_mode,
            )

            # Convert state
            state_map = {
                "success": flx_pb2.MELTANO_JOB_STATE_SUCCESS,
                "failure": flx_pb2.MELTANO_JOB_STATE_FAIL,
                "running": flx_pb2.MELTANO_JOB_STATE_RUNNING,
                "idle": flx_pb2.MELTANO_JOB_STATE_IDLE,
            }

            return flx_pb2.MeltanoExecution(
                execution_id=result["execution_id"],
                project_name=request.project_name,
                pipeline_name=result.get("pipeline_name", ""),
                state=state_map.get(
                    result["state"],
                    flx_pb2.MELTANO_JOB_STATE_UNSPECIFIED,
                ),
                started_at=datetime_to_timestamp(result["started_at"]),
                environment=request.environment,
                result_data=dict_to_struct(result.get("result_data", {})),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to run Meltano pipeline", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to run pipeline: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoExecution()

    async def GetMeltanoJobStatus(
        self, request: flx_pb2.GetMeltanoJobStatusRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoJobStatus:
        """Retrieve status information for a Meltano job."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            job = await self._meltano_job_manager.get_job(
                project=project,
                job_id=request.job_id,
            )

            if not job:
                _context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Job {request.job_id} not found",
                )

            # Convert state
            state_map = {
                "SUCCESS": flx_pb2.MELTANO_JOB_STATE_SUCCESS,
                "FAIL": flx_pb2.MELTANO_JOB_STATE_FAIL,
                "RUNNING": flx_pb2.MELTANO_JOB_STATE_RUNNING,
                "IDLE": flx_pb2.MELTANO_JOB_STATE_IDLE,
            }

            return flx_pb2.MeltanoJobStatus(
                job_id=str(getattr(job, "job_id", getattr(job, "id", request.job_id))),
                run_id=str(getattr(job, "run_id", "")),
                state=state_map.get(
                    getattr(getattr(job, "state", None), "value", "UNSPECIFIED"),
                    flx_pb2.MELTANO_JOB_STATE_UNSPECIFIED,
                ),
                started_at=(
                    datetime_to_timestamp(job.started_at)
                    if getattr(job, "started_at", None)
                    else None
                ),
                last_heartbeat_at=(
                    datetime_to_timestamp(job.last_heartbeat_at)
                    if getattr(job, "last_heartbeat_at", None)
                    else None
                ),
                payload=str(getattr(job, "payload", "")),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to get job status", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get job status: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoJobStatus()

    async def ListMeltanoJobs(
        self, request: flx_pb2.ListMeltanoJobsRequest, _context: ServicerContext
    ) -> flx_pb2.ListMeltanoJobsResponse:
        """List Meltano jobs with filtering and pagination."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            # Convert state filter
            from meltano.core.job import State

            state_filter = None
            if request.state != flx_pb2.MELTANO_JOB_STATE_UNSPECIFIED:
                state_map = {
                    flx_pb2.MELTANO_JOB_STATE_SUCCESS: State.SUCCESS,
                    flx_pb2.MELTANO_JOB_STATE_FAIL: State.FAIL,
                    flx_pb2.MELTANO_JOB_STATE_RUNNING: State.RUNNING,
                    flx_pb2.MELTANO_JOB_STATE_IDLE: State.IDLE,
                }
                state_filter = state_map.get(request.state)

            # ZERO TOLERANCE - Use domain config for pagination
            config = get_config()

            jobs = await self._meltano_job_manager.list_jobs(
                project=project,
                state=state_filter,
                run_id=request.run_id or None,
                limit=request.limit or config.business.DEFAULT_PAGINATION_SIZE,
                offset=request.offset or 0,
            )

            # Convert to protobuf
            pb_jobs = []
            for job in jobs:
                pb_job = await self.GetMeltanoJobStatus(
                    flx_pb2.GetMeltanoJobStatusRequest(
                        project_name=request.project_name,
                        job_id=str(getattr(job, "job_id", getattr(job, "id", ""))),
                    ),
                    _context,
                )
                pb_jobs.append(pb_job)

            return flx_pb2.ListMeltanoJobsResponse(
                jobs=pb_jobs,
                total=len(pb_jobs),
                limit=request.limit or config.business.DEFAULT_PAGINATION_SIZE,
                offset=request.offset or 0,
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to list jobs", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to list jobs: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.ListMeltanoJobsResponse()

    async def GetMeltanoState(
        self, request: flx_pb2.GetMeltanoStateRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoState:
        """Retrieve Meltano state for incremental data processing."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            from flx_meltano.state_manager import CachePolicy

            cache_policy = (
                CachePolicy.USE_CACHE
                if request.use_cache
                else CachePolicy.FORCE_REFRESH
            )

            state = await self._meltano_state_manager.get_state(
                project=project,
                state_id=request.state_id,
                cache_policy=cache_policy,
            )

            if not state:
                _context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"State {request.state_id} not found",
                )

            return flx_pb2.MeltanoState(
                state_id=request.state_id,
                state_data=dict_to_struct(getattr(state, "state_data", {})),
                version=str(getattr(state, "version", "")),
                updated_at=(
                    datetime_to_timestamp(state.updated_at)
                    if getattr(state, "updated_at", None)
                    else None
                ),
                backend=str(getattr(state, "backend", "")),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to get state", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get state: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoState()

    async def SetMeltanoState(
        self, request: flx_pb2.SetMeltanoStateRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Update Meltano state for incremental data processing."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            # Convert state data
            from meltano.core.state_store.base import MeltanoState as MeltanoStateBase

            state = MeltanoStateBase(
                state_id=request.state_id,
                partial_state=struct_to_dict(request.state_data),
            )

            from flx_meltano.state_manager import BackupPolicy

            backup_policy = (
                BackupPolicy.CREATE_BACKUP
                if request.create_backup
                else BackupPolicy.SKIP_BACKUP
            )

            await self._meltano_state_manager.set_state(
                project=project,
                state_id=request.state_id,
                state=state,
                backup_policy=backup_policy,
            )

            return empty_pb2.Empty()

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to set state", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to set state: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return empty_pb2.Empty()

    async def GetMeltanoJobStatistics(
        self, request: flx_pb2.GetMeltanoJobStatisticsRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoJobStatistics:
        """Retrieve Meltano job statistics for performance analysis."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            stats = await self._meltano_job_manager.get_job_statistics(
                project=project,
                days=request.days or 7,
            )

            return flx_pb2.MeltanoJobStatistics(
                period_days=stats["period_days"],
                total_jobs=stats["total_jobs"],
                state_counts=stats["state_counts"],
                success_rate=stats["success_rate"],
                generated_at=datetime_to_timestamp(
                    datetime.fromisoformat(stats["generated_at"]),
                ),
                cutoff_date=stats["cutoff_date"],
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to get job statistics", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get job statistics: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoJobStatistics()

    async def CleanupStaleMeltanoJobs(
        self, request: flx_pb2.CleanupStaleMeltanoJobsRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoJobCleanupResult:
        """Clean up stale Meltano jobs for system maintenance."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            # Use domain configuration for monitoring defaults
            get_config = __import__(
                "flx_core.config.domain_config",
                fromlist=["get_config"],
            ).get_config
            config = get_config()

            from flx_meltano.job_manager import JobExecutionMode

            execution_mode = (
                JobExecutionMode.DRY_RUN
                if request.dry_run
                else JobExecutionMode.EXECUTE
            )

            result = await self._meltano_job_manager.cleanup_stale_jobs(
                project=project,
                heartbeat_timeout_minutes=request.heartbeat_timeout_minutes
                or (
                    config.monitoring.heartbeat_interval_seconds
                    // config.business.STANDARD_TIMEOUT_SECONDS
                )
                or config.business.DEFAULT_HEARTBEAT_TIMEOUT_MINUTES,  # ZERO TOLERANCE: Use domain config
                execution_mode=execution_mode,
            )

            return flx_pb2.MeltanoJobCleanupResult(
                dry_run=result["dry_run"],
                stale_jobs_found=result["stale_jobs_found"],
                jobs_cleaned=result["jobs_cleaned"],
                heartbeat_timeout_minutes=result["heartbeat_timeout_minutes"],
                cleaned_at=datetime_to_timestamp(
                    datetime.fromisoformat(result["cleaned_at"]),
                ),
                cleaned_job_ids=result.get("cleaned_jobs", []),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to cleanup stale jobs", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to cleanup stale jobs: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoJobCleanupResult()

    async def RunMeltanoCommand(
        self, request: flx_pb2.RunMeltanoCommandRequest, _context: ServicerContext
    ) -> flx_pb2.MeltanoCommandResult:
        """Execute arbitrary Meltano commands with monitoring."""
        try:
            # Load project
            project = await self._meltano_project_manager.load_project(
                project_name=request.project_name,
            )

            result = await self._meltano_project_manager.run_command(
                project=project,
                command_args=list(request.command_args),
                environment=request.environment or "dev",
                env_vars=dict(request.env_vars),
            )

            return flx_pb2.MeltanoCommandResult(
                return_code=result["return_code"],
                stdout=result["stdout"],
                stderr=result["stderr"],
                duration_seconds=result["duration_seconds"],
                command=result["command"],
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to run Meltano command", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to run command: {e}",
            )
            # Never reached, but helps mypy understand this method returns
            return flx_pb2.MeltanoCommandResult()

    # === SCHEDULE MANAGEMENT METHODS ===

    async def CreateSchedule(
        self, request: flx_pb2.CreateScheduleRequest, _context: ServicerContext
    ) -> flx_pb2.Schedule:
        """Create a new pipeline schedule."""
        self.logger.info("Creating schedule", name=getattr(request, "name", "unnamed"))

        schedule_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        from flx_core.domain.business_types import ScheduleId, Timezone
        from flx_core.domain.value_objects import PipelineId

        schedule = ScheduleModel(
            id=ScheduleId(value=schedule_id),
            pipeline_id=PipelineId(value=getattr(request, "pipeline_id", "")),
            cron_expression=CronExpression(
                value=getattr(request, "cron_expression", "0 0 * * *"),
            ),
            timezone=Timezone(value=getattr(request, "timezone", "UTC")),
            is_active=getattr(request, "is_active", True),
            created_at=now,
            updated_at=now,
        )

        self._schedules[schedule_id] = schedule

        # Publish domain event
        await self.event_bus.publish(
            "schedule.created",
            {
                "schedule_id": schedule.id,
                "pipeline_id": schedule.pipeline_id,
                "cron_expression": str(schedule.cron_expression),
            },
        )

        return self._convert_schedule_to_pb(schedule)

    async def UpdateSchedule(
        self, request: flx_pb2.UpdateScheduleRequest, _context: ServicerContext
    ) -> flx_pb2.Schedule:
        """Update configuration of an existing pipeline schedule."""
        self.logger.info("Updating schedule", schedule_id=request.id)

        schedule = self._schedules.get(request.id)
        if not schedule:
            _context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Schedule {request.id} not found",
            )

        # Create a dictionary of updates with pythonic attribute access
        update_data: dict[str, Any] = {}
        try:
            update_data["cron_expression"] = CronExpression(
                value=request.cron_expression,
            )
        except AttributeError:
            pass  # cron_expression not provided in request

        try:
            # Import Timezone from business types
            from flx_core.domain.business_types import Timezone

            update_data["timezone"] = Timezone(value=request.timezone)
        except AttributeError:
            pass  # timezone not provided in request

        try:
            update_data["is_active"] = bool(request.is_active)
        except AttributeError:
            pass  # is_active not provided in request

        if update_data and schedule:
            updated_schedule = schedule.model_copy(update=update_data)
            self._schedules[request.id] = updated_schedule

            # Publish domain event
            await self.event_bus.publish(
                "schedule.updated",
                {
                    "schedule_id": request.id,
                    "updates": update_data,
                },
            )
        elif schedule:
            updated_schedule = schedule
        else:
            # Schedule not found
            msg = f"Schedule {request.id} not found"
            raise ValueError(msg)

        self.logger.info("Schedule updated", schedule_id=updated_schedule.id)
        return self._convert_schedule_to_pb(updated_schedule)

    async def DeleteSchedule(
        self, request: flx_pb2.DeleteScheduleRequest, _context: ServicerContext
    ) -> empty_pb2.Empty:
        """Delete a pipeline schedule from the system."""
        self.logger.info("Deleting schedule", schedule_id=request.id)

        schedule = self._schedules.get(request.id)
        if not schedule:
            _context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Schedule {request.id} not found",
            )

        # Delete schedule
        self._schedules.pop(request.id)

        # Publish domain event
        await self.event_bus.publish(
            "schedule.deleted",
            {
                "schedule_id": request.id,
            },
        )

        return empty_pb2.Empty()

    async def ListSchedules(
        self, request: flx_pb2.ListSchedulesRequest, _context: ServicerContext
    ) -> flx_pb2.ListSchedulesResponse:
        """List pipeline schedules with filtering and pagination."""
        self.logger.info("Listing schedules", pipeline_id=request.pipeline_id)

        schedules = [
            s
            for s in self._schedules.values()
            if str(s.pipeline_id) == request.pipeline_id
        ]

        # Filter by pipeline_id if provided
        if request.pipeline_id:
            schedules = [
                s for s in schedules if str(s.pipeline_id) == request.pipeline_id
            ]

        # Sort by created_at descending
        schedules.sort(key=lambda s: getattr(s, "created_at", 0), reverse=True)

        # Paginate - handle missing attributes with pythonic approach
        total = len(schedules)
        try:
            start = request.offset
        except AttributeError:
            start = 0  # Default offset

        try:
            limit = request.limit
        except AttributeError:
            # ZERO TOLERANCE - Use domain configuration for pagination
            config = get_config()
            limit = config.business.DEFAULT_PAGINATION_SIZE
        end = start + limit if limit > 0 else None
        paginated_schedules = schedules[start:end]

        return flx_pb2.ListSchedulesResponse(
            schedules=[self._convert_schedule_to_pb(s) for s in paginated_schedules],
            total=total,
        )

    def _convert_schedule_to_pb(self, s: ScheduleModel) -> flx_pb2.Schedule:
        """Convert schedule model to protobuf."""
        return flx_pb2.Schedule(
            id=str(s.id) if s.id else "",
            pipeline_id=str(s.pipeline_id),
            cron=str(s.cron_expression) if s.cron_expression else "",
            is_active=bool(s.is_active),
        )

    # === PLUGIN CONFIGURATION METHODS ===

    async def GetPluginConfig(
        self, request: flx_pb2.GetPluginConfigRequest, _context: ServicerContext
    ) -> flx_pb2.PluginConfig:
        """Retrieve configuration settings for a Meltano plugin."""
        try:
            # Get config from Meltano
            config = await self.meltano_engine.get_config(
                plugin_name=str(request.name),
            )

            # Convert config to proper format for protobuf
            config_dict: dict[str, object] = {}
            if isinstance(config, dict):
                for key, value in config.items():
                    # Convert ConfigurationValue to basic types
                    config_dict[key] = str(value) if value is not None else ""

            return flx_pb2.PluginConfig(
                name=request.name,
                type=request.type,
                config=dict_to_struct(config_dict),
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to get plugin config", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get plugin config: {e}",
            )
        # This return is needed for mypy, though unreachable due to _context.abort
        return flx_pb2.PluginConfig(
            name="",
            type=request.type,
            config=dict_to_struct({}),
        )

    async def UpdatePluginConfig(
        self, request: flx_pb2.UpdatePluginConfigRequest, _context: ServicerContext
    ) -> flx_pb2.PluginConfig:
        """Update configuration settings for a Meltano plugin."""
        try:
            # Convert config data
            config_data = struct_to_dict(request.config)

            # Update with Meltano - set each config key individually
            success = True
            for key, value in config_data.items():
                # Convert value to supported types for Meltano engine
                config_value = (
                    value
                    if isinstance(value, str | int | float | bool | type(None))
                    else str(value)
                )

                success = success and await self.meltano_engine.set_config(
                    plugin_name=str(request.name),
                    config_key=key,
                    config_value=config_value,
                )

            if not success:
                _context.abort(
                    grpc.StatusCode.INTERNAL,
                    "Failed to update plugin config",
                )

            # Publish domain event
            await self.event_bus.publish(
                "plugin.config.updated",
                {
                    "plugin_name": str(request.name),
                    "plugin_type": str(request.type),
                    "config_keys": list(config_data.keys()),
                },
            )

            return flx_pb2.PluginConfig(
                name=request.name,
                type=request.type,
                config=request.config,
            )

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC server failures
            self.logger.exception("Failed to update plugin config", error=str(e))
            _context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to update plugin config: {e}",
            )
        # This return is needed for mypy, though unreachable due to _context.abort
        return flx_pb2.PluginConfig(
            name="",
            type=request.type,
            config=dict_to_struct({}),
        )

    def _get_user_from_context(self, context: ServicerContext) -> str:
        """Extract user identity from gRPC context metadata."""
        try:
            # Extract user from gRPC metadata
            metadata = dict(context.invocation_metadata())

            # Check for JWT token in authorization header
            auth_header = metadata.get("authorization", "")
            # Handle both bytes and string authorization headers
            if isinstance(auth_header, bytes):
                auth_header = auth_header.decode("utf-8")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix

                # Basic JWT validation (in production, use proper validation)
                try:
                    payload = jwt.decode(
                        token,
                        self.settings.secrets.jwt_secret_key,
                        algorithms=[self.settings.secrets.jwt_algorithm],
                    )
                    return str(payload.get("sub", "unknown"))
                except (
                    ValueError,
                    TypeError,
                    RuntimeError,
                    ImportError,
                    KeyError,
                    AttributeError,
                ):
                    pass

            # Check for direct user ID in metadata
            return str(metadata.get("user-id", "system"))

        except (
            ValueError,
            TypeError,
            RuntimeError,
            ImportError,
            KeyError,
            AttributeError,
        ):
            return "system"

    def _map_plugin_type_to_protobuf(self, plugin_type: str) -> int:
        """Map plugin type string to protobuf enum value."""
        type_mapping = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        return type_mapping.get(plugin_type.lower(), flx_pb2.PLUGIN_TYPE_UNSPECIFIED)

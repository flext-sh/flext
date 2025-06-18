"""
gRPC server implementation for FLX platform.

Implements the FLX service defined in the protocol buffer definitions,
providing the main API for interacting with the platform.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import grpc
import structlog
from google.protobuf import empty_pb2, struct_pb2, timestamp_pb2

from flx.engine.meltano_wrapper import MeltanoEngine
from flx.events.event_bus import Event, EventBus
from flx.grpc.proto import flx_pb2, flx_pb2_grpc
from flx.monitoring.health import HealthChecker
from flx.monitoring.health import HealthStatus as HealthStatusEnum
from flx.monitoring.metrics import MetricsCollector

logger = structlog.get_logger()


def datetime_to_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    """Convert datetime to protobuf timestamp."""
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp


def dict_to_struct(data: dict[str, Any]) -> struct_pb2.Struct:
    """Convert dictionary to protobuf struct."""
    struct = struct_pb2.Struct()
    struct.update(data)
    return struct


class FlxGrpcServer(flx_pb2_grpc.FlxServiceServicer):
    """gRPC server implementation for FLX service."""

    def __init__(
        self,
        daemon: Any,
        event_bus: EventBus,
        meltano_engine: MeltanoEngine,
        health_checker: HealthChecker,
    ) -> None:
        """Initialize gRPC server."""
        self.daemon = daemon
        self.event_bus = event_bus
        self.meltano_engine = meltano_engine
        self.health_checker = health_checker
        self.metrics = MetricsCollector()
        self.logger = logger.bind(component="grpc_server")

        # In-memory storage for demo (should use database in production)
        self._pipelines: dict[str, dict[str, Any]] = {}
        self._executions: dict[str, dict[str, Any]] = {}
        self._schedules: dict[str, dict[str, Any]] = {}

    async def GetSystemStats(
        self,
        request: empty_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> flx_pb2.SystemStats:
        """Get system statistics."""
        self.logger.debug("Getting system stats")

        # Calculate stats
        active_pipelines = len(
            [p for p in self._pipelines.values() if p.get("is_active", True)]
        )
        total_executions = len(self._executions)
        success_count = len(
            [e for e in self._executions.values() if e.get("status") == "success"]
        )
        success_rate = (
            (success_count / total_executions * 100) if total_executions > 0 else 0.0
        )

        # Get system metrics
        import psutil

        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        return flx_pb2.SystemStats(
            active_pipelines=active_pipelines,
            total_executions=total_executions,
            success_rate=success_rate,
            uptime_seconds=int(
                asyncio.get_event_loop().time() - self.daemon._start_time
            ),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            active_connections=10,  # TODO: Get real connection count
        )

    async def HealthCheck(
        self,
        request: empty_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> flx_pb2.HealthStatus:
        """Perform health check."""
        self.logger.debug("Performing health check")

        # Run health checks
        checks = await self.health_checker.check_all()
        overall_status = await self.health_checker.get_overall_status()

        # Convert to protobuf
        components = {}
        for name, check in checks.items():
            components[name] = flx_pb2.ComponentHealth(
                name=check.name,
                healthy=check.status == HealthStatusEnum.HEALTHY,
                message=check.message,
                metadata=check.metadata,
            )

        return flx_pb2.HealthStatus(
            healthy=overall_status == HealthStatusEnum.HEALTHY,
            components=components,
            timestamp=datetime_to_timestamp(datetime.now(timezone.utc)),
        )

    async def GetSystemInfo(
        self,
        request: empty_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> flx_pb2.SystemInfo:
        """Get system information."""
        import sys

        import meltano

        return flx_pb2.SystemInfo(
            version="2.0.0",
            environment=self.daemon.settings.environment,
            python_version=sys.version,
            meltano_version=meltano.__version__,
            features={
                "multi_tenancy": str(self.daemon.settings.multi_tenancy_enabled),
                "circuit_breaker": str(self.daemon.settings.circuit_breaker_enabled),
                "rate_limiting": str(self.daemon.settings.rate_limiting_enabled),
                "tracing": str(self.daemon.settings.tracing_enabled),
            },
        )

    async def ListPipelines(
        self,
        request: flx_pb2.ListPipelinesRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.ListPipelinesResponse:
        """List pipelines."""
        self.logger.debug(
            "Listing pipelines", limit=request.limit, offset=request.offset
        )

        # Filter and sort pipelines
        pipelines = list(self._pipelines.values())

        # Apply filter if provided
        if request.filter:
            pipelines = [
                p for p in pipelines if request.filter.lower() in p["name"].lower()
            ]

        # Sort
        if request.sort_by:
            reverse = request.descending
            pipelines.sort(key=lambda p: p.get(request.sort_by, ""), reverse=reverse)

        # Paginate
        total = len(pipelines)
        start = request.offset
        end = start + request.limit if request.limit > 0 else None
        pipelines = pipelines[start:end]

        # Convert to protobuf
        pb_pipelines = []
        for p in pipelines:
            pb_pipeline = flx_pb2.Pipeline(
                id=p["id"],
                name=p["name"],
                description=p.get("description", ""),
                extractor=p["extractor"],
                loader=p["loader"],
                transform=p.get("transform", ""),
                schedule=p.get("schedule", ""),
                is_active=p.get("is_active", True),
                created_by=p.get("created_by", "system"),
                created_at=datetime_to_timestamp(p["created_at"]),
                updated_at=datetime_to_timestamp(p["updated_at"]),
            )

            if "config" in p:
                pb_pipeline.config.CopyFrom(dict_to_struct(p["config"]))

            pb_pipelines.append(pb_pipeline)

        return flx_pb2.ListPipelinesResponse(
            pipelines=pb_pipelines,
            total=total,
            limit=request.limit,
            offset=request.offset,
        )

    async def GetPipeline(
        self,
        request: flx_pb2.GetPipelineRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Pipeline:
        """Get a specific pipeline."""
        self.logger.debug("Getting pipeline", id=request.id)

        if request.id not in self._pipelines:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Pipeline {request.id} not found")

        p = self._pipelines[request.id]

        pb_pipeline = flx_pb2.Pipeline(
            id=p["id"],
            name=p["name"],
            description=p.get("description", ""),
            extractor=p["extractor"],
            loader=p["loader"],
            transform=p.get("transform", ""),
            schedule=p.get("schedule", ""),
            is_active=p.get("is_active", True),
            created_by=p.get("created_by", "system"),
            created_at=datetime_to_timestamp(p["created_at"]),
            updated_at=datetime_to_timestamp(p["updated_at"]),
        )

        if "config" in p:
            pb_pipeline.config.CopyFrom(dict_to_struct(p["config"]))

        return pb_pipeline

    async def CreatePipeline(
        self,
        request: flx_pb2.CreatePipelineRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Pipeline:
        """Create a new pipeline."""
        self.logger.info("Creating pipeline", name=request.name)

        # Generate ID
        pipeline_id = str(uuid.uuid4())

        # Create pipeline
        now = datetime.now(timezone.utc)
        pipeline = {
            "id": pipeline_id,
            "name": request.name,
            "description": request.description,
            "extractor": request.extractor,
            "loader": request.loader,
            "transform": request.transform,
            "config": (
                struct_pb2.Struct.to_dict(request.config)
                if request.HasField("config")
                else {}
            ),
            "schedule": request.schedule,
            "is_active": True,
            "created_by": "system",  # TODO: Get from auth context
            "created_at": now,
            "updated_at": now,
        }

        # Store pipeline
        self._pipelines[pipeline_id] = pipeline

        # Publish event
        await self.event_bus.publish(
            Event.create(
                "pipeline.created",
                {
                    "pipeline_id": pipeline_id,
                    "name": request.name,
                },
            )
        )

        # Convert to protobuf
        return await self.GetPipeline(
            flx_pb2.GetPipelineRequest(id=pipeline_id),
            context,
        )

    async def UpdatePipeline(
        self,
        request: flx_pb2.UpdatePipelineRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Pipeline:
        """Update an existing pipeline."""
        self.logger.info("Updating pipeline", id=request.id)

        if request.id not in self._pipelines:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Pipeline {request.id} not found")

        # Update pipeline
        pipeline = self._pipelines[request.id]

        if request.name:
            pipeline["name"] = request.name
        if request.description:
            pipeline["description"] = request.description
        if request.extractor:
            pipeline["extractor"] = request.extractor
        if request.loader:
            pipeline["loader"] = request.loader
        if request.transform:
            pipeline["transform"] = request.transform
        if request.schedule:
            pipeline["schedule"] = request.schedule
        if request.HasField("config"):
            pipeline["config"] = struct_pb2.Struct.to_dict(request.config)
        if request.HasField("is_active"):
            pipeline["is_active"] = request.is_active

        pipeline["updated_at"] = datetime.now(timezone.utc)

        # Publish event
        await self.event_bus.publish(
            Event.create(
                "pipeline.updated",
                {
                    "pipeline_id": request.id,
                    "changes": {
                        k: v for k, v in request.ListFields() if k.name != "id"
                    },
                },
            )
        )

        # Return updated pipeline
        return await self.GetPipeline(
            flx_pb2.GetPipelineRequest(id=request.id),
            context,
        )

    async def DeletePipeline(
        self,
        request: flx_pb2.DeletePipelineRequest,
        context: grpc.ServicerContext,
    ) -> empty_pb2.Empty:
        """Delete a pipeline."""
        self.logger.info("Deleting pipeline", id=request.id)

        if request.id not in self._pipelines:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Pipeline {request.id} not found")

        # Delete pipeline
        pipeline = self._pipelines.pop(request.id)

        # Publish event
        await self.event_bus.publish(
            Event.create(
                "pipeline.deleted",
                {
                    "pipeline_id": request.id,
                    "name": pipeline["name"],
                },
            )
        )

        return empty_pb2.Empty()

    @MetricsCollector().track_grpc_request("RunPipeline")
    async def RunPipeline(
        self,
        request: flx_pb2.RunPipelineRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Execution:
        """Run a pipeline."""
        self.logger.info("Running pipeline", pipeline_id=request.pipeline_id)

        if request.pipeline_id not in self._pipelines:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Pipeline {request.pipeline_id} not found"
            )

        pipeline = self._pipelines[request.pipeline_id]

        # Create execution record
        execution_id = str(uuid.uuid4())
        execution = {
            "id": execution_id,
            "pipeline_id": request.pipeline_id,
            "status": "running",
            "started_at": datetime.now(timezone.utc),
            "triggered_by": "manual",  # TODO: Get from auth context
            "env_vars": dict(request.env_vars),
            "full_refresh": request.full_refresh,
        }

        self._executions[execution_id] = execution

        # Run pipeline asynchronously
        asyncio.create_task(
            self._run_pipeline_async(
                execution_id,
                pipeline,
                request.full_refresh,
                dict(request.env_vars),
            )
        )

        # Return execution
        return flx_pb2.Execution(
            id=execution_id,
            pipeline_id=request.pipeline_id,
            status=flx_pb2.STATUS_RUNNING,
            started_at=datetime_to_timestamp(execution["started_at"]),
            triggered_by=execution["triggered_by"],
        )

    async def _run_pipeline_async(
        self,
        execution_id: str,
        pipeline: dict[str, Any],
        full_refresh: bool,
        env_vars: dict[str, str],
    ) -> None:
        """Run pipeline asynchronously."""
        execution = self._executions[execution_id]

        try:
            # Run with Meltano
            result = await self.meltano_engine.run_pipeline(
                extractor=pipeline["extractor"],
                loader=pipeline["loader"],
                transform=pipeline.get("transform"),
                state_id=f"pipeline_{pipeline['id']}",
                full_refresh=full_refresh,
                env=env_vars,
                event_bus=self.event_bus,
            )

            # Update execution
            execution["status"] = "success" if result["success"] else "failed"
            execution["error_message"] = (
                result.get("stderr", "") if not result["success"] else ""
            )
            execution["finished_at"] = datetime.now(timezone.utc)
            execution["duration_seconds"] = int(
                (execution["finished_at"] - execution["started_at"]).total_seconds()
            )

            # Publish event
            await self.event_bus.publish(
                Event.create(
                    "pipeline.execution.completed",
                    {
                        "execution_id": execution_id,
                        "pipeline_id": pipeline["id"],
                        "status": execution["status"],
                        "duration_seconds": execution["duration_seconds"],
                    },
                )
            )

        except Exception as e:
            self.logger.error("Pipeline execution failed", error=str(e))

            execution["status"] = "failed"
            execution["error_message"] = str(e)
            execution["finished_at"] = datetime.now(timezone.utc)
            execution["duration_seconds"] = int(
                (execution["finished_at"] - execution["started_at"]).total_seconds()
            )

    async def GetExecution(
        self,
        request: flx_pb2.GetExecutionRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Execution:
        """Get execution details."""
        if request.id not in self._executions:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Execution {request.id} not found"
            )

        e = self._executions[request.id]

        # Map status
        status_map = {
            "pending": flx_pb2.STATUS_PENDING,
            "running": flx_pb2.STATUS_RUNNING,
            "success": flx_pb2.STATUS_SUCCESS,
            "failed": flx_pb2.STATUS_FAILED,
            "cancelled": flx_pb2.STATUS_CANCELLED,
        }

        execution = flx_pb2.Execution(
            id=e["id"],
            pipeline_id=e["pipeline_id"],
            status=status_map.get(e["status"], flx_pb2.STATUS_UNSPECIFIED),
            started_at=datetime_to_timestamp(e["started_at"]),
            triggered_by=e.get("triggered_by", ""),
            metadata=e.get("metadata", {}),
        )

        if "finished_at" in e:
            execution.finished_at.CopyFrom(datetime_to_timestamp(e["finished_at"]))

        if "duration_seconds" in e:
            execution.duration_seconds = e["duration_seconds"]

        if "error_message" in e:
            execution.error_message = e["error_message"]

        if "records_processed" in e:
            execution.records_processed = e["records_processed"]

        return execution

    async def ListExecutions(
        self,
        request: flx_pb2.ListExecutionsRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.ListExecutionsResponse:
        """List executions."""
        # Filter executions
        executions = list(self._executions.values())

        if request.pipeline_id:
            executions = [
                e for e in executions if e["pipeline_id"] == request.pipeline_id
            ]

        # TODO: Add more filtering options

        # Sort by started_at descending
        executions.sort(key=lambda e: e["started_at"], reverse=True)

        # Paginate
        total = len(executions)
        start = request.offset
        end = start + request.limit if request.limit > 0 else None
        executions = executions[start:end]

        # Convert to protobuf
        pb_executions = []
        for e in executions:
            pb_executions.append(
                await self.GetExecution(
                    flx_pb2.GetExecutionRequest(id=e["id"]),
                    context,
                )
            )

        return flx_pb2.ListExecutionsResponse(
            executions=pb_executions,
            total=total,
            limit=request.limit,
            offset=request.offset,
        )

    async def CancelExecution(
        self,
        request: flx_pb2.CancelExecutionRequest,
        context: grpc.ServicerContext,
    ) -> empty_pb2.Empty:
        """Cancel a running execution."""
        if request.id not in self._executions:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Execution {request.id} not found"
            )

        execution = self._executions[request.id]

        if execution["status"] != "running":
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                f"Execution {request.id} is not running",
            )

        # TODO: Actually cancel the execution
        execution["status"] = "cancelled"
        execution["finished_at"] = datetime.now(timezone.utc)

        return empty_pb2.Empty()

    async def StreamExecution(
        self,
        request: flx_pb2.StreamExecutionRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.ExecutionUpdate:
        """Stream execution updates."""
        if request.execution_id not in self._executions:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Execution {request.execution_id} not found"
            )

        # Subscribe to execution events
        execution_complete = asyncio.Event()
        updates_queue = asyncio.Queue()

        async def handle_event(event: Event) -> None:
            """Handle execution events."""
            if event.data.get("execution_id") == request.execution_id:
                update = flx_pb2.ExecutionUpdate(
                    execution_id=request.execution_id,
                    type=event.type,
                    message=json.dumps(event.data),
                    timestamp=datetime_to_timestamp(event.timestamp),
                )

                await updates_queue.put(update)

                if event.type == "pipeline.execution.completed":
                    execution_complete.set()

        # Subscribe to events
        self.event_bus.subscribe("pipeline.output", handle_event)
        self.event_bus.subscribe("pipeline.execution.completed", handle_event)

        try:
            # Stream updates
            while not execution_complete.is_set():
                try:
                    update = await asyncio.wait_for(updates_queue.get(), timeout=1.0)
                    yield update
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield flx_pb2.ExecutionUpdate(
                        execution_id=request.execution_id,
                        type="heartbeat",
                        message="",
                        timestamp=datetime_to_timestamp(datetime.now(timezone.utc)),
                    )
        finally:
            # Unsubscribe
            self.event_bus.unsubscribe("pipeline.output", handle_event)
            self.event_bus.unsubscribe("pipeline.execution.completed", handle_event)

    async def ListPlugins(
        self,
        request: flx_pb2.ListPluginsRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.ListPluginsResponse:
        """List available plugins."""
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

        # Get plugins from Meltano
        plugins = await self.meltano_engine.list_plugins(
            plugin_type=plugin_type,
            installed_only=request.installed_only,
        )

        # Convert to protobuf
        pb_plugins = []
        for p in plugins:
            pb_plugin = flx_pb2.Plugin(
                name=p["name"],
                type=flx_pb2.PLUGIN_TYPE_UNSPECIFIED,  # TODO: Map type
                variant=p.get("variant", ""),
                version=p.get("version", ""),
                description=p.get("description", ""),
                installed=p.get("installed", False),
            )

            if "settings" in p:
                pb_plugin.settings.CopyFrom(dict_to_struct(p["settings"]))

            pb_plugins.append(pb_plugin)

        return flx_pb2.ListPluginsResponse(
            plugins=pb_plugins,
            total=len(pb_plugins),
        )

    async def InstallPlugin(
        self,
        request: flx_pb2.InstallPluginRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.Plugin:
        """Install a plugin."""
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
            plugin_name=request.name,
            variant=request.variant or None,
        )

        if not success:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to install plugin")

        # Return plugin info
        return flx_pb2.Plugin(
            name=request.name,
            type=request.type,
            variant=request.variant,
            installed=True,
        )

    async def UninstallPlugin(
        self,
        request: flx_pb2.UninstallPluginRequest,
        context: grpc.ServicerContext,
    ) -> empty_pb2.Empty:
        """Uninstall a plugin."""
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
            plugin_name=request.name,
        )

        if not success:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to uninstall plugin")

        return empty_pb2.Empty()

    async def GetState(
        self,
        request: flx_pb2.GetStateRequest,
        context: grpc.ServicerContext,
    ) -> flx_pb2.State:
        """Get pipeline state."""
        state_data = await self.meltano_engine.get_state(request.id)

        return flx_pb2.State(
            id=request.id,
            data=dict_to_struct(state_data),
            updated_at=datetime_to_timestamp(datetime.now(timezone.utc)),
        )

    async def SetState(
        self,
        request: flx_pb2.SetStateRequest,
        context: grpc.ServicerContext,
    ) -> empty_pb2.Empty:
        """Set pipeline state."""
        state_data = struct_pb2.Struct.to_dict(request.data)

        success = await self.meltano_engine.set_state(request.id, state_data)

        if not success:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to set state")

        return empty_pb2.Empty()

    async def ClearState(
        self,
        request: flx_pb2.ClearStateRequest,
        context: grpc.ServicerContext,
    ) -> empty_pb2.Empty:
        """Clear pipeline state."""
        success = await self.meltano_engine.clear_state(request.id)

        if not success:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to clear state")

        return empty_pb2.Empty()

    # Additional methods for schedules, config, etc. would follow similar patterns
